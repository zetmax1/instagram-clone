from django.urls import path
from .views import PostListAPIView, PostCreateAPIView, PostRetrieveUpdateDeleteAPIView, PostCommentAPIView, \
PostCommentCreateView, CommentListCreateAPIView, CommentRetrieveAPIView, PostLikeListView, CommentLikeListView, \
PostLikeAPIView, CommentLikeApiView

urlpatterns = [
    path('list/', PostListAPIView.as_view()),
    path('create/', PostCreateAPIView.as_view()),
    path('<uuid:pk>/', PostRetrieveUpdateDeleteAPIView.as_view()),
    path('<uuid:pk>/comments/', PostCommentAPIView.as_view()),
    path('<uuid:pk>/comments/create/', PostCommentCreateView.as_view()),
    path('comments/<uuid:pk>/', CommentRetrieveAPIView.as_view()),

    path('comments/create/', CommentListCreateAPIView.as_view()),
    path('<uuid:pk>/likes/', PostLikeListView.as_view()),
    path('comments/<uuid:pk>/likes/', CommentLikeListView.as_view()),
    path('<uuid:pk>/create-delete-like/', PostLikeAPIView.as_view()),
    path('comment/<uuid:pk>/create-delete-like/', CommentLikeApiView.as_view()),

]