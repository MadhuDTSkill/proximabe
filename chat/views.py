from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Chat, Message, UploadedFile
from .serializers import ChatSerializer, MessageSerializer, UploadedFileSerializer
from .ai_vector_dbs import AIVectorDB

class ChatViewSet(ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def get_queryset(self):
        return super().get_queryset().filter(user = self.request.user)

    def list(self, request, *args, **kwargs):
        today = datetime.now().date()
        
        # Time boundaries
        today_start = today  # Beginning of today
        yesterday_start = today - timedelta(days=1)  # Beginning of yesterday
        seven_days_ago_start = today - timedelta(days=7)  # 7 days ago (starting point)
        thirty_days_ago_start = today - timedelta(days=30)  # 30 days ago (starting point)

        # Querysets for each group
        today_chats = Chat.objects.filter(created_at__date=today_start)

        yesterday_chats = Chat.objects.filter(
            created_at__date__gte=yesterday_start,
            created_at__date__lt=today_start  # Strictly yesterday
        )

        previous_7_days_chats = Chat.objects.filter(
            created_at__date__gte=seven_days_ago_start,
            created_at__date__lt=yesterday_start  # Not including yesterday or today
        )

        previous_30_days_chats = Chat.objects.filter(
            created_at__date__gte=thirty_days_ago_start,
            created_at__date__lt=seven_days_ago_start  # From 30 days ago to just before 7 days ago
        )

        # Serialize the data
        today_data = ChatSerializer(today_chats, many=True).data
        yesterday_data = ChatSerializer(yesterday_chats, many=True).data
        previous_7_days_data = ChatSerializer(previous_7_days_chats, many=True).data
        previous_30_days_data = ChatSerializer(previous_30_days_chats, many=True).data
        
        # Group the data into the required format
        response_data = {
            "Today": today_data,
            "Yesterday": yesterday_data,
            "Previous 7 Days": previous_7_days_data,
            "Previous 30 Days": previous_30_days_data
        }
    
        return Response(response_data)

        
class MessageListCreateView(ListCreateAPIView):
    
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        return super().get_queryset().filter(user = self.request.user, chat_id = self.kwargs['chat_id'])
    

class FileUploadView(CreateAPIView):

    parser_classes = (MultiPartParser, FormParser)
    serializer_class = UploadedFileSerializer
    queryset = UploadedFile.objects.all()

    def post(self, request, chat_id, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        path = obj.file.path
        chat = Chat.objects.get(id=chat_id)
        ai_vector_db = AIVectorDB()
        vector_db_path = ai_vector_db.save_vector_db(path, str(request.user.id), chat_id)   
        obj.vector_db_path = vector_db_path
        obj.save()
        chat.attach = obj
        chat.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)