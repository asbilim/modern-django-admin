# apps/blog/views.py
from rest_framework import viewsets, generics, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.db.models import F, Q
from django.shortcuts import get_object_or_404

from .models import Post, Comment, Newsletter, PostLike
from apps.core.models import Category, Tag
from .serializers import (
    PostListSerializer, PostDetailSerializer, CategorySerializer,
    TagSerializer, CommentSerializer, CommentCreateSerializer,
    AuthorSerializer, NewsletterSerializer
)
from .permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly, CanModerateComments
from .pagination import BlogPagination
# from .filters import PostFilter, CommentFilter, CategoryFilter # Disabled due to tool issue

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.published.all().select_related('author').prefetch_related('categories', 'tags')
    serializer_class = PostListSerializer
    pagination_class = BlogPagination
    # filterset_class = PostFilter # Disabled due to tool issue
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['published_at', 'view_count', 'likes_count']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostListSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if PostLike.objects.filter(post=post, user=user).exists():
            return Response({"message": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)
        
        PostLike.objects.create(post=post, user=user)
        Post.objects.filter(pk=post.pk).update(likes_count=F('likes_count') + 1)
        return Response({"message": "Post liked successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        post = self.get_object()
        user = request.user
        like = PostLike.objects.filter(post=post, user=user)
        if not like.exists():
            return Response({"message": "You have not liked this post."}, status=status.HTTP_400_BAD_REQUEST)
        
        like.delete()
        Post.objects.filter(pk=post.pk).update(likes_count=F('likes_count') - 1)
        return Response({"message": "Post unliked successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        post = self.get_object()
        Post.objects.filter(pk=post.pk).update(view_count=F('view_count') + 1)
        return Response(status=status.HTTP_204_NO_CONTENT)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    # filterset_class = CategoryFilter # Disabled due to tool issue
    search_fields = ['name', 'description']

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        category = self.get_object()
        posts = Post.published.filter(categories=category)
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    search_fields = ['name']
    
    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        tag = self.get_object()
        posts = Post.published.filter(tags=tag)
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = AuthorSerializer

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        author = self.get_object()
        posts = Post.published.filter(author=author)
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.approved.all()
    # filterset_class = CommentFilter # Disabled due to tool issue
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [CanModerateComments]
        elif self.action == 'create':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer):
        post_id = self.request.data.get('post')
        post = get_object_or_404(Post, pk=post_id)
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(post=post, user=user, is_approved=False) 

class NewsletterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [AllowAny]

class SearchAPIView(generics.ListAPIView):
    serializer_class = PostListSerializer
    pagination_class = BlogPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if query:
            return Post.published.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query)
            ).distinct()
        return Post.published.none()

class CommentListCreateView(generics.ListCreateAPIView):
    """
    View to list and create comments for a specific post.
    """
    pagination_class = BlogPagination

    def get_queryset(self):
        post_pk = self.kwargs.get('post_pk')
        return Comment.approved.filter(post__pk=post_pk)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        post_pk = self.kwargs.get('post_pk')
        post = get_object_or_404(Post, pk=post_pk)
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(post=post, user=user, is_approved=False)

class PostFeedView(generics.ListAPIView):
    """
    An RSS-like feed of the most recent posts.
    """
    queryset = Post.published.all()[:20] # Get 20 most recent
    serializer_class = PostListSerializer 
    # In a real app, you might want a specific FeedSerializer and a custom renderer

class BlogStatsView(generics.GenericAPIView):
    """
    Provides statistics about the blog.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        stats = {
            'total_posts': Post.published.count(),
            'total_comments': Comment.approved.count(),
            'total_categories': Category.objects.filter(is_active=True).count(),
            'total_tags': Tag.objects.count(),
        }
        return Response(stats) 