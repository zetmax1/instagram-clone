from django.core.serializers import serialize
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.views import APIView

from .models import PostLike, PostComment, Post, CommentLike
from .serializers import UserSerializer, PostLikeSerializer, PostSerializer, CommentSerializer, CommentLikeSerializer
from shared.custom_pagination import CustomPagination
from rest_framework.response import Response


class PostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny, ]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Post.objects.all()


class PostCreateAPIView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    serializer_class = PostSerializer

    def put(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.serializer_class(post, data=request.data)
        serializer.is_valid(raise_exception= True)
        serializer.save()
        return Response(
            {
                "success": True,
                "code": status.HTTP_200_OK,
                "message": "Post successfully updated",
                "data": serializer.data
            }
        )

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        post.delete()
        return Response(
            {
                "success": True,
                "code": status.HTTP_200_OK,
                "message": "Post successfully deleted",
            }
        )


class PostCommentAPIView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        post_id = self.kwargs['pk']
        queryset = PostComment.objects.filter(post__id=post_id)
        return queryset


class PostCommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        post_id = self.kwargs['pk']
        serializer.save(author= self.request.user, post_id = post_id)


class CommentListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    serializer_class = CommentSerializer
    pagination_class = CustomPagination
    queryset = PostComment.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)



class CommentRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny, ]
    queryset = PostComment.objects.all()


class PostLikeListView(generics.ListAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        post_id = self.kwargs['pk']
        return PostLike.objects.filter(post_id=post_id)


class CommentLikeListView(generics.ListAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        comment_id = self.kwargs['pk']
        return CommentLike.objects.filter(comment_id=comment_id)


class PostLikeAPIView(APIView):

    # def post(self, request, pk):
    #     try:
    #         post_like = PostLike.objects.create(
    #             author= self.request.user,
    #             post_id=pk,
    #         )
    #         serializer = PostLikeSerializer(post_like)
    #         data = {
    #             "success": True,
    #             "message": "New post like successfully added",
    #             "data": serializer.data,
    #         }
    #         return Response(data, status=status.HTTP_201_CREATED)
    #     except Exception as e:
    #         data = {
    #             "success": False,
    #             "message": f"{str(e)}",
    #             "data": None,
    #         }
    #         return Response(data, status=status.HTTP_400_BAD_REQUEST)
    #
    # def delete(self, request, pk):
    #     try:
    #         post_like = PostLike.objects.get(
    #             author=self.request.user,
    #             post_id=pk,
    #         )
    #         post_like.delete()
    #         data = {
    #             "success": True,
    #             "message": "Like successfully DELETED",
    #             "data": None,
    #         }
    #         return Response(data, status=status.HTTP_204_NO_CONTENT)
    #     except Exception as e:
    #         data = {
    #             "success": False,
    #             "message": f"{str(e)}",
    #             "data": None,
    #         }
    #         return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk):
        try:
            post_like = PostLike.objects.get(
                author= self.request.user,
                post_id= pk
            )
            post_like.delete()
            data = {
                "success": True,
                "message": "Like successfully DELETED",
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        except PostLike.DoesNotExist:
            post_like = PostLike.objects.create(
                author= self.request.user,
                post_id=pk,
            )
            serializer = PostLikeSerializer(post_like)
            data = {
                "success": True,
                "message": "New post like successfully added",
                "data": serializer.data,
            }
            return Response(data, status=status.HTTP_201_CREATED)


class CommentLikeApiView(APIView):

    def post(self, request, pk):
        try:
            comment_like = CommentLike.objects.get(
                author= self.request.user,
                comment_id= pk
            )
            comment_like.delete()
            data = {
                "success": True,
                "message": "Like successfully DELETED",
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        except CommentLike.DoesNotExist:
            comment_like = CommentLike.objects.create(
                author= self.request.user,
                comment_id=pk,
            )
            serializer = CommentLikeSerializer(comment_like)
            data = {
                "success": True,
                "message": "New comment like successfully added",
                "data": serializer.data,
            }
            return Response(data, status=status.HTTP_201_CREATED)

