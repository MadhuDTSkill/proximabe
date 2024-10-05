from rest_framework import serializers
from .models import Chat, Message, UploadedFile


class ChatSerializer(serializers.ModelSerializer):

    user = serializers.HiddenField(
      default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Chat
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    
    user = serializers.HiddenField(
      default=serializers.CurrentUserDefault()
    )

    
    class Meta:
        model = Message
        fields = '__all__'
        

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['file', 'created_at']