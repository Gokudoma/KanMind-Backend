from rest_framework import serializers
from user_auth_app.models import CustomUser
from kanban_board_app.models import Board, Task, Comment

class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'fullname', 'email']
        read_only_fields = fields

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'author', 'task']
        read_only_fields = ['created_at', 'author', 'task']

class TaskSerializer(serializers.ModelSerializer):
    assignee = UserNestedSerializer(read_only=True)
    reviewer = UserNestedSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source='assignee', write_only=True, allow_null=True, required=False 
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source='reviewer', write_only=True, allow_null=True, required=False
    )
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority', 
            'due_date', 'assignee', 'reviewer', 'assignee_id', 'reviewer_id', 'comments_count'
        ]
        extra_kwargs = {'board': {'write_only': True}}

    def get_comments_count(self, obj):
        return obj.comments.count()

class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    members = UserNestedSerializer(many=True, read_only=True)
    owner = UserNestedSerializer(read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    owner_id = serializers.ReadOnlyField(source='owner.id')

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'owner', 'owner_id', 'members', 'tasks',
            'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count'
        ]

    def get_member_count(self, obj): return obj.members.count()
    def get_ticket_count(self, obj): return obj.tasks.count()
    def get_tasks_to_do_count(self, obj): return obj.tasks.filter(status='to-do').count()
    def get_tasks_high_prio_count(self, obj): return obj.tasks.filter(priority='high').count()

class BoardCreateUpdateSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), many=True, required=False
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
        return BoardSerializer(instance, context=self.context).data