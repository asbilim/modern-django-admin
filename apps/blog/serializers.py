# apps/blog/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, Newsletter
from apps.core.models import Category, Tag
from .validators import validate_profanity

class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'parent', 'is_active', 'post_count', 'meta_title', 'meta_description', 'subcategories')
        read_only_fields = ('post_count',)

    def get_subcategories(self, obj):
        subcategories = obj.children.filter(is_active=True)
        return CategorySerializer(subcategories, many=True, context=self.context).data

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color', 'post_count')
        read_only_fields = ('post_count',)

class AuthorSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    # profile_image = serializers.ImageField(source='profile.image') # Example if you have a profile model

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'post_count') # 'profile_image'
    
    def get_post_count(self, obj):
        return obj.blog_posts.count()

class PostListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    absolute_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = (
            'id', 'title', 'slug', 'excerpt', 'author', 'categories', 'tags',
            'featured_image', 'is_featured', 'is_sticky', 'published_at',
            'reading_time', 'view_count', 'likes_count', 'comments_count', 'absolute_url'
        )
    
    def get_absolute_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(f'/blog/{obj.slug}/') if request else f'/blog/{obj.slug}/'


class PostDetailSerializer(PostListSerializer):
    previous_post = serializers.SerializerMethodField()
    next_post = serializers.SerializerMethodField()
    related_posts = serializers.SerializerMethodField()

    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + (
            'content', 'meta_title', 'meta_description', 'meta_keywords',
            'og_image', 'previous_post', 'next_post', 'related_posts'
        )

    def get_previous_post(self, obj):
        request = self.context.get('request')
        try:
            previous = obj.get_previous_by_published_at(status='published')
            return PostListSerializer(previous, context={'request': request}).data
        except Post.DoesNotExist:
            return None

    def get_next_post(self, obj):
        request = self.context.get('request')
        try:
            next = obj.get_next_by_published_at(status='published')
            return PostListSerializer(next, context={'request': request}).data
        except Post.DoesNotExist:
            return None
    
    def get_related_posts(self, obj, count=5):
        request = self.context.get('request')
        # Simple related by category for now
        related = Post.published.filter(categories__in=obj.categories.all()).exclude(id=obj.id)
        related = related.distinct().order_by('-published_at')[:count]
        return PostListSerializer(related, many=True, context={'request': request}).data


class CommentSerializer(serializers.ModelSerializer):
    author_display_name = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'post', 'author_display_name', 'author_website', 'user', 'parent', 'content', 'created_at', 'replies')
        read_only_fields = ('user',)

    def get_author_display_name(self, obj):
        return obj.user.username if obj.user else obj.author_name
    
    def get_replies(self, obj):
        # Recursive serialization for nested comments
        if obj.replies.exists():
            return CommentSerializer(obj.replies.filter(is_approved=True), many=True, context=self.context).data
        return []

class CommentCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(validators=[validate_profanity])

    class Meta:
        model = Comment
        fields = ('content', 'author_name', 'author_email', 'author_website', 'parent')

    def validate_author_name(self, value):
        if self.context['request'].user.is_authenticated:
            return self.context['request'].user.username
        if not value:
            raise serializers.ValidationError("Author name is required for anonymous users.")
        return value

    def validate_author_email(self, value):
        if self.context['request'].user.is_authenticated:
            return self.context['request'].user.email
        if not value:
            raise serializers.ValidationError("Author email is required for anonymous users.")
        return value

class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = ('email',)

    def validate_email(self, value):
        if Newsletter.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already subscribed.")
        return value 