from django.urls import path
from .views import UserRegisterView, UserLoginView, UserLogoutView, UserDetailsView, UserConfigView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('user-details/', UserDetailsView.as_view(), name='user-details'),
    path('user-config/', UserConfigView.as_view(), name='user-config'),
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
]
