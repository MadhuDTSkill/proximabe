from rest_framework import serializers
from .models import Chat, Message



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