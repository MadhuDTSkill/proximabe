from typing import Generator
from base_app.consumers import BaseChatAsyncJsonWebsocketConsumer
from base_app.decorators import consumer_method_exception_handler
from .ai_chats import LLMResponse, SourceDecider
from .ai_graphs import ProximaAgentStateGraph
from .ai_memory import Memory
from channels.db import database_sync_to_async
from users.models import User, UserSettings
from .models import Chat
from langchain_core.chat_history import BaseChatMessageHistory
from .ai_vector_dbs import AIVectorDB
import asyncio

class ChatConsumer(BaseChatAsyncJsonWebsocketConsumer):
    groups = []

    async def connect(self):
        if await self.user_connect() and await self.chat_connect():
            config = await self.get_user_settings_config()
            # self.llm_response = LLMResponse(config, str(self.user.id), str(self.chat.id))
            # self.source_decider = SourceDecider(config, str(self.user.id), str(self.chat.id))
            self.proxima_agent_graph = ProximaAgentStateGraph(self, config, str(self.user.id), str(self.chat.id))
            self.history = await self.get_session_history(str(self.chat.id))
            
    @database_sync_to_async
    def get_attached_context(self, query) -> dict:
        self.chat = Chat.objects.get(id=self.chat.id)
        if self.chat.attach is not None:
            return AIVectorDB().get_context(self.chat.attach.vector_db_path, query)
        return None
    
    async def send_source_status(self, source:str):
        await self.send_json({
            'type': 'source_status',
            'source': source
        })
        await asyncio.sleep(0.1)
        
    @database_sync_to_async
    def get_user_settings_config(self):
        try:
            user_settings = UserSettings.objects.get(user=self.user)
            config = user_settings.config
        except User.settings.RelatedObjectDoesNotExist:
            config = {}
        if config is None:
            config = {}
        return {
            "model" : config.get('model_id') or 'llama3-70b-8192',
            "temperature" : config.get("temperature") or 0.3
        }

    # @consumer_method_exception_handler
    async def receive_json(self, content, **kwargs):
        self.prompt = content.get('prompt') or ''
        await self.get_agent_response()

    async def get_session_history(self, session_id:str = 'default') -> BaseChatMessageHistory:
        return Memory.get_memory(session_id, str(self.user.id), 5000, self.proxima_agent_graph.llm, True, False, 'human')
    
    async def add_response_to_session_history(self,query,  response):
        memory = self.history
        memory.add_user_message(query)
        memory.add_ai_message(response)
    
    async def get_agent_response(self):
        # await asyncio.sleep(0.5)
        response : str = await self.proxima_agent_graph.get_response(query=self.prompt, history = self.history)
        await self.send_response(response)
    
    async def send_response(self, response):
        await self.send_json({
            'id' : await BaseChatAsyncJsonWebsocketConsumer.generate_random_id(),
            'type': 'response',
            'prompt' : self.prompt,
            'response': response,
            'user_id' : str(self.user.id),
            'user_name' : str(self.user.name),
        })
        await self.add_response_to_session_history(self.prompt, response)
    
    async def disconnect(self, close_code):
        if close_code == 4403:
            await self.send_json({"error": "User not found"})
        

        
      
        
        