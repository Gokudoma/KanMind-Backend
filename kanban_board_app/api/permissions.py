from rest_framework.permissions import BasePermission

from kanban_board_app.models import Board, Comment, Task


class IsBoardOwner(BasePermission):
    """
    Permission check for Board ownership.
    
    Logic:
    - Returns True only if the object's 'owner' field matches request.user.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsBoardMember(BasePermission):
    """
    Permission check for Board membership.
    
    Logic:
    1. Determines the associated Board based on the object type:
       - If object is Board: use object itself.
       - If object is Task: use obj.board.
       - If object is Comment: use obj.task.board.
    2. Checks if request.user exists in board.members.
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
    Permission check for Comment authorship.
    
    Logic:
    - Returns True only if the comment's author matches request.user.
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsTaskAuthorOrBoardOwner(BasePermission):
    """
    Permission check for Task deletion.
    
    Logic:
    - Allows access if request.user is the Task assignee.
    - OR if request.user is the Owner of the parent Board.
    """
    def has_object_permission(self, request, view, obj):
        is_task_assignee = obj.assignee == request.user
        is_board_owner = obj.board.owner == request.user
        return is_task_assignee or is_board_owner