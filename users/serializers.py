from rest_framework import serializers
from .models import User, UserSettings

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'password', 'is_active', 'is_staff', 'is_superuser', 'last_login']
        read_only_fields = ['id', 'last_login', 'is_active', 'is_staff', 'is_superuser']


    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    email =  serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserLogoutSerializer(serializers.ModelSerializer):
    access = serializers.CharField(write_only=True)
    
class UserConfigSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserSettings
        fields = '__all__'