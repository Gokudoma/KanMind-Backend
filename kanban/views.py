from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Board, Task, Comment
from .serializers import (
    BoardSerializer, BoardCreateUpdateSerializer, 
    TaskSerializer, CommentSerializer
)
from .permissions import (
    IsBoardOwner, IsBoardMember, IsCommentAuthor, IsTaskAuthorOrBoardOwner
)

# -------------------------------------------------------------------
# 1. Board ViewSet (/api/boards/ & /api/boards/<id>/)
# -------------------------------------------------------------------
class BoardViewSet(viewsets.ModelViewSet):
    
    def get_queryset(self):
        user = self.request.user
        return user.boards.all().prefetch_related('members', 'tasks', 'owner')

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return BoardCreateUpdateSerializer
        return BoardSerializer

    def get_permissions(self):
        if self.action == 'partial_update': 
            self.permission_classes = [IsAuthenticated, IsBoardMember]
        elif self.action == 'destroy': 
            self.permission_classes = [IsAuthenticated, IsBoardOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_context(self):
        return {'request': self.request}

# -------------------------------------------------------------------
# 2. Task ViewSet (/api/tasks/<id>/)
# -------------------------------------------------------------------
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        if self.action == 'create': 
            self.permission_classes = [IsAuthenticated] 
        elif self.action == 'partial_update': 
            self.permission_classes = [IsAuthenticated, IsBoardMember]
        elif self.action == 'destroy': 
            self.permission_classes = [IsAuthenticated, IsTaskAuthorOrBoardOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        board_id = serializer.validated_data['board'].id
        board = Board.objects.get(id=board_id)
        
        if not board.members.filter(id=self.request.user.id).exists():
            raise serializers.ValidationError(
                {"detail": "You must be a member of this board to create a task."},
                code=status.HTTP_403_FORBIDDEN
            )
        serializer.save()

# -------------------------------------------------------------------
# 3. Comment ViewSet (/api/tasks/<task_id>/comments/)
# -------------------------------------------------------------------
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        task_id = self.kwargs.get('task_pk') 
        return Comment.objects.filter(task_id=task_id).order_by('created_at')

    def get_permissions(self):
        task_id = self.kwargs.get('task_pk')
        task = Task.objects.get(id=task_id)
        
        if self.action == 'destroy': 
            self.permission_classes = [IsAuthenticated, IsCommentAuthor]
        elif self.action == 'create' or self.action == 'list': 
            self.check_object_permissions(self.request, task)
            self.permission_classes = [IsAuthenticated, IsBoardMember] 
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_pk')
        task = Task.objects.get(id=task_id)
        serializer.save(author=self.request.user, task=task)

# -------------------------------------------------------------------
# 4. Spezielle Task-Listen (APIViews)
# -------------------------------------------------------------------
class AssignedTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(assignee=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReviewingTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(reviewer=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)