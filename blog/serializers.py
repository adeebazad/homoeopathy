from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import BlogPost, Comment

User = get_user_model()

class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_name', 'content', 'created_at', 'updated_at', 'is_approved']
        read_only_fields = ['author', 'is_approved', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class BlogPostSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    author_role = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    updated_at_formatted = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    author_details = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = (
            'id', 
            'title', 
            'content',
            'slug',
            'status',
            'summary',
            'featured', 
            'author', 
            'author_name',
            'author_role',
            'is_author',
            'created_at',
            'created_at_formatted',
            'updated_at',
            'updated_at_formatted',
            'image',
            'comments',
            'author_details',
        )
        read_only_fields = ('author', 'created_at', 'updated_at')

    def get_author_name(self, obj):
        if hasattr(obj.author, 'role') and obj.author.role == 'DOCTOR':
            first = obj.author.first_name or ''
            last = obj.author.last_name or ''
            name = f"Dr. {first} {last}".strip()
            return name if name != 'Dr.' else obj.author.username
        else:
            return obj.author.username

    def get_author_details(self, obj):
        return {
            'id': obj.author.id,
            'first_name': obj.author.first_name,
            'last_name': obj.author.last_name,
            'role': getattr(obj.author, 'role', None),
            'specialization': getattr(obj.author, 'specialization', None),
            'bio': getattr(obj.author, 'bio', None),
            'email': obj.author.email,
            'phone_number': getattr(obj.author, 'phone_number', None),
            'address': getattr(obj.author, 'address', None),
        }

    def get_is_author(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.author == request.user
        return False

    def get_author_role(self, obj):
        return obj.author.role if hasattr(obj.author, 'role') else None

    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime("%B %d, %Y %I:%M %p")

    def get_updated_at_formatted(self, obj):
        return obj.updated_at.strftime("%B %d, %Y %I:%M %p")

    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long")
        return value

    def validate_content(self, value):
        if len(value.strip()) < 20:
            raise serializers.ValidationError("Content must be at least 20 characters long")
        return value
