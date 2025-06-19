from rest_framework import serializers
from users.models import User
from .models import Post, PostLike, PostComment, CommentLike


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'image'
        ]


class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField('get_post_likes_count')
    post_comments_count = serializers.SerializerMethodField('get_post_comments_count')
    me_liked = serializers.SerializerMethodField('get_me_liked')

    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'image',
            'caption',
            'created_time',
            'likes_count',
            'post_comments_count',
            'me_liked'
        ]
        extra_kwargs = {"image": {"required": False}}

    @staticmethod
    def get_post_likes_count(obj):
        return obj.likes.count()

    @staticmethod
    def get_post_comments_count(obj):
        return obj.likes.count()


    def get_me_liked(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            try:
                likes = PostLike.objects.get(post= obj, author= request.user)
                return True
            except PostLike.DoesNotExist:
                return False

        return False


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField('get_likes_count')
    replies = serializers.SerializerMethodField('is_replied')
    me_liked = serializers.SerializerMethodField('get_me_liked')

    class Meta:
        model = PostComment
        fields = [
            'id',
            'author',
            'post',
            'comment',
            'parent',
            'created_time',
            'replies',
            'me_liked',
            'likes_count'
        ]

    def is_replied(self, obj):
        if obj.child.exists():
            serializer = self.__class__(obj.child.all(), many=True, context=self.context)
            return serializer.data
        return None

    def get_me_liked(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.likes.filter(author=user).exists()
        return False

    @staticmethod
    def get_likes_count(obj):
        return obj.likes.count()


class PostLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = PostLike
        fields = [
            'id',
            'author',
            'post'
        ]


class CommentLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = CommentLike
        fields = [
            'id',
            'author',
            'comment'
        ]



