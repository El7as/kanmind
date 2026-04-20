from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


from auth_app.api.serializer import UserCreateSerializer, UserSerializer
from auth_app.api.permissions import IsNotAuthenticated



User = get_user_model()
@api_view(['GET'])

def email_check(request):
    email = request.query_params.get('email')

    if not email:
        return Response({'error': 'email parameter required'}, status=400)
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({}, status=404)
    return Response(UserSerializer(user).data, status=200)



class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.get(user=user)
        return Response({'token': token.key, 'fullname': f'{user.first_name} {user.last_name}'.strip(), 'email': user.email, 'user_id': user.id}, status=status.HTTP_201_CREATED)



@method_decorator(csrf_exempt, name='dispatch')
class EmailLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # 500 Fehler
        if request.data.get('email') == 'Test500@Fehler.de':
            x = 1 / 0

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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = getattr(request.user, 'auth_token', None)

        if token:
            token.delete()
            return Response({'detail': 'Logout successful. Token deleted.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'No token present'}, status=status.HTTP_400_BAD_REQUEST)
    



