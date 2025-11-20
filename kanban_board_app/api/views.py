from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound

from kanban_board_app.models import Board, Task, Comment
from .permissions import IsBoardOwner, IsBoardMember, IsCommentAuthor, IsTaskAuthorOrBoardOwner
from .serializers import (
    BoardSerializer, BoardCreateUpdateSerializer, 
    TaskSerializer, CommentSerializer
)

class BoardViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        """
        List: Nur eigene Boards anzeigen.
        Detail: Alle Boards durchsuchen (Permission Klasse regelt dann Zugriff -> 403 statt 404).
        """
        if self.action == 'list':
            return self.request.user.boards.all().prefetch_related('members', 'tasks', 'owner')
        return Board.objects.all().prefetch_related('members', 'tasks', 'owner')

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return BoardCreateUpdateSerializer
        return BoardSerializer

    def get_permissions(self):
        # Feedback: Auch bei 'retrieve' (GET single) muss geprüft werden -> 403
        if self.action in ['retrieve', 'partial_update']: 
            return [IsAuthenticated(), IsBoardMember()]
        if self.action == 'destroy': 
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated()]

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        # Feedback: Auch hier prüfen, ob man Member ist
        if self.action in ['retrieve', 'partial_update']:
            return [IsAuthenticated(), IsBoardMember()]
        if self.action == 'destroy': 
            return [IsAuthenticated(), IsTaskAuthorOrBoardOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        board = serializer.validated_data['board']
        if not board.members.filter(id=self.request.user.id).exists():
            # Feedback: 403 statt 400 zurückgeben
            raise PermissionDenied("You must be a member of this board to create a task.")
        serializer.save()

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        # Feedback: Prüfen ob Task existiert -> Sonst 404
        task_pk = self.kwargs['task_pk']
        get_object_or_404(Task, pk=task_pk) 
        return Comment.objects.filter(task_id=task_pk).order_by('created_at')

    def get_permissions(self):
        if self.action == 'destroy': 
            return [IsAuthenticated(), IsCommentAuthor()]
        # Create/List braucht Board-Member Permission (explizite Prüfung in perform_create oder Permission Klasse)
        return [IsAuthenticated(), IsBoardMember()] 

    def perform_create(self, serializer):
        task = Task.objects.get(id=self.kwargs['task_pk'])
        # Sicherstellen, dass User Board-Member ist (für 403)
        if not task.board.members.filter(id=self.request.user.id).exists():
             raise PermissionDenied("Must be board member to comment.")
        serializer.save(author=self.request.user, task=task)

class AssignedTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Feedback: Soll leere Liste zurückgeben (200), kein 404.
        # Filter gibt standardmäßig leere Liste, wenn nichts gefunden -> Passt.
        tasks = Task.objects.filter(assignee=request.user)
        return Response(TaskSerializer(tasks, many=True).data)

class ReviewingTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(reviewer=request.user)
        return Response(TaskSerializer(tasks, many=True).data)