from django.db import models
from django.conf import settings

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
    
    # --- Auswahlmöglichkeiten (Choices) ---
    # Definiert durch Frontend-Logik (board.js) und API-Doku
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

    # --- Felder ---
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True) # Kann leer sein
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to-do')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField()

    # --- Beziehungen (Relations) ---
    
    # Gehört zu einem Board. Wenn das Board gelöscht wird, wird die Task gelöscht.
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='tasks' # Erlaubt board.tasks.all()
    )
    
    # Zugewiesener Benutzer.
    # on_delete=SET_NULL: Wenn der User gelöscht wird, bleibt die Task bestehen (wird 'unassigned').
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='assigned_tasks',
        null=True, # Muss null=True sein für SET_NULL
        blank=True # Darf im Formular leer sein
    )
    
    # Reviewer (gleiche Logik wie assignee)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='review_tasks',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title


# -------------------------------------------------------------------
# 3. Comment Modell
# -------------------------------------------------------------------
class Comment(models.Model):
    """
    Modell für einen Kommentar. Hängt an einer Task.
    Definiert durch die API-Doku.
    """
    content = models.TextField()
    
    # auto_now_add=True: Setzt das Datum automatisch beim Erstellen.
    created_at = models.DateTimeField(auto_now_add=True) 
    
    # Gehört zu einer Task.
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments' # Erlaubt task.comments.all()
    )
    
    # Gehört zu einem Autor.
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    def __str__(self):
        # Zeigt die ersten 50 Zeichen des Kommentars an
        return f'Comment by {self.author.email} on "{self.task.title}": {self.content[:50]}...'