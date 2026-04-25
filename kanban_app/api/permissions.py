from rest_framework.permissions import BasePermission, SAFE_METHODS

from django.contrib.auth import get_user_model


from kanban_app.models import Board, Column



User = get_user_model()

class IsBoardOwner(BasePermission):

    """
    Permission: Allows access only to the owner of a board.

    Rules:
        - has_permission: Always returns True (object-level check is required).
        - has_object_permission: Grants access if the requesting user is
          the board owner or a board member.

    Notes:
        - This permission is typically used for BoardViewSet.
    """

    def has_permission(self, request, view):
        return True
    

    def has_object_permission(self, request, view, obj):
        if obj is None:
            return False
        return (obj.owner == request.user or request.user in obj.member.all())    



class IsBoardOwnerOrMember(BasePermission):

    """
    Permission: Grants access to board owners and board members.

    Rules:
        - has_permission: No global restriction (object-level check required).
        - has_object_permission: User must be owner or member of the board.

    Notes:
        - Useful for read/write operations on boards.
    """


    def has_permission(self, request, view):
        return True


    def has_object_permission(self, request, view, obj):
        user = request.user

        if obj.owner == user:
            return True
        
        if user in obj.members.all():
            return True
        
        return False



class CanAccessTask(BasePermission):

    """
    Permission: Ensures that only board owners or board members can
    create, view, update, or delete tasks.

    Rules:
        - CREATE:
            - Requires a valid board ID in request.data.
            - User must be owner or member of that board.
        - Other actions:
            - Object-level permission checks if the user belongs to the
              board the task is associated with.

    Notes:
        - This is the main permission used for TaskViewSet.
    """

    def has_permission(self, request, view):

        if view.action == 'create':
            board_id = request.data.get('board')
            if not board_id:
                return False
            
            try:
                board = Board.objects.get(id=board_id)
            except Board.DoesNotExist:
                return False
            
            user = request.user
            return (board.owner == user or board.members.filter(id=user.id).exists())
        return True
    
    def has_object_permission(self, request, view, obj):
        board = obj.board
        user = request.user

        if board.owner == user:
            return True
        
        if user in board.members.all():
            return True
        return False
    
        

class IsColumnInUserBoard(BasePermission):
     
    """
    Permission: Ensures that a column belongs to a board owned by the user.

    Rules:
        - POST:
            - Requires a board ID in request.data.
            - User must be the owner of that board.
        - Other methods:
            - Allowed globally, object-level check applies.

        - Object-level:
            - Column's board must be owned by the requesting user.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            board_id = request.data.get('board')
            if not board_id:
                return False
            return Board.objects.filter(id=board_id, owner=request.user).exists()
        return True
    

    def has_object_permission(self, request, view, obj):
        return obj.board.owner == request.user



class IsTaskInUserBoard(BasePermission):

    """
    Permission: Ensures that a task belongs to a board owned by the user.

    Rules:
        - POST:
            - Requires a column ID in request.data.
            - Column must belong to a board owned by the user.
        - Non-detail views:
            - Always allowed.
        - Object-level:
            - If the object has a column, its board must be owned by the user.
    """

    def has_permission(self, request, view):
        if not view.detail:
            return True
        
        if request.method == 'POST':
            column_id = request.data.get('column')
            if not column_id:
                return False
            return Column.objects.filter(id=column_id, board__owner=request.user).exists()
        return True
    

    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, 'column'):
            return True
        return obj.column.board.owner == request.user



class CanDeleteTask(BasePermission):
    
    """
    Permission: Allows deletion of a task only if the user is either:

        - the creator of the task, OR
        - the owner of the board the task belongs to.

    Rules:
        - Non-DELETE requests always pass.
        - DELETE requests require creator or board owner.
    """

    def has_object_permission(self, request, view, obj):
        if request.method != 'DELETE':
            return True
        
        user = request.user        
        return (obj.created_by == user or obj.board.owner == user)
    


