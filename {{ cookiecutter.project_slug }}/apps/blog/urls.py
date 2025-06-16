from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet, CategoryViewSet, TagViewSet, CommentViewSet,
    AuthorViewSet, NewsletterViewSet, SearchAPIView,
    CommentListCreateView, PostFeedView, BlogStatsView
)

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'newsletter', NewsletterViewSet, basename='newsletter')

app_name = 'blog'

urlpatterns = [
    path('', include(router.urls)),
    path('search/', SearchAPIView.as_view(), name='search'),
    path('posts/<uuid:post_pk>/comments/', CommentListCreateView.as_view(), name='post-comments'),
    path('feed/', PostFeedView.as_view(), name='post-feed'),
    path('stats/', BlogStatsView.as_view(), name='blog-stats'),
] 