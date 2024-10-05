from channels.db import database_sync_to_async
from users.models import User
from chat.models import Chat
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import AccessToken

@database_sync_to_async
def get_user(id):
    try:
        return User.objects.get(id=id)
    except User.DoesNotExist:
        return None
    
@database_sync_to_async
def get_chat(id):
    try:
        return Chat.objects.get(id=id)
    except User.DoesNotExist:
        return None
    

class WsAuthMiddleware:

    def __init__(self, app):
        self.app = app
        
        
    async def authenticate(self, scope):
        query_string = scope.get('query_string', None)
        if not query_string or query_string == '':
            return None
        try:
            token = query_string.decode('utf-8').strip().split('=')[1]
            access_token = AccessToken(token)
            payload = access_token.payload
            access_token.verify()
            # print('payload : ', payload)
            return await get_user(payload.get('user_id'))
        except Exception as e:
            print(e)
            return None        
     
    async def connect_to_chat(self, scope):
        raw_path = scope.get('raw_path', None)
        if not raw_path or raw_path == '':
            return None    
        try:
            chat_id = raw_path.decode('utf-8').split('/')[-1]
            return await get_chat(chat_id)
        except Exception as e:
            print(e)
            return None
            
    async def __call__(self, scope, receive, send):
        user, chat = await self.authenticate(scope), await self.connect_to_chat(scope)
        scope['user'] = user
        scope['chat'] = chat
        return await self.app(scope, receive, send)
    