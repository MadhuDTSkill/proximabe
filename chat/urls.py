from django.urls import path, include
from .views import ChatViewSet, MessageListCreateView, MessageRetrieveDestroyView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('', ChatViewSet)

urlpatterns = [
    path('', include(router.urls), name = 'chat-crud')    ,
    path('<chat_id>/message/create-list/', MessageListCreateView.as_view(), name='message-create'),
    path('<uuid:chat_id>/message/retrieve-delete/<uuid:pk>/', MessageRetrieveDestroyView.as_view(), name='message-retrieve-delete'),
]
