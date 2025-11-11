from rest_framework import serializers
from .models import Board, Task, Comment
from users.models import CustomUser # Wir brauchen das User-Modell für die Zuweisungen

# -------------------------------------------------------------------
# 1. Ein einfacher User-Serializer (für Read-Only-Darstellungen)
# -------------------------------------------------------------------
class UserNestedSerializer(serializers.ModelSerializer):
    """
    Ein einfacher, schreibgeschützter Serializer, der Benutzerinformationen 
    für die Verschachtelung in Tasks und Boards bereitstellt (gemäß API-Doku).
    """
    class Meta:
        model = CustomUser
        # Wir halten uns an die Checkliste: Felder explizit auflisten
        fields = ['id', 'fullname', 'email']
        read_only_fields = fields # Nur zur Anzeige

# -------------------------------------------------------------------
# 2. Comment Serializer
# -------------------------------------------------------------------
class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer für Kommentare.
    Die API-Doku verlangt, dass der Autor (author)
    automatisch gesetzt und 'created_at' schreibgeschützt ist.
    """
    # 'author' soll als Name (String) angezeigt werden, nicht als ID.
    author = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Comment
        # 'task' und 'author' werden in der View gesetzt, nicht vom Client gesendet.
        fields = ['id', 'content', 'created_at', 'author', 'task']
        read_only_fields = ['created_at', 'author', 'task']

# -------------------------------------------------------------------
# 3. Task Serializer (für detaillierte Ansichten)
# -------------------------------------------------------------------
class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer für Tasks.
    Gemäß API-Doku müssen 'assignee' und 'reviewer' 
    als verschachtelte Objekte (mit id, fullname, email) angezeigt werden.
    """
    # Wir verwenden den UserNestedSerializer für die Anzeige
    assignee = UserNestedSerializer(read_only=True)
    reviewer = UserNestedSerializer(read_only=True)
    
    # Felder, die nur geschrieben (beim Erstellen/Updaten), aber nicht gelesen werden sollen
    # (z.B. POST /api/tasks/ sendet 'assignee_id', nicht das ganze Objekt)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source='assignee', write_only=True, allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source='reviewer', write_only=True, allow_null=True
    )

    # 'comments_count' ist ein berechnetes Feld, kein Datenbankfeld
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority', 'due_date',
            'assignee', 'reviewer', 'assignee_id', 'reviewer_id', 'comments_count'
        ]
        # 'board' wird beim Erstellen mitgesendet, darf aber später nicht geändert werden
        extra_kwargs = {
            'board': {'write_only': True} 
        }

    def get_comments_count(self, obj):
        # Zählt die Kommentare für diese Task (obj)
        return obj.comments.count()

# -------------------------------------------------------------------
# 4. Board Serializer (für Listen- und Detailansichten)
# -------------------------------------------------------------------
class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer für die Anzeige von Boards (GET-Anfragen).
    Gemäß API-Doku müssen wir diverse Felder berechnen
    (member_count, ticket_count, etc.).
    """
    # Berechnete Felder
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    
    # Verschachtelte Felder für die Detailansicht
    members = UserNestedSerializer(many=True, read_only=True)
    owner = UserNestedSerializer(read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    
    # Das Feld 'owner_id' wird explizit gefordert
    owner_id = serializers.ReadOnlyField(source='owner.id')

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'owner', 'owner_id', 'members', 'tasks',
            'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count'
        ]
        read_only_fields = fields # Dieser Serializer ist nur zum Lesen da

    # Methoden für die SerializerMethodFields
    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()

# -------------------------------------------------------------------
# 5. Board Serializer (für Erstellen und Update)
# -------------------------------------------------------------------
class BoardCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer für das Erstellen (POST) und Aktualisieren (PATCH) von Boards.
    Akzeptiert nur 'title' und 'members' (als Liste von IDs) gemäß API-Doku.
    """
    # 'members' erwartet eine Liste von User-IDs
    members = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        many=True,
        required=False # Man kann ein Board ohne Member erstellen
    )
    
    class Meta:
        model = Board
        fields = ['title', 'members']

    def create(self, validated_data):
        # Den 'owner' (aus dem request) automatisch hinzufügen
        owner = self.context['request'].user
        validated_data['owner'] = owner
        
        # 'members' extrahieren
        members_data = validated_data.pop('members', [])
        
        # Board erstellen
        board = Board.objects.create(**validated_data)
        
        # Owner UND Members hinzufügen (API-Doku: "Der Benutzer wird automatisch als owner erstellt und kann sich selbst als member hinzufügen")
        board.members.add(owner)
        board.members.add(*members_data) # Fügt alle anderen Member hinzu
        
        return board