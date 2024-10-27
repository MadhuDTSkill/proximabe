from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from .ai_memory import Memory
import os
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory

apikey = os.getenv('GROQ_API_KEY')


class CustomGPTResponse:
    def __init__(self, config:dict, user_id:str, chat_id:str, system_prompt) -> None:
        self.config = config
        self.llm = ChatGroq(api_key=apikey, **self.config)
        self.user_id = user_id
        self.chat_id = chat_id
        self.system_prompt = system_prompt
        self.qa_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", self.system_prompt),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{input}"),
                ]
            )

        self.chain = self.qa_prompt | self.llm | StrOutputParser()
        self.conversational_rag_chain = RunnableWithMessageHistory(
            self.chain,
            get_session_history=self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    def get_session_history(self, session_id:str = 'default') -> BaseChatMessageHistory:
        return Memory.get_memory(session_id, self.user_id, 2000, self.llm, True, False, 'human')
        
    def get_response(self, prompt: str):
        input = {
            'input' : prompt, 
            }
        memory = self.get_session_history(str(self.chat_id))
        memory.add_user_message(prompt)
        return self.conversational_rag_chain.invoke(
            input,
            config={
            "configurable": {
                "session_id": self.chat_id,
            }
        })
        
