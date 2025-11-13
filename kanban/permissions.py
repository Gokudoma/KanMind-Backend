from rest_framework.permissions import BasePermission
from .models import Task 

class IsBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsBoardMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        board = obj
        if isinstance(obj, Task):
            board = obj.board
        
        return board.members.filter(id=request.user.id).exists()

class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

class IsTaskAuthorOrBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        is_task_assignee = obj.assignee == request.user
        is_board_owner = obj.board.owner == request.user
        return is_task_assignee or is_board_owner