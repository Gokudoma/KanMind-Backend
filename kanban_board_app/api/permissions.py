from rest_framework.permissions import BasePermission

from kanban_board_app.models import Board, Comment, Task


class IsBoardOwner(BasePermission):
    """
    Allows access only to the owner of the board.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsBoardMember(BasePermission):
    """
    Allows access only to members of the board.
    Automatically resolves the board from Task or Comment objects.
    """
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Board):
            board = obj
        elif isinstance(obj, Task):
            board = obj.board
        elif isinstance(obj, Comment):
            board = obj.task.board
        else:
            return False
        
        return board.members.filter(id=request.user.id).exists()


class IsCommentAuthor(BasePermission):
    """
    Allows access only to the author of the comment.
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsTaskAuthorOrBoardOwner(BasePermission):
    """
    Allows access if the user is the task assignee OR the board owner.
    """
    def has_object_permission(self, request, view, obj):
        is_task_assignee = obj.assignee == request.user
        is_board_owner = obj.board.owner == request.user
        return is_task_assignee or is_board_owner