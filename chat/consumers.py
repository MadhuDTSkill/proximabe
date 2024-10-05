from typing import Generator
import django.conf.urls.static
from base_app.consumers import BaseChatAsyncJsonWebsocketConsumer
from base_app.decorators import consumer_method_exception_handler
from .ai_chats import LLMResponse
from channels.db import database_sync_to_async
from users.models import User


sample = """A black hole is a region of spacetime where gravity is so strong that nothing, not even light and other electromagnetic waves, is capable of possessing enough energy to escape it.[2] Einstein's theory of general relativity predicts that a sufficiently compact mass can deform spacetime to form a black hole.[3][4] The boundary of no escape is called the event horizon. A black hole has a great effect on the fate and circumstances of an object crossing it, but it has no locally detectable features according to general relativity.[5] In many ways, a black hole acts like an ideal black body, as it reflects no light.[6][7] Quantum field theory in curved spacetime predicts that event horizons emit Hawking radiation, with the same spectrum as a black body of a temperature inversely proportional to its mass. This temperature is of the order of billionths of a kelvin for stellar black holes, making it essentially impossible to observe directly."""

class ChatConsumer(BaseChatAsyncJsonWebsocketConsumer):
    groups = []

    async def connect(self):
        if await self.user_connect() and await self.chat_connect():
            config = await self.get_user_settings_config()
            self.llm_response = LLMResponse(config, self.user.id, self.chat.id)

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

    
    async def get_llm_response(self):
        generator : Generator = self.llm_response.get_response(self.prompt)
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
        

        
      
        
        