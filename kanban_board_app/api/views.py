from rest_framework import viewsets, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_nested.viewsets import NestedViewSetMixin

from kanban_board_app.models import Board, Task, Comment
from .permissions import IsBoardOwner, IsBoardMember, IsCommentAuthor, IsTaskAuthorOrBoardOwner
from .serializers import (
    BoardSerializer, BoardCreateUpdateSerializer, 
    TaskSerializer, CommentSerializer
)

class BoardViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return self.request.user.boards.all().prefetch_related('members', 'tasks', 'owner')

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return BoardCreateUpdateSerializer
        return BoardSerializer

    def get_permissions(self):
        if self.action == 'partial_update': return [IsAuthenticated(), IsBoardMember()]
        if self.action == 'destroy': return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated()]

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        if self.action == 'partial_update': return [IsAuthenticated(), IsBoardMember()]
        if self.action == 'destroy': return [IsAuthenticated(), IsTaskAuthorOrBoardOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        board = serializer.validated_data['board']
        if not board.members.filter(id=self.request.user.id).exists():
            raise serializers.ValidationError(
                {"detail": "Must be member of board."}, code=status.HTTP_403_FORBIDDEN
            )
        serializer.save()

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs['task_pk']).order_by('created_at')

    def get_permissions(self):
        if self.action == 'destroy': return [IsAuthenticated(), IsCommentAuthor()]
        return [IsAuthenticated(), IsBoardMember()]

    def perform_create(self, serializer):
        task = Task.objects.get(id=self.kwargs['task_pk'])
        # Check permissions implicitly via IsBoardMember on view or manually check board membership
        serializer.save(author=self.request.user, task=task)

class AssignedTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(assignee=request.user)
        return Response(TaskSerializer(tasks, many=True).data)

class ReviewingTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(reviewer=request.user)
        return Response(TaskSerializer(tasks, many=True).data)