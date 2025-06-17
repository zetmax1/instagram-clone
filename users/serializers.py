from django.contrib.auth.password_validation import password_changed, validate_password
from django.core.validators import FileExtensionValidator
from django.db.models.fields import return_None
from rest_framework import serializers
from .models import User, UserConfirmation, NEW, CODE_VERIFIED, \
    DONE, PHOTO_DONE, VIA_EMAIL, VIA_PHONE
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from shared.utility import check_email_or_phone, send_email, send_phone_code

class SignUPSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only= True)

    def __init__(self, *args, **kwargs):
        super(SignUPSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required= False)

    class Meta:
        model = User
        fields = (
            'id',
            'auth_type',
            'auth_status',
        )

        extra_kwargs = {
            'auth_type': {'read_only':True, 'required': False},
            'auth_status': {'read_only': True, 'required': False},
        }

    def create(self, validated_data):
        user = super(SignUPSerializer, self).create(validated_data)
        print(user)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone_number, code)
            # send_phone_code(user.phone_number, code)
        
        user.save()

        return user



    def validate(self, data):
        super(SignUPSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(data):
        print(data)
        user_input = str(data.get('email_phone_number')).lower()
        input_type = check_email_or_phone(user_input)
        if input_type == 'email':
            data = {
                'email': user_input,
                'auth_type': VIA_EMAIL
            }
        elif input_type == 'phone':
            data = {
                'phone_number': user_input,
                'auth_type': VIA_PHONE
            }
        elif input_type is None:
            data = {
                'success': False,
                'message': 'you must enter email or phone number'
            }
            raise ValidationError(data)
        
        print(f'data {data}')

        return data
    
    def validate_email_phone_number(self, value):
        value = value.lower()
        if value and User.objects.filter(email=value).exists():
            data = {
                'success':False,
                'message': 'This email was used before',

            }
            raise ValidationError(data)
        
        elif value and User.objects.filter(phone_number=value).exists():
            data = {
                'success':False,
                'message': 'This phone number was used before',

            }
            raise ValidationError(data)



        return value

    
    def to_representation(self, instance):
        print(f'ro_repr: {instance}')
        data = super(SignUPSerializer, self).to_representation(instance)
        data.update(instance.token())

        return data

class ChangeUserInformation(serializers.Serializer):
    first_name = serializers.CharField(required= True, write_only=True)
    last_name = serializers.CharField(required= True, write_only=True)
    username = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        password= data.get('password', None)
        confirm_password = data.get('confirm_password', None)
        if password != confirm_password:
            raise ValidationError({
                "message": 'passwords do not match\nPlease enter same passwords'
            })

        if password:
            validate_password(password)
            validate_password(confirm_password)

        return data

    def validate_username(self, username):
        if len(username) < 5 or len(username) > 35:
            raise ValidationError({
                "message": "username's characters should be between 5 and 35 "
            })

        if username.isdigit():
            raise ValidationError({
                "message": "username should not be entirely numeric"
            })

        return username

    def validate_first_name(self, first_name):
        if not isinstance(first_name, str):
            raise ValidationError({
                "message": "first name cannot be numeric"
            })

        temp= first_name.strip(' ')
        if len(temp) < 2 or len(temp) > 30:
            raise ValidationError({
                "message":"please enter correct first name"
            })
        return first_name

    def validate_first_name(self, last_name):
        if not isinstance(last_name, str):
            raise ValidationError({
                "message": "last name cannot be numeric"
            })

        temp= last_name.strip(' ')
        if len(temp) < 2 or len(temp) > 30:
            raise ValidationError({
                "message":"please enter correct last name"
            })

        return last_name

    def update(self, instance, validated_data):

        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.username = validated_data.get("username", instance.username)
        instance.password = validated_data.get("password", instance.password)

        if validated_data.get("password"):
            instance.set_password(validated_data.get("password"))

        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE

        return instance



class ChangeUserPhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'webp', 'heic', 'heif', 'raw'])])
    def update(self, instance, validated_data):
        photo = validated_data.get('photo')
        if photo:
            instance.photo = photo
            instance.auth_status = PHOTO_DONE
            instance.save()
        return instance



    