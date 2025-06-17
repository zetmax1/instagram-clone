from rest_framework.utils.representation import serializer_repr

from .serializers import SignUPSerializer, ChangeUserInformation, ChangeUserPhotoSerializer
from .models import User, DONE, CODE_VERIFIED, NEW, VIA_EMAIL, VIA_PHONE
from rest_framework import permissions
from rest_framework.decorators import permission_classes
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.views import APIView
from datetime import datetime
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from shared.utility import send_email

class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = SignUPSerializer


class VerifyAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        user = self.request.user             
        code = self.request.data.get('code') 

        self.check_verify(user, code)
        return Response(
            data={
                "success": True,
                "auth_status": user.auth_status,
                "access": user.token()['access'],
                "refresh": user.token()['refresh_token']
            }
        )

    @staticmethod
    def check_verify(user, code):      
        verifies = user.verify_code.filter(expiration_time__gte=datetime.now(), code=code, is_confirmed=False)
        print(verifies)
        if not verifies.exists():
            data = {
                "message": "Verification code is wrong or expired"
            }
            raise ValidationError(data)
        else:
            verifies.update(is_confirmed=True)
        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.save()
        return True


class GetNewVerification(APIView):
    
    def get(self, request, *args, **kwargs):
        user = self.request.user
        self.check_verification(user)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone_number, code)
        else: 
            data = {
                'message': 'Email or phone number is wrong entered'
            }
            raise ValidationError(data)
        
        return Response(
            {
                "success": True,
                "message": "We sent verification code again"
            }
        )
        

    @staticmethod
    def check_verification(user):
        verifies = user.verify_code.filter(expiration_time=datetime.now(), is_confirmed= False)
        if verifies.exists():
            data = {
                "message": "Your verification code is still val please wait"
            }
            raise ValidationError(data)


class ChangeUserInformationView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = ChangeUserInformation
    http_method_names = ['patch', 'put']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super(ChangeUserInformationView, self).update(request, *args, **kwargs)
        data = {
            "status": True,
            "message": "User information successfully changed",
            "auth_status": self.request.user.auth_status,
        }
        return Response(data, status=200)

    def partial_update(self, request, *args, **kwargs):
        super(ChangeUserInformationView, self).partial_update(request, *args, **kwargs)
        data = {
            "status": True,
            "message": "User information successfully changed",
            "auth_status": self.request.user.auth_status,
        }
        return Response(data, status=200)


class ChangeUserPhotoView(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def put(self, request, *args, **kwargs):
        serializer= ChangeUserPhotoSerializer(data=request.data)
        if serializer.is_valid():
            user= request.user
            serializer.update(user, serializer.validated_data)
            return Response({
                "status": True,
                "message": "photo successfully changed"
            }, status=200)
        return Response(serializer.errors, status=400)

