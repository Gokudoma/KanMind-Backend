from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, NotFound
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
        """
        Determines the queryset based on the action.
        
        Steps:
        1. Check if the action is 'list' (GET /boards/).
           - If yes: Filter boards to return only those where the user is a member.
        2. For all other actions (retrieve, update, destroy):
           - Return all boards initially.
           - Access control is handled later by the permission classes (IsBoardMember/IsBoardOwner).
           - This ensures that accessing a forbidden board returns 403 Forbidden instead of 404 Not Found.
        """
        if self.action == 'list':
            return self.request.user.boards.all().prefetch_related(
                'members', 'tasks', 'owner'
            )
        return Board.objects.all().prefetch_related(
            'members', 'tasks', 'owner'
        )

    def get_serializer_class(self):
        """
        Selects the appropriate serializer based on the action.
        
        Steps:
        1. If action is 'list': Use BoardListSerializer (summary view with counts).
        2. If action is 'create' or 'partial_update': Use BoardCreateUpdateSerializer (input validation).
        3. Default: Use BoardSerializer (detailed view with nested objects).
        """
        if self.action == 'list':
            return BoardListSerializer
        if self.action in ['create', 'partial_update']:
            return BoardCreateUpdateSerializer
        return BoardSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        
        Steps:
        1. If accessing a specific board (retrieve/update): User must be a board member.
        2. If deleting a board: User must be the board owner.
        3. Default: User must be authenticated.
        """
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
        """
        Selects serializer based on action.
        
        Steps:
        1. If updating (PATCH/PUT): Use TaskUpdateSerializer (excludes board/counts from response).
        2. Default: Use TaskSerializer (full details).
        """
        if self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer

    def get_permissions(self):
        """
        Define permissions for tasks.
        
        Steps:
        1. View/Edit: Must be a board member.
        2. Delete: Must be task author OR board owner.
        3. Default: Authenticated.
        """
        if self.action in ['retrieve', 'partial_update']:
            return [IsAuthenticated(), IsBoardMember()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsTaskAuthorOrBoardOwner()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """
        Custom create method to handle Board 404 explicitly.
        
        Steps:
        1. Extract 'board' ID from request data.
        2. Try to fetch the Board object.
        3. If Board does not exist, raise NotFound (404).
           (This prevents the Serializer from raising a 400 ValidationError).
        4. Proceed with standard creation.
        """
        board_id = request.data.get('board')
        if board_id:
            if not Board.objects.filter(pk=board_id).exists():
                raise NotFound(f"Board with id {board_id} not found.")
        
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Save the new task with additional permission checks.
        
        Steps:
        1. Extract the board instance from validated data.
        2. Check if the requesting user is a member of this board.
        3. If not a member: Raise PermissionDenied (403).
        4. If member: Save the task.
        """
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
        """
        Filter comments by task and enforce board membership.
        
        Steps:
        1. Retrieve 'task_pk' from the URL.
        2. Fetch the Task object or raise 404 if not found.
        3. Check permissions: Is the user a member of the task's board?
           - No: Raise PermissionDenied (403).
           - Yes: Continue.
        4. Return comments belonging to this task, sorted by creation date.
        """
        task_pk = self.kwargs['task_pk']
        task = get_object_or_404(Task, pk=task_pk)
        
        if not task.board.members.filter(id=self.request.user.id).exists():
            raise PermissionDenied("Must be board member to view comments.")

        return Comment.objects.filter(task_id=task_pk).order_by('created_at')

    def get_permissions(self):
        """
        Define permissions for comments.
        
        Steps:
        1. Delete: Only the comment author can delete.
        2. Default: Must be authenticated and a board member.
        """
        if self.action == 'destroy':
            return [IsAuthenticated(), IsCommentAuthor()]
        return [IsAuthenticated(), IsBoardMember()]

    def perform_create(self, serializer):
        """
        Create a comment associated with a task.
        
        Steps:
        1. Fetch the task using 'task_pk' (Use get_object_or_404 to avoid 500 error).
        2. Check if the user is a member of the board.
        3. If not member: Raise PermissionDenied (403).
        4. Save comment with the current user as author and associated task.
        """
        # Fix for 500 error on POST request (Issue from feedback)
        task = get_object_or_404(Task, id=self.kwargs['task_pk'])
        
        if not task.board.members.filter(id=self.request.user.id).exists():
            raise PermissionDenied("Must be board member to comment.")
        serializer.save(author=self.request.user, task=task)


class AssignedTasksView(APIView):
    """
    API Endpoint to list tasks assigned to the current user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET request for assigned tasks.
        
        Steps:
        1. Filter tasks where 'assignee' matches the current user.
        2. Serialize the queryset using TaskSerializer.
        3. Return serialized data (List of tasks).
        """
        tasks = Task.objects.filter(assignee=request.user)
        return Response(TaskSerializer(tasks, many=True).data)


class ReviewingTasksView(APIView):
    """
    API Endpoint to list tasks where the current user is the reviewer.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET request for reviewing tasks.
        
        Steps:
        1. Filter tasks where 'reviewer' matches the current user.
        2. Serialize the queryset using TaskSerializer.
        3. Return serialized data (List of tasks).
        """
        tasks = Task.objects.filter(reviewer=request.user)
        return Response(TaskSerializer(tasks, many=True).data)