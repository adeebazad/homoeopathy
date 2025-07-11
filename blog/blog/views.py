from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, status, filters, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import BlogPost, Comment
from .serializers import BlogPostSerializer, CommentSerializer

# Create your views here.

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the owner/author
        return obj.author == request.user and request.user.role == 'DOCTOR'

class BlogPostList(generics.ListCreateAPIView):
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'author__first_name', 'author__last_name']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        # For authenticated doctors, show their drafts too
        if self.request.user.is_authenticated and self.request.user.role == 'DOCTOR':
            queryset = BlogPost.objects.all()
            if self.request.query_params.get('my_posts', None) == 'true':
                queryset = queryset.filter(author=self.request.user)
        else:
            queryset = BlogPost.objects.filter(status='PUBLISHED')
        
        # Filter by featured posts
        featured = self.request.query_params.get('featured', None)
        if featured is not None:
            queryset = queryset.filter(featured=featured.lower() == 'true')

        # Filter by author
        author_id = self.request.query_params.get('author', None)
        if author_id:
            queryset = queryset.filter(author_id=author_id)

        # Filter by status for doctors
        status = self.request.query_params.get('status', None)
        if status and self.request.user.is_authenticated and self.request.user.role == 'DOCTOR':
            queryset = queryset.filter(status=status)

        return queryset

    def perform_create(self, serializer):
        if not self.request.user.role == 'DOCTOR':
            raise permissions.PermissionDenied("Only doctors can create blog posts")
            
        # Set author and handle draft status if specified
        status = self.request.data.get('status', 'DRAFT')
        serializer.save(
            author=self.request.user,
            status=status
        )

class BlogPostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.role == 'DOCTOR':
            return BlogPost.objects.all()
        return BlogPost.objects.filter(status='PUBLISHED')

    @action(detail=True, methods=['post'])
    def feature(self, request, *args, **kwargs):
        post = self.get_object()
        if not request.user.role == 'DOCTOR':
            return Response(
                {"error": "Only doctors can feature posts"},
                status=status.HTTP_403_FORBIDDEN
            )
        post.featured = not post.featured
        post.save()
        return Response(
            {"status": "featured" if post.featured else "unfeatured"},
            status=status.HTTP_200_OK
        )

class DoctorBlogPosts(generics.ListAPIView):
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.role == 'DOCTOR':
            raise permissions.PermissionDenied("Only doctors can view their posts")
        return BlogPost.objects.filter(author=self.request.user).order_by('-created_at')

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['post', 'author', 'is_approved']
    search_fields = ['content']
    ordering_fields = ['created_at']

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.role == 'DOCTOR':
            return Comment.objects.all()
        return Comment.objects.filter(is_approved=True)

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'author', 'featured']
    search_fields = ['title', 'content', 'summary']
    ordering_fields = ['created_at', 'title']
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.role == 'DOCTOR':
            return BlogPost.objects.all()
        return BlogPost.objects.filter(status='PUBLISHED')

    def perform_create(self, serializer):
        if not self.request.user.role == 'DOCTOR':
            raise permissions.PermissionDenied("Only doctors can create blog posts")
        status_value = self.request.data.get('status', 'DRAFT')
        serializer.save(author=self.request.user, status=status_value)
