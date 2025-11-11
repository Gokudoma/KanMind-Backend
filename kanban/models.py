from django.db import models
from django.conf import settings # Importiert die settings, um das CustomUser-Modell zu nutzen

# -------------------------------------------------------------------
# 1. Board Modell
# -------------------------------------------------------------------
class Board(models.Model):
    """
    Modell für ein Kanban-Board.
    Definiert durch die API-Doku.
    """
    title = models.CharField(max_length=255)
    
    # 'owner' ist der Ersteller des Boards.
    # related_name='owned_boards' erlaubt uns, user.owned_boards abzufragen.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_boards'
    )
    
    # 'members' sind die zugewiesenen Benutzer.
    # related_name='boards' erlaubt uns, user.boards abzufragen.
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='boards'
    )

    # __str__ Methode ist Pflicht laut Checkliste
    def __str__(self):
        return self.title

# -------------------------------------------------------------------
# 2. Task Modell
# -------------------------------------------------------------------
class Task(models.Model):
    """
    Modell für eine Task. Hängt an einem Board.
    Definiert durch die API-Doku.
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to-do')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
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
    Modell für einen Kommentar. Hängt an einer Task.
    Definiert durch die API-Doku.
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
        return f'Comment by {self.author.email} on "{self.task.title}": {self.content[:50]}...'