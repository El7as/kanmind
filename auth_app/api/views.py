from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


from auth_app.api.serializer import UserCreateSerializer, UserSerializer



User = get_user_model()
@api_view(['GET'])

def email_check(request):

    """
    Check whether an email address is already registered.

    Query Parameters:
        email (str): The email address to check.

    Responses:
        200: Email exists → returns serialized user data.
        404: Email does not exist.
        400: Missing 'email' parameter.

    Use cases:
        - Frontend validation during registration.
        - Checking availability of an email.
    """

    email = request.query_params.get('email')

    if not email:
        return Response({'error': 'email parameter required'}, status=400)
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({}, status=404)
    return Response(UserSerializer(user).data, status=200)



class RegisterView(APIView):

    """
    Register a new user account.

    Permissions:
        - AllowAny: Anyone can register.

    Behavior:
        - Validates user data via UserCreateSerializer.
        - Creates the user.
        - Returns an authentication token and basic user info.

    Response:
        201 Created:
            {
                "token": "...",
                "fullname": "John Doe",
                "email": "john@example.com",
                "user_id": 1
            }
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.get(user=user)
        return Response({'token': token.key, 'fullname': f'{user.first_name} {user.last_name}'.strip(), 'email': user.email, 'user_id': user.id}, status=status.HTTP_201_CREATED)



@method_decorator(csrf_exempt, name='dispatch')
class EmailLoginView(APIView):

    """
    Login using email + password.

    Permissions:
        - AllowAny: Login must be publicly accessible.

    Behavior:
        - Validates email and password.
        - Returns token + user info on success.
        - Returns 400 on invalid credentials.

    Notes:
        - CSRF exempt because token authentication is used.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

    
        if not email or not password:
            return Response({'message': 'email and password required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'username or password Incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(password):
            return Response({'message': 'username or password Incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        
        token, _ = Token.objects.get_or_create(user=user)
        fullname = f'{user.first_name} {user.last_name}'.strip()
        return Response({'token': token.key, 'fullname': fullname, 'email': user.email, 'user_id': user.id}, status=status.HTTP_200_OK)



class LogoutView(APIView):

    """
    Logout the current user by deleting their authentication token.

    Permissions:
        - IsAuthenticated: Only logged-in users can log out.

    Behavior:
        - Deletes the user's token if present.
        - Returns 200 on success.
        - Returns 400 if no token exists.

    Response:
        200:
            {"detail": "Logout successful. Token deleted."}
        400:
            {"detail": "No token present"}
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = getattr(request.user, 'auth_token', None)

        if token:
            token.delete()
            return Response({'detail': 'Logout successful. Token deleted.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'No token present'}, status=status.HTTP_400_BAD_REQUEST)
    



