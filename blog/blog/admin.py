from django.contrib import admin
from .models import BlogPost, Comment

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'author')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at', 'author')
    search_fields = ('post__title', 'author__username', 'content')
    date_hierarchy = 'created_at'
