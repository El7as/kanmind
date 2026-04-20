from django.contrib import admin


from kanban_app.models import Board, Column, Task



admin.site.register(Board)
admin.site.register(Column)
admin.site.register(Task)



def save_model(self, request, obj, form, change):
    if not obj.pk:
        obj.created_by = request.user
    super().save_model(request, obj, form, change)
