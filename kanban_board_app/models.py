from django.conf import settings
from django.db import models


class Board(models.Model):
    """
    Represents a Kanban board containing tasks and members.
    """
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_boards'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='boards'
    )

    def __str__(self):
        return self.title


class Task(models.Model):
    """
    Represents a task item on a specific board.
    Includes status, priority, assignment, and scheduling details.
    """
    STATUS_CHOICES = [
        ('to-do', 'To-do'),
        ('in-progress', 'In-progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='to-do'
    )
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default='medium'
    )
    due_date = models.DateField()

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='assigned_tasks',
        null=True,
        blank=True
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='review_tasks',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    Represents a user comment on a task.
    """
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    def __str__(self):
        return f'Comment by {self.author.email} on "{self.task.title}"'