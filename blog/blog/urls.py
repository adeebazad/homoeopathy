# blog/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogPostViewSet, CommentViewSet, BlogPostList, BlogPostDetail

router = DefaultRouter()
router.register(r'posts', BlogPostViewSet, basename='blogpost')
router.register(r'comments', CommentViewSet, basename='comment')
urlpatterns = [
    path('list/', BlogPostList.as_view(), name='blog-list'),
    path('detail/<slug:slug>/', BlogPostDetail.as_view(), name='blog-detail'),
    path('', include(router.urls)),
]

