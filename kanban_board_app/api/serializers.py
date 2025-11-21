from rest_framework import serializers

from kanban_board_app.models import Board, Comment, Task
from user_auth_app.models import CustomUser


class UserNestedSerializer(serializers.ModelSerializer):
    """
    Serializer for nested user representation (read-only).
    
    Purpose:
    Provides a simplified user object for embedding in other responses.
    Matches exact field order from documentation: id -> email -> fullname.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'fullname']
        read_only_fields = fields


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comments.
    
    Purpose:
    - Handles validation and serialization of Comment objects.
    - Displays author's fullname instead of ID for better readability in frontend.
    """
    author = serializers.ReadOnlyField(source='author.fullname')

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['created_at', 'author']


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for full task details.
    
    Usage:
    - Used for GET /api/tasks/ (Detail & List) and POST /api/tasks/ (Create).
    
    Features:
    - Includes board reference.
    - 'assignee_id' and 'reviewer_id' are write-only fields to allow setting
      relations by ID, while 'assignee' and 'reviewer' show nested details.
    - Calculates 'comments_count' dynamically.
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
    
    Purpose:
    - Returns a limited set of fields after a successful update.
    - Excludes 'board' and 'comments_count' as per API documentation.
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
    
    Purpose:
    - Inherits validation logic from TaskSerializer.
    - Overrides 'to_representation' to use TaskPatchResponseSerializer
      for the response payload, ensuring strict adherence to the API spec.
    """
    def to_representation(self, instance):
        return TaskPatchResponseSerializer(instance, context=self.context).data


class BoardTaskSerializer(serializers.ModelSerializer):
    """
    Stripped-down task serializer for the Board Detail View.
    
    Purpose:
    - Used nested within BoardSerializer.
    - Provides essential task info without redundant parent board IDs.
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
    
    Usage:
    - Used for GET /api/boards/ and as response for POST /api/boards/.
    
    Features:
    - Includes calculated fields (member_count, ticket_count, etc.).
    - Excludes nested 'tasks' list to keep the response lightweight.
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
    
    Purpose:
    - Provides full board details including nested members and tasks.
    - Uses 'BoardTaskSerializer' for the tasks list.
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
    
    Purpose:
    - Returns specific structure for board updates: owner_data and members_data objects.
    - Excludes tasks list and count fields.
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
        """
        Creates a new Board instance.
        
        Steps:
        1. Extract members list from validated data.
        2. Set the current user as the owner.
        3. Create the Board instance.
        4. Add owner and other members to the ManyToMany relation.
        """
        members = validated_data.pop('members', [])
        owner = self.context['request'].user
        board = Board.objects.create(owner=owner, **validated_data)
        board.members.add(owner, *members)
        return board

    def to_representation(self, instance):
        """
        Customizes the output format based on the action.
        
        Logic:
        - If PATCH (update): Return BoardPatchResponseSerializer format.
        - If POST (create): Return BoardListSerializer format.
        """
        if self.context.get('view') and self.context['view'].action == 'partial_update':
            return BoardPatchResponseSerializer(instance, context=self.context).data

        return BoardListSerializer(instance, context=self.context).data