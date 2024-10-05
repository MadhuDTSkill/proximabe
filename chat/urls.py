from django.urls import path, include
from .views import ChatViewSet, MessageListCreateView, FileUploadView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('', ChatViewSet)

urlpatterns = [
    path('', include(router.urls), name = 'chat-crud')    ,
    path('<chat_id>/message/create-list/', MessageListCreateView.as_view(), name='message-create'),
    path('<chat_id>/upload-file/', FileUploadView.as_view(), name='upload-file'),
]
