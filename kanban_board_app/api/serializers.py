from rest_framework import serializers

from kanban_board_app.models import Board, Comment, Task
from user_auth_app.models import CustomUser


class UserNestedSerializer(serializers.ModelSerializer):
    """
    Serializer for nested user representation (read-only).
    Matches exact field order from documentation: id -> email -> fullname.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'fullname']
        read_only_fields = fields


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comments.
    Displays author's fullname instead of ID.
    """
    author = serializers.ReadOnlyField(source='author.fullname')

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['created_at', 'author']


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for full task details (GET /api/tasks/ and POST).
    Includes board reference and counts.
    """
    assignee = UserNestedSerializer(read_only=True)
    reviewer = UserNestedSerializer(read_only=True)

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='assignee',
        write_only=True,
        allow_null=True,
        required=False
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='reviewer',
        write_only=True,
        allow_null=True,
        required=False
    )

    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'due_date', 'assignee', 'reviewer', 'assignee_id', 'reviewer_id',
            'comments_count'
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()


class TaskPatchResponseSerializer(serializers.ModelSerializer):
    """
    Specific serializer for PATCH responses of Tasks.
    Excludes 'board' and 'comments_count' as per documentation.
    """
    assignee = UserNestedSerializer(read_only=True)
    reviewer = UserNestedSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date'
        ]


class TaskUpdateSerializer(TaskSerializer):
    """
    Serializer specifically for updating tasks.
    Inherits validation logic from TaskSerializer but uses
    TaskPatchResponseSerializer for the response format.
    """
    def to_representation(self, instance):
        return TaskPatchResponseSerializer(instance, context=self.context).data


class BoardTaskSerializer(serializers.ModelSerializer):
    """
    Stripped-down task serializer for the Board Detail View.
    """
    assignee = UserNestedSerializer(read_only=True)
    reviewer = UserNestedSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date', 'comments_count'
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()


class BoardListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing boards (summary view).
    Used for GET /api/boards/ and POST response.
    """
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.ReadOnlyField(source='owner.id')

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'member_count', 'ticket_count',
            'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id'
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()


class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed board view (GET /api/boards/{id}/).
    Includes nested members and tasks.
    """
    owner_id = serializers.ReadOnlyField(source='owner.id')
    members = UserNestedSerializer(many=True, read_only=True)
    tasks = BoardTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']


class BoardPatchResponseSerializer(serializers.ModelSerializer):
    """
    Specific serializer for PATCH responses.
    Includes owner_data and members_data, but NO tasks and NO counts.
    """
    owner_data = UserNestedSerializer(source='owner', read_only=True)
    members_data = UserNestedSerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data']


class BoardCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating boards.
    """
    members = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Board
        fields = ['title', 'members']

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        owner = self.context['request'].user
        board = Board.objects.create(owner=owner, **validated_data)
        board.members.add(owner, *members)
        return board

    def to_representation(self, instance):
        if self.context.get('view') and self.context['view'].action == 'partial_update':
            return BoardPatchResponseSerializer(instance, context=self.context).data

        return BoardListSerializer(instance, context=self.context).data