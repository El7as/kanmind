from django.db import models
from django.conf import settings



class Board(models.Model):

    """
    Represents a Kanban board that groups tasks and columns.

    Attributes:
        name (str): Human‑readable name of the board.
        description (str): Optional longer description of the board.
        created_at (datetime): Timestamp when the board was created.
        owner (User): The user who owns the board and has full permissions.
        members (QuerySet[User]): Additional users who can access the board.

        member_count (int): Cached number of board members.
        ticket_count (int): Cached number of tasks belonging to the board.
        tasks_to_do_count (int): Cached number of tasks with status "to‑do".
        tasks_high_prio_count (int): Cached number of tasks with priority "high".

    Notes:
        - The *_count fields are denormalized values for performance optimization.
        - They must be updated manually or via signals.
    """

    name = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.CASCADE, related_name='boards')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='member_boards', blank=True)

    member_count = models.IntegerField(default=0)
    ticket_count = models.IntegerField(default=0)
    tasks_to_do_count = models.IntegerField(default=0)
    tasks_high_prio_count = models.IntegerField(default=0)


    def __str__(self):
        return self.name



class Column(models.Model):

    """
    Represents a workflow column inside a board (e.g., To Do, In Progress).

    Attributes:
        board (Board): The board this column belongs to.
        position (int): Sort order of the column within the board.
        title (str): Display name of the column.

    Meta:
        ordering: Columns are always ordered by their position.
    """

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="columns")
    position = models.PositiveIntegerField(default=0)

    title = models.CharField(max_length=250)


    class Meta:
        ordering = ['position']

    def __str__(self):
         return f'{self.title} ({self.board.name})'



class Task(models.Model):

    """
    Represents a single task inside a board.

    Attributes:
        board (Board): The board this task belongs to.
        position (int): Sort order for drag‑and‑drop operations.
        created_at (datetime): Timestamp when the task was created.
        updated_at (datetime): Timestamp when the task was last updated.

        title (str): Short title describing the task.
        description (str): Optional detailed description.
        status (str): Workflow state (to‑do, in‑progress, review, done).

        assignee (User): User responsible for completing the task.
        reviewer (User): User responsible for reviewing the task.
        due_date (date): Optional deadline.
        priority (str): Priority level (low, medium, high).

        created_by (User): User who originally created the task.

    Meta:
        ordering: Tasks are ordered by their position.
    """

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    position = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=25, choices=[('to-do', 'To Do'), ('in-progress', 'In Progress'), ('review', 'Review'), ('done', 'Done'),], default='to-do')

    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, null= True, blank=True, on_delete=models.SET_NULL)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, null= True, blank=True, on_delete=models.SET_NULL, related_name='review_tasks')
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')])

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tasks')


    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.title



class Comment(models.Model):

    """
    Represents a user comment attached to a task.

    Attributes:
        task (Task): The task this comment belongs to.
        author (User): The user who wrote the comment.
        content (str): The text content of the comment.
        created_at (datetime): Timestamp when the comment was created.

    Meta:
        ordering: Newest comments appear first.
    """
    
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
            ordering = ['-created_at']

    def __str__(self):
         return f'Comment by {self.author} on {self.task}'
    

