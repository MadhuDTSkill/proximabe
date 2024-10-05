from channels.generic.websocket import AsyncJsonWebsocketConsumer
from langchain_core.messages import trim_messages, AIMessage, HumanMessage
from uuid import UUID, uuid4  # Import uuid4 for generating random UUIDs

class BaseChatAsyncJsonWebsocketConsumer(AsyncJsonWebsocketConsumer):
    __sessions = {}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def user_connect(self):
        user = self.scope.get('user')
        if user is None:
            await self.close(code=4403)  
            return False
        else:
            await self.accept()
            self.user = self.scope.get('user')
            return True
            
    async def chat_connect(self):
        chat = self.scope.get('chat')
        if chat is None:
            await self.close(code=4403)  
            return False
        else:
            self.chat = self.scope.get('chat')
            return True
            


    async def send_msg_and_close(self, msg=''):
        await self.send_json({'detail': msg})
        await self.close()

    @classmethod
    async def generate_random_id(cls):
        # Generates a random UUID and returns it as a string
        return str(uuid4())