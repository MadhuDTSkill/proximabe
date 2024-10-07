from typing import Generator
from base_app.consumers import BaseChatAsyncJsonWebsocketConsumer
from base_app.decorators import consumer_method_exception_handler
from .ai_chats import LLMResponse, SourceDecider
from .ai_memory import Memory
from channels.db import database_sync_to_async
from users.models import User, UserSettings
from .models import Chat
from langchain_core.chat_history import BaseChatMessageHistory
from .ai_vector_dbs import AIVectorDB
from .ai_tools import wikipedia_tool, duckduckgo_search_tool, web_url_tool
import asyncio, time

class ChatConsumer(BaseChatAsyncJsonWebsocketConsumer):
    groups = []

    async def connect(self):
        if await self.user_connect() and await self.chat_connect():
            config = await self.get_user_settings_config()
            self.llm_response = LLMResponse(config, str(self.user.id), str(self.chat.id))
            self.source_decider = SourceDecider(config, str(self.user.id), str(self.chat.id))
            
    @database_sync_to_async
    def get_attached_context(self, query) -> dict:
        self.chat = Chat.objects.get(id=self.chat.id)
        if self.chat.attach is not None:
            return AIVectorDB().get_context(self.chat.attach.vector_db_path, query)
        return None

    async def get_wikipedia_context(self, query) -> str:
        return wikipedia_tool(query)

    async def get_duckduckgo_search_context(self, query) -> str:
        return duckduckgo_search_tool(query)
    
    async def get_web_url_context(self, query) -> str:
        return web_url_tool(query)
    
    async def send_source_status(self, source:str):
        await self.send_json({
            'type': 'source_status',
            'source': source
        })
        await asyncio.sleep(0.1)
        
    
    async def get_context(self, query) -> str:
        try:
            source = self.source_decider.get_response(query)
            if 'LLM Response' in source:
                await self.send_source_status('Loading ...')
                return await self.get_attached_context(query), 'Attached Context'
            elif 'Wikipedia Search' in source:
                await self.send_source_status('Searching Wikipedia ...')
                return await self.get_wikipedia_context(query), 'Wikipedia Search Context'
            elif 'Web Search' in source:
                await self.send_source_status('Searching Web ...')
                return await self.get_duckduckgo_search_context(query), 'Web Search Context'
            elif 'Web URL' in source:
                await self.send_source_status('Searching Web URL(S) ...')
                return await self.get_web_url_context(query), 'Web URL Context'
            else:
                await self.send_source_status('Loading ...')
                return await self.get_attached_context(query), 'Attached Context'
        except Exception as e:
            print("Error:", e)
            await self.send_source_status('Loading ...')
            return await self.get_attached_context(query), 'Attached Context'

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
        await self.get_llm_response()


    async def get_session_history(self, session_id:str = 'default') -> BaseChatMessageHistory:
        return Memory.get_memory(session_id, str(self.user.id), 2000, self.llm_response.llm, True, False, 'human')
    
    async def add_response_to_session_history(self, response):
        memory = await self.get_session_history(str(self.chat.id))
        memory.add_ai_message(response)
        
    
    async def get_llm_response(self):
        context, source = await self.get_context(self.prompt)
        generator : Generator = self.llm_response.get_response(self.prompt, context, source)
        await self.stream_response(generator)
    
    async def stream_response(self, generator:Generator):
        await self.send_json({
                "id" : "uuid",
                "type" : "stream_response",
                'prompt' : self.prompt,
                "response": '<start>',
                "user_id" : str(self.user.id),
                "user_name" : str(self.user.name),
            })

        full_response = ""        
        for response in generator:
            await self.send_json({
                "type" : "stream_response",
                'prompt' : self.prompt,
                "response": response,
                "user_id" : str(self.user.id),
                "user_name" : str(self.user.name),
            })
            full_response  += response

        await self.add_response_to_session_history(full_response)

        await self.send_json({
                "type" : "stream_response",
                'prompt' : self.prompt,
                "response": "<end>",
                "full_response": full_response,
                "user_id" : str(self.user.id),
                "user_name" : str(self.user.name),
            })


    async def disconnect(self, close_code):
        if close_code == 4403:
            await self.send_json({"error": "User not found"})
        

        
      
        
        