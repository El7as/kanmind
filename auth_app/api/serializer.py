from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


User = get_user_model()

class UserCreateSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    repeated_password = serializers.CharField(write_only=True)


    class Meta:
         model = User
         fields = ['fullname', 'email', 'password', 'repeated_password']
         extra_kwargs = {'email': {'required': True}}


    def validate(self, data):
         email = data.get('email')

         if User.objects.filter(email=email).exists():
             raise serializers.ValidationError({'email': 'Email already registered'})

         if data['password'] != data['repeated_password']:
             raise serializers.ValidationError({'password': 'Passwords do not match'})

         return data


    def create(self, validated_data):
         fullname = validated_data.pop('fullname')
         password = validated_data.pop('password')
         validated_data.pop('repeated_password')

         first, *rest = fullname.split(' ', 1)
         last = rest[0] if rest else ''

         user = User.objects.create_user(email=validated_data.get('email'), first_name=first, last_name=last, password=password)

         Token.objects.create(user=user)
         return user



class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()


    class Meta:
         model = User
         fields = ['id', 'email', 'fullname']

    
    def get_fullname(self, obj):
         full = f'{obj.first_name} {obj.last_name}'.strip()
         return full if full else obj.email

