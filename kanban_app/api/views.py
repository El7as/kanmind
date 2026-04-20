from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView 
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied


from kanban_app.models import Board, Column, Task, Comment
from kanban_app.api.serializer import BoardCreateSerializer, BoardListSerializer, BoardDetailSerializer, BoardUpdateSerializer, TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer, CommentSerializer, CommentCreateSerializer, BoardMembersSerializer, TaskPatchSerializer
from kanban_app.api.permissions import IsBoardOwnerOrMember, CanDeleteTask 



class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()


    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsBoardOwnerOrMember()]
        if self.action == 'list':
            return [IsAuthenticated()]
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthenticated()]


    def get_serializer_class(self):
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
        board = serializer.save()

        default_columns = [('to-do', 0), ('in-progress', 1), ('review', 2), ('done', 4)]

        for title, pos in default_columns:
            Column.objects.create(board=board, title=title, position=pos)
        return board

    
    def create(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        return Response(BoardListSerializer(board).data, status=status.HTTP_201_CREATED)
    

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        board = self.get_object()
        return Response(BoardMembersSerializer(board).data)
    

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        board = self.get_object()
        return Response(BoardMembersSerializer(board).data)



class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated, CanDeleteTask] 


    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()

        serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        read_serializer = TaskPatchSerializer(task)
        return Response(read_serializer.data, status=200)

    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        if self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer
    

    def create(self, request, *args, **kwargs):
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
        pk = self.kwargs.get('pk')

        if not str(pk).isdigit():
            raise ValidationError({'detail': 'Unglültige Task-ID'})

        return super().get_object()
    

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        if not str(pk).isdigit():
            return Response({'detail': 'Unglültige Task-ID'}, status=400)
        return super().destroy(request, *args, **kwargs)



class TaskAssignedToMeView(ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        user = self.request.user
        return (Task.objects.filter(assignee=user).select_related('assignee', 'reviewer').prefetch_related('comments'))
    


class TaskReviewerView(ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        user = self.request.user
        return (Task.objects.filter(reviewer=user).select_related('assignee', 'reviewer').prefetch_related('comments'))
    


class TaskCommentView(APIView):
    permission_classes = [IsAuthenticated]


    def get_task(self, task_id):
        if not str(task_id).isdigit():
            raise ValidationError({'detail': 'Ungütlige Task-Id'})
        
        try:
            return Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound('Task nicht gefunden')
        

    def check_board_permission(self, user, task):
        board = task.board

        if user != board.owner and user not in board.members.all():
            raise PermissionDenied('Du bist kein Mitglied dieses Boards')
        

    def get(self, request, task_id):
        task = self.get_task(task_id)
        self.check_board_permission(request.user, task)

        comments = task.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    

    def post(self, request, task_id):
        task = self.get_task(task_id)
        self.check_board_permission(request.user, task)

        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = Comment.objects.create(task=task, author=request.user, content=serializer.validated_data['content'])
        return Response(CommentSerializer(comment).data, status=201)
    

    def delete(self, request, task_id, comment_id):

        if not str(comment_id).isdigit():
            raise ValidationError({'detail': 'Ungültige Kommentar-id'})
        
        task = self.get_task(task_id)
        self.check_board_permission(request.user, task)

        try:
            comment = task.comments.get(id=comment_id)
        except Comment.DoesNotExist:
            raise NotFound('Kommentar nicht gefunden')
        
        if comment.task_id != task.id:
            return Response({'detail': 'Kommentar gehört nicht zu dieser Task'}, status=400)
        
        if comment.author != request.user:
            raise PermissionDenied('Du darfst diesen Kommentar nicht löschen')
        
        comment.delete()
        return Response(status=204)

