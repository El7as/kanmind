from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView 
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

from django.db.models import Q


from kanban_app.models import Board, Column, Task, Comment
from kanban_app.api.serializer import BoardCreateSerializer, BoardListSerializer, BoardDetailSerializer, BoardUpdateSerializer, TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer, CommentSerializer, CommentCreateSerializer, BoardMembersSerializer, TaskPatchSerializer
from kanban_app.api.permissions import IsBoardOwnerOrMember, CanDeleteTask, CanAccessTask



class BoardViewSet(viewsets.ModelViewSet):

    """
    ViewSet for managing Kanban boards.

    Supports:
        - list:    List all boards the user has access to.
        - create:  Create a new board.
        - retrieve: Get detailed board information.
        - update / partial_update: Modify board metadata.
        - destroy: Delete a board.

    Permissions:
        - Only authenticated users may access boards.
        - Only board owners or members may retrieve/update/delete.

    Serializers:
        - create: BoardCreateSerializer
        - list: BoardListSerializer
        - retrieve: BoardDetailSerializer
        - update/partial_update: BoardUpdateSerializer
    """

    queryset = Board.objects.all()


    def get_queryset(self):
        # Return all boards. Filtering is handled by permissions.
        return Board.objects.all()


    def get_permissions(self):
        # Assign permissions based on the action.
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsBoardOwnerOrMember()]
        if self.action == 'list':
            return [IsAuthenticated()]
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthenticated()]


    def get_serializer_class(self):
        # Return serializer depending on the action.
        if self.action == 'create':
            return BoardCreateSerializer
        if self.action == 'list':
            return BoardListSerializer
        if self.action == 'retrieve':
            return BoardDetailSerializer
        if self.action in ['update', 'partial_update']:
            return BoardUpdateSerializer
        return BoardDetailSerializer
    

    def perform_create(self, serializer):
        # Create a board and automatically generate default columns.  Default columns: to-do, in-progress, review, done
        board = serializer.save()

        default_columns = [('to-do', 0), ('in-progress', 1), ('review', 2), ('done', 4)]

        for title, pos in default_columns:
            Column.objects.create(board=board, title=title, position=pos)
        return board

    
    def create(self, request, *args, **kwargs):
        # Create a board and return list-style response.
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        return Response(BoardListSerializer(board).data, status=status.HTTP_201_CREATED)
    

    def partial_update(self, request, *args, **kwargs):
        # Return updated board with member information

        super().partial_update(request, *args, **kwargs)
        board = self.get_object()
        return Response(BoardMembersSerializer(board).data)
    

    def update(self, request, *args, **kwargs):
        # Return updated board with member information.

        super().update(request, *args, **kwargs)
        board = self.get_object()
        return Response(BoardMembersSerializer(board).data)



class TaskViewSet(ModelViewSet):

    """
    ViewSet for managing tasks.

    Supports:
        - list: List all tasks (not filtered by board).
        - create: Create a new task inside a board.
        - retrieve: Get a single task.
        - update / partial_update: Modify task fields.
        - destroy: Delete a task.

    Permissions:
        - CanAccessTask: Ensures user is board owner or member.
        - CanDeleteTask: Restricts deletion to creator or board owner.
    """

    queryset = Task.objects.all()
    

    def get_permissions(self):
        # Assign permissions based on action

        if self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'create']:
            return [IsAuthenticated(), CanAccessTask(), CanDeleteTask()]
        return [IsAuthenticated()]


    def partial_update(self, request, *args, **kwargs):
        # Update selected fields of a task. Behavior: If body is empty → enforce required fields (400). Otherwise perform normal partial update.
        
        task = self.get_object()
        self.check_object_permissions(request, task)

        if not request.data:
            serializer = TaskUpdateSerializer(task, data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
    

        serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        read_serializer = TaskPatchSerializer(task)
        return Response(read_serializer.data, status=200)
    

    def get_serializer_class(self):
        # Return serializer depending on action.

        if self.action == 'create':
            return TaskCreateSerializer
        if self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer
    

    def create(self, request, *args, **kwargs):
        # Create a new task. Validates: board exists, user has permission to create in that board

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        board_id = serializer.validated_data['board']
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            raise NotFound(detail='Board not found')


        task = serializer.save(board=board, created_by=request.user)
        read_serializer = TaskSerializer(task, context={'request': request})
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
    

    def get_object(self):
        # Validate task ID before retrieving.

        pk = self.kwargs.get('pk')

        if not str(pk).isdigit():
            raise ValidationError({'detail': 'Invalid Task-ID'})

        return super().get_object()
    

    def destroy(self, request, *args, **kwargs):
        # Validate task ID before deletion.

        pk = kwargs.get('pk')

        if not str(pk).isdigit():
            return Response({'detail': 'Invalid Task-ID'}, status=400)
        return super().destroy(request, *args, **kwargs)



class TaskAssignedToMeView(ListAPIView):

    """
    Returns all tasks assigned to the current user.

    Optimizations:
        - select_related: assignee, reviewer
        - prefetch_related: comments
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        user = self.request.user
        return (Task.objects.filter(assignee=user).select_related('assignee', 'reviewer').prefetch_related('comments'))
    


class TaskReviewerView(ListAPIView):

    """
    Returns all tasks where the current user is the reviewer.

    Optimizations:
        - select_related: assignee, reviewer
        - prefetch_related: comments
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        user = self.request.user
        return (Task.objects.filter(reviewer=user).select_related('assignee', 'reviewer').prefetch_related('comments'))
    


class TaskCommentView(APIView):

    """
    Handles listing, creating and deleting comments for a task.

    Permissions:
        - User must be board owner or board member.
        - Only comment authors may delete their comments.
    """

    permission_classes = [IsAuthenticated]


    def get_task(self, task_id):
        # Validate and return a task by ID.

        if not str(task_id).isdigit():
            raise ValidationError({'detail': 'Invalid Task-Id'})
        
        try:
            return Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound('Task not found')
        

    def check_board_permission(self, user, task):
        # Ensure user is owner or member of the task's board.

        board = task.board

        if user != board.owner and user not in board.members.all():
            raise PermissionDenied('You are not a member of this board.')
        

    def get(self, request, task_id):
        # Return all comments for a task.

        task = self.get_task(task_id)
        self.check_board_permission(request.user, task)

        comments = task.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    

    def post(self, request, task_id):
        # Create a new comment for a task.

        task = self.get_task(task_id)
        self.check_board_permission(request.user, task)

        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = Comment.objects.create(task=task, author=request.user, content=serializer.validated_data['content'])
        return Response(CommentSerializer(comment).data, status=201)
    

    def delete(self, request, task_id, comment_id):
        # Delete a comment if the user is the author.

        if not str(comment_id).isdigit():
            raise ValidationError({'detail': 'Invalid  Kommentar-id'})
        
        task = self.get_task(task_id)
        self.check_board_permission(request.user, task)

        try:
            comment = task.comments.get(id=comment_id)
        except Comment.DoesNotExist:
            raise NotFound('Comment not found')
        
        if comment.task_id != task.id:
            return Response({'detail': 'Comments are not part of this task'}, status=400)
        
        if comment.author != request.user:
            raise PermissionDenied('You must not delete this comment')
        
        comment.delete()
        return Response(status=204)

