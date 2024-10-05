from typing import Generator
from base_app.consumers import BaseChatAsyncJsonWebsocketConsumer
from base_app.decorators import consumer_method_exception_handler
from .ai_chats import LLMResponse
from .ai_memory import Memory
from channels.db import database_sync_to_async
from users.models import User
from langchain_core.chat_history import BaseChatMessageHistory
from .ai_vector_dbs import AIVectorDB


class ChatConsumer(BaseChatAsyncJsonWebsocketConsumer):
    groups = []

    async def connect(self):
        if await self.user_connect() and await self.chat_connect():
            config = await self.get_user_settings_config()
            self.llm_response = LLMResponse(config, str(self.user.id), str(self.chat.id))

    @database_sync_to_async
    def get_context(self, query) -> dict:
        if self.chat.attach is not None:
            return AIVectorDB().get_context(self.chat.attach.vector_db_path, query)
        return None


    @database_sync_to_async
    def get_user_settings_config(self):
        try:
            config = self.user.settings.config
        except User.settings.RelatedObjectDoesNotExist:
            config = {}
 
        return {
            "model" : config.get('model_id') or 'llama3-70b-8192',
            "temperature" : config.get("temperature") or 0.3
        }

    # @consumer_method_exception_handler
    async def receive_json(self, content, **kwargs):
        self.prompt = content.get('prompt') or ''
        await self.get_llm_response()


    async def get_session_history(self, session_id:str = 'default') -> BaseChatMessageHistory:
        return Memory.get_memory(session_id, str(self.user.id), 2000, self.llm_response.llm, True, False, 'human')
    
    async def add_response_to_session_history(self, response):
        memory = await self.get_session_history(str(self.chat.id))
        memory.add_ai_message(response)
        
    
    async def get_llm_response(self):
        context = await self.get_context(self.prompt)
        generator : Generator = self.llm_response.get_response(self.prompt, context)
        await self.stream_response(generator)
    
    async def stream_response(self, generator:Generator):
        await self.send_json({
                "id" : "uuid",
                'prompt' : self.prompt,
                "response": '<start>',
                "user_id" : str(self.user.id),
                "user_name" : str(self.user.name),
            })

        full_response = ""        
        for response in generator:
            await self.send_json({
                'prompt' : self.prompt,
                "response": response,
                "user_id" : str(self.user.id),
                "user_name" : str(self.user.name),
            })
            full_response  += response

        await self.add_response_to_session_history(full_response)

        await self.send_json({
                'prompt' : self.prompt,
                "response": "<end>",
                "full_response": full_response,
                "user_id" : str(self.user.id),
                "user_name" : str(self.user.name),
            })


    async def disconnect(self, close_code):
        if close_code == 4403:
            await self.send_json({"error": "User not found"})
        

        
      
        
        