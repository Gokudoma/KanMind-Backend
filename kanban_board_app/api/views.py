from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from kanban_board_app.models import Board, Comment, Task
from .permissions import (
    IsBoardMember, IsBoardOwner, IsCommentAuthor, IsTaskAuthorOrBoardOwner
)
from .serializers import (
    BoardCreateUpdateSerializer, BoardListSerializer,
    BoardSerializer, CommentSerializer, TaskSerializer, TaskUpdateSerializer
)


class BoardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing boards.
    Handles permission checks to ensure users only see authorized content.
    """
    def get_queryset(self):
        if self.action == 'list':
            return self.request.user.boards.all().prefetch_related(
                'members', 'tasks', 'owner'
            )
        return Board.objects.all().prefetch_related(
            'members', 'tasks', 'owner'
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return BoardListSerializer
        if self.action in ['create', 'partial_update']:
            return BoardCreateUpdateSerializer
        return BoardSerializer

    def get_permissions(self):
        if self.action in ['retrieve', 'partial_update']:
            return [IsAuthenticated(), IsBoardMember()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated()]


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks.
    Enforces board membership for creation and updates.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer

    def get_permissions(self):
        if self.action in ['retrieve', 'partial_update']:
            return [IsAuthenticated(), IsBoardMember()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsTaskAuthorOrBoardOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        board = serializer.validated_data['board']
        if not board.members.filter(id=self.request.user.id).exists():
            raise PermissionDenied("You must be a member of this board to create a task.")
        serializer.save()


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments on specific tasks.
    """
    serializer_class = CommentSerializer

    def get_queryset(self):
        task_pk = self.kwargs['task_pk']
        get_object_or_404(Task, pk=task_pk)
        return Comment.objects.filter(task_id=task_pk).order_by('created_at')

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsCommentAuthor()]
        return [IsAuthenticated(), IsBoardMember()]

    def perform_create(self, serializer):
        task = Task.objects.get(id=self.kwargs['task_pk'])
        if not task.board.members.filter(id=self.request.user.id).exists():
            raise PermissionDenied("Must be board member to comment.")
        serializer.save(author=self.request.user, task=task)


class AssignedTasksView(APIView):
    """
    API Endpoint to list tasks assigned to the current user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(assignee=request.user)
        return Response(TaskSerializer(tasks, many=True).data)


class ReviewingTasksView(APIView):
    """
    API Endpoint to list tasks where the current user is the reviewer.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(reviewer=request.user)
        return Response(TaskSerializer(tasks, many=True).data)