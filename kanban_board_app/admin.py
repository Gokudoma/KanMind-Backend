"""
Django admin registration for the Kanban board application.
Registers Board, Task, and Comment models for administrative access.
"""

from django.contrib import admin

from .models import Board, Comment, Task

admin.site.register(Board)
admin.site.register(Comment)
admin.site.register(Task)