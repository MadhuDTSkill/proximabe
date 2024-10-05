from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserLogoutSerializer
from .models import TokenBlockList, User

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        access = AccessToken.for_user(user)
        return Response({
            'token': str(access),
        })
        
        
class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()

        if user and user.check_password(password):
            access = AccessToken.for_user(user)
            return Response({
                'token': str(access),
            })

        return Response({'detail': 'Invalid credentials'}, status=400)

class UserLogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserLogoutSerializer

    def post(self, request):
        access_token = request.data.get("access")
        
        if not access_token:
            return Response({'detail': 'Access token is required'}, status=400)

        try:
            token = TokenBlockList(token=access_token)
            token.save()
            return Response({'detail': 'Successfully logged out'}, status=205)
        
        except TokenError:
            return Response({'detail': 'Invalid access token'}, status=400)
        except Exception:
            return Response({'detail': 'Error occurred while logging out'}, status=500)

class UserDetailsView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = self.queryset.get(id=request.user)
        user_data = self.serializer_class(user).data
        return Response(user_data)
    