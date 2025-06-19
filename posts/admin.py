from django.contrib import admin
from .models import PostLike, PostComment, Post, CommentLike


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'caption', 'created_time']
    search_fields = ['id', 'author__username', 'caption']


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'comment','parent', 'created_time']
    search_fields = ['id', 'author__username', 'post', 'comment']


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'created_time']
    search_fields = ['id', 'author__username', 'post']


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'comment', 'created_time']
    search_fields = ['id', 'author__username', 'comment']