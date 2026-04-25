from rest_framework import serializers

from django.contrib.auth import get_user_model


from kanban_app.models import Board, Task, Column, Comment



User = get_user_model()



class UserSerializer(serializers.ModelSerializer):

    """
    Serializer for representing user information in task and board responses.

    Fields:
        id (int): Primary key of the user.
        email (str): Email address of the user.
        fullname (str): Computed full name (first + last name). Falls back to username.

    Notes:
        - get_fullname handles both User instances and integer IDs.
    """

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

    """
    Serializer for updating an existing task (PATCH or PUT).

    Fields:
        title (str): Optional updated title.
        description (str): Optional updated description.
        status (str): Updated workflow state.
        priority (str): Updated priority.
        assignee_id (int): User ID of the new assignee.
        reviewer_id (int): User ID of the new reviewer.
        due_date (date): Updated deadline.

    Notes:
        - assignee_id and reviewer_id map to the actual FK fields via 'source'.
    """

    assignee_id =serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='assignee', write_only=True, required=False)
    reviewer_id =serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='reviewer', write_only=True, required=False)


    class Meta:
        model = Task
        fields = [ 'title', 'description', 'status', 'priority', 'assignee_id', 'reviewer_id', 'due_date']



class TaskUserSerializer(serializers.ModelSerializer):

    """
    Lightweight user serializer for embedding user info inside task responses.

    Fields:
        id (int)
        email (str)
        fullname (str): Computed full name or email fallback.
    """

    fullname = serializers.SerializerMethodField()


    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    
    def get_fullname(self, obj):

        if not hasattr(obj, 'first_name') or not hasattr(obj, 'last_name'): return obj.email
        full = f'{obj.first_name} {obj.last_name}'.strip()
        return full if full else obj.email



class TaskCreateSerializer(serializers.ModelSerializer):

    """
    Serializer for creating new tasks.

    Fields:
        board (int): ID of the board the task belongs to.
        title (str)
        description (str)
        status (str)
        priority (str)
        assignee_id (int)
        reviewer_id (int)
        due_date (date)

    Notes:
        - board is validated in the ViewSet.
        - assignee_id and reviewer_id map to FK fields.
    """

    board = serializers.IntegerField()
    assignee_id =serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='assignee', write_only=True, required=False)
    reviewer_id =serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='reviewer', write_only=True, required=False)


    class Meta:
        model = Task
        fields = [ 'board', 'title', 'description', 'status', 'priority', 'assignee_id', 'reviewer_id', 'due_date']
        extra_kwargs = {'board': {'required': True}, 'title': {'required': True}, 'status': {'required': True}, 'priority': {'required': True}, 'due_date': {'required': True},'description': {'required': True},}



class TaskPatchSerializer(serializers.ModelSerializer):

    """
    Read-only serializer for returning updated task data after PATCH.

    Fields:
        id (int)
        title (str)
        description (str)
        status (str)
        priority (str)
        assignee (User)
        reviewer (User)
        due_date (date)
    """

    assignee = TaskUserSerializer(read_only=True)
    reviewer = TaskUserSerializer(read_only=True)


    class Meta:
        model = Task
        fields = [ 'id', 'title', 'description', 'status', 'priority', 'assignee', 'reviewer', 'due_date']



class TaskSerializerforBoardDetail(serializers.ModelSerializer):

    """
    Serializer for embedding tasks inside BoardDetail responses.

    Adds:
        comments_count (int): Number of comments on the task.
    """

    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()


    class Meta:
        model = Task
        fields = [ 'id', 'title', 'description', 'status', 'priority', 'assignee', 'reviewer', 'due_date', 'comments_count']

    
    def get_comments_count(self, task):
        return task.comments.count()



class TaskSerializer(serializers.ModelSerializer):

    """
    Full task serializer for list and detail views.

    Adds:
        board (int): Board ID.
        comments_count (int)
    """

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

    """
    Serializer for Kanban columns.

    Fields:
        id (int)
        title (str)
        position (int)
    """
    class Meta:
        model = Column 
        fields = 'id', 'title', 'position'



class BoardCreateSerializer(serializers.ModelSerializer):

    """
    Serializer for creating new boards.

    Fields:
        title (str): Mapped to Board.name.
        members (list[int]): Optional list of user IDs.

    Notes:
        - The request user becomes owner AND member.
        - Additional members are added automatically.
    """


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

    """
    Serializer for listing boards with computed statistics.

    Adds:
        member_count (int)
        ticket_count (int)
        tasks_to_do_count (int)
        tasks_high_prio_count (int)
    """

    title = serializers.CharField(source='name')
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)

    member_count = serializers.IntegerField(read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)
    

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

    """
    Detailed board serializer including members and tasks.

    Fields:
        id (int)
        title (str)
        owner_id (int)
        members (list[User])
        tasks (list[Task])
    """

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

    """
    Serializer for updating board metadata.

    Fields:
        title (str): Mapped to Board.name.
        members (list[int]): New member list.

    Notes:
        - Members are fully replaced using .set().
    """

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

    """
    Read-only serializer for returning updated board data after PATCH.

    Adds:
        tasks (list[TaskPatchSerializer])
    """

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

    """
    Serializer for returning board membership information.

    Fields:
        id (int)
        title (str)
        owner_data (User)
        members_data (list[User])
    """

    title = serializers.CharField(source='name', read_only=True )
    owner_data = UserSerializer(source='owner', read_only=True)
    members_data = UserSerializer(source='members', many=True, read_only=True)


    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data']



class CommentSerializer(serializers.ModelSerializer):

    """
    Serializer for returning comment data.

    Fields:
        id (int)
        created_at (datetime)
        author (str): Full name or username.
        content (str)
    """

    author = serializers.SerializerMethodField()


    class Meta:
        model = Comment
        fields = ['id','created_at', 'author', 'content']


    def get_author(self, obj):
        full = f'{obj.author.first_name} {obj.author.last_name}'.strip()
        return full if full else obj.author.username



class CommentCreateSerializer(serializers.ModelSerializer):
    
    """
    Serializer for creating new comments.

    Fields:
        content (str): The comment text.
    """

    class Meta:
        model = Comment
        fields = ['content']



