from django.db import models
from django.conf import settings



# Create your models here.



class Board(models.Model):
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
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="columns")
    position = models.PositiveIntegerField(default=0)

    title = models.CharField(max_length=250)


    class Meta:
        ordering = ['position']

    def __str__(self):
         return f'{self.title} ({self.board.name})'



class Task(models.Model):
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
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
            ordering = ['-created_at']

    def __str__(self):
         return f'Comment by {self.author} on {self.task}'
    

