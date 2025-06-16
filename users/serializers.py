from rest_framework import serializers
from .models import User, UserConfirmation, NEW, CODE_VERIFIED, \
    DONE, PHOTO_STEP, VIA_EMAIL, VIA_PHONE
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
    
    