from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


User = get_user_model()

class UserCreateSerializer(serializers.ModelSerializer):
     
    """
    Serializer for registering a new user.

    Fields:
        fullname (str): Full name entered by the user (split into first/last name).
        email (str): Unique email address used for authentication.
        password (str): Raw password (validated using Django's password validators).
        repeated_password (str): Must match the password field.

    Validation:
        - Email must be unique.
        - Password and repeated_password must match.
        - Password must pass Django's password validation.

    Behavior:
        - Splits fullname into first_name and last_name.
        - Creates the user via CustomUserManager.create_user().
        - Automatically creates an authentication token.

    Returns:
        User instance.
    """

    password = serializers.CharField(write_only=True, validators=[validate_password])
    repeated_password = serializers.CharField(write_only=True)


    class Meta:
         model = User
         fields = ['fullname', 'email', 'password', 'repeated_password']
         extra_kwargs = {'email': {'required': True}}


    def validate(self, data):
         # Validate email uniqueness and matching passwords.

         email = data.get('email')

         if User.objects.filter(email=email).exists():
             raise serializers.ValidationError({'email': 'Email already registered'})

         if data['password'] != data['repeated_password']:
             raise serializers.ValidationError({'password': 'Passwords do not match'})

         return data


    def create(self, validated_data):
         # Create a new user. Steps: Extract fullname and split into first/last name. Create user with email + password. Create authentication token.

         fullname = validated_data.pop('fullname')
         password = validated_data.pop('password')
         validated_data.pop('repeated_password')

         first, *rest = fullname.split(' ', 1)
         last = rest[0] if rest else ''

         user = User.objects.create_user(email=validated_data.get('email'), first_name=first, last_name=last, password=password)

         Token.objects.create(user=user)
         return user



class UserSerializer(serializers.ModelSerializer):
    
    """
    Serializer for returning basic user information.

    Fields:
        id (int)
        email (str)
        fullname (str): Computed from first_name + last_name, fallback to email.
    """

    fullname = serializers.SerializerMethodField()


    class Meta:
         model = User
         fields = ['id', 'email', 'fullname']

    
    def get_fullname(self, obj):
         # Return full name or fallback to email.
         
         full = f'{obj.first_name} {obj.last_name}'.strip()
         return full if full else obj.email

