from rest_framework.permissions import BasePermission, SAFE_METHODS

from django.contrib.auth import get_user_model


from kanban_app.models import Board, Column, Task



User = get_user_model()

class IsBoardOwner(BasePermission):

    def has_permission(self, request, view):
        return True
    

    def has_object_permission(self, request, view, obj):
        if obj is None:
            return False
        return (obj.owner == request.user or request.user in obj.member.all())    



class IsBoardOwnerOrMember(BasePermission):


    def has_permission(self, request, view):
        if view.action != 'create':
            return True
        
        board_id = request.data.get('board')
        if not board_id:
            return False
        
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return False
        
        user = request.user
        return (board.owner == user or board.members.filter(id=user.id).exists())
    
     

class IsColumnInUserBoard(BasePermission):
     
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
    
    def has_object_permission(self, request, view, obj):
        if request.method != 'DELETE':
            return True
        
        user = request.user        
        return (obj.created_by == user or obj.board.owner == user)
    


