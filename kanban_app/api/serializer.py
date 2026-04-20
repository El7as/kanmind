from rest_framework import serializers

from django.contrib.auth import get_user_model


from kanban_app.models import Board, Task, Column, Comment



User = get_user_model()



class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()


    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']


    def get_fullname(slef, obj):
        if isinstance(obj, int):
            obj = User.objects.get(id=obj)

        full = f'{obj.first_name} {obj.last_name}'.strip()
        return full if full else obj.username



class TaskUpdateSerializer(serializers.ModelSerializer):
    assignee_id =serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='assignee', write_only=True, required=False)
    reviewer_id =serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='reviewer', write_only=True, required=False)


    class Meta:
        model = Task
        fields = [ 'title', 'description', 'status', 'priority', 'assignee_id', 'reviewer_id', 'due_date']



class TaskUserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()


    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    
    def get_fullname(self, obj):

        if not hasattr(obj, 'first_name') or not hasattr(obj, 'last_name'): return obj.email
        full = f'{obj.first_name} {obj.last_name}'.strip()
        return full if full else obj.email



class TaskCreateSerializer(serializers.ModelSerializer):
    board = serializers.IntegerField()
    assignee_id =serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='assignee', write_only=True, required=False)
    reviewer_id =serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='reviewer', write_only=True, required=False)


    class Meta:
        model = Task
        fields = [ 'board', 'title', 'description', 'status', 'priority', 'assignee_id', 'reviewer_id', 'due_date']
        extra_kwargs = {'board': {'required': True}, 'title': {'required': True}, 'status': {'required': True}, 'priority': {'required': True}, 'due_date': {'required': True},'description': {'required': True},}



class TaskPatchSerializer(serializers.ModelSerializer):
    assignee = TaskUserSerializer(read_only=True)
    reviewer = TaskUserSerializer(read_only=True)


    class Meta:
        model = Task
        fields = [ 'id', 'title', 'description', 'status', 'priority', 'assignee', 'reviewer', 'due_date']



class TaskSerializerforBoardDetail(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()


    class Meta:
        model = Task
        fields = [ 'id', 'title', 'description', 'status', 'priority', 'assignee', 'reviewer', 'due_date', 'comments_count']

    
    def get_comments_count(self, task):
        return task.comments.count()



class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    board = serializers.IntegerField(source='board.id', read_only=True)
    comments_count = serializers.SerializerMethodField()


    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority', 'assignee', 'reviewer', 'due_date', 'comments_count']

    def get_comments_count(self, task):
        return task.comments.count()



class ColumnSerializer(serializers.ModelSerializer): 

    
    class Meta:
        model = Column 
        fields = 'id', 'title', 'position'



class BoardCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name')
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)


    class Meta:
        model = Board 
        fields = ['title', 'members']


    def create(self, validated_data):
        request = self.context['request']
        members = validated_data.pop('members', [])

        board = Board.objects.create(owner=request.user, **validated_data)
        board.members.add(request.user)
        board.members.add(*members)
        return board



class BoardListSerializer(serializers.ModelSerializer): 
    title = serializers.CharField(source='name')
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)

    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    

    class Meta: 
        model = Board 
        fields = ['id', 'title', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id']

    
    def get_member_count(self, board):
        return board.members.count()
    

    def get_ticket_count(self, board):
        return board.tasks.count()
    

    def get_tasks_to_do_count(self, board):
        return board.tasks.filter(status='to-do').count()
    

    def get_tasks_high_prio_count(self, board):
        return board.tasks.filter(priority='high').count()



class BoardDetailSerializer(serializers.ModelSerializer): 
    title = serializers.CharField(source='name')
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskSerializerforBoardDetail(many=True, read_only=True) 


    class Meta: 
        model = Board 
        fields = ['id', 'title', 'owner_id', 'members', 'tasks'] 

    
    def get_tasks(self, board):
        tasks = Task.objects.filter(board=board)
        return TaskSerializer(tasks, many=True).data
    


class BoardUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name', required=False )
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many= True)


    class Meta:
        model = Board
        fields = ['title', 'members']

    
    def update(self, instance, validated_data):

        if 'name' in validated_data:
            instance.name = validated_data['name']
        if 'members' in validated_data:
            instance.members.set(validated_data['members'])

        instance.save()
        return instance



class BoardPatchSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name')
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = UserSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()


    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks'] 

    
    def get_tasks(self, board):
        tasks = Task.objects.filter(board=board)
        return TaskPatchSerializer(tasks, many=True).data



class BoardMembersSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name', read_only=True )
    owner_data = UserSerializer(source='owner', read_only=True)
    members_data = UserSerializer(source='members', many=True, read_only=True)


    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data']



class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()


    class Meta:
        model = Comment
        fields = ['id','created_at', 'author', 'content']


    def get_author(self, obj):
        full = f'{obj.author.first_name} {obj.author.last_name}'.strip()
        return full if full else obj.author.username



class CommentCreateSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = Comment
        fields = ['content']



