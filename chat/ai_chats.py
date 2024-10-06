from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from .ai_memory import Memory
import os
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory

apikey = os.getenv('GROQ_API_KEY')

system_prompt = """
    Your name is Proxima, developed by **Madhu**, an Application Developer. You are designed to assist users by generating responses based on interactions with local, open-source LLM models from providers like Groq, Meta, and Google. You are currently using the model: **{current_model}**.

    You will respond to user queries by following these simple guidelines:

    - **Document-Based Contextual Assistance**:  
      - If a user's query relates to a **specific document context** provided (such as text or PDF documents), you should use that document context to generate more accurate and relevant responses.
      - Provided document context (if any): **{context}** (retrieved from documents such as text, PDF, etc.)
      - **Context Source**: **{context_source}** (Possible sources include: "Wikipedia search result", "DuckDuckGo search context", "Scraped web page content from specific url", "User-uploaded document (PDF/Text)")
      - If the query does not relate to the provided document context, proceed with your general knowledge to assist the user.

    Only use prefixes and suffixes when they naturally fit the response context.
"""

system_prompt_for_source_decide = """
    You are tasked with determining the most appropriate mechanism for handling a user’s query. Based on the input prompt, you will output one of the following four options as a single string:

    - **LLM Response**
    - **Wikipedia Search**
    - **Web Search**
    - **Web URL** (only if the user provides a URL)

    Guidelines:
    - If the query involves general, code programming or conceptual information that does not require real-time data, output **LLM Response**.
    - If the query is about specific, factual data, output **Wikipedia Search**.
    - If the query relates to real-time or rapidly changing information (e.g., current events, sports scores), output **Web Search**.
    - If the user asks for specific details related to a web page and provides a URL, output **Web URL**. 
    - If the query mentions a web page but no URL is provided, do not suggest **Web URL** and select another appropriate option.

    Only output the chosen option as a string. Do not include any additional text, explanation, or formatting.
"""



class LLMResponse:
    def __init__(self, config:dict, user_id:str, chat_id:str) -> None:
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
        
    def get_response(self, prompt: str, source : str, context:str|None = None):
        input = {
            'input' : prompt, 
            "current_model": self.config.get('model'),
            "context": context or 'No Context Provided',
            "context_source" : source
            }
        memory = self.get_session_history(str(self.chat_id))
        memory.add_user_message(prompt)
        return self.conversational_rag_chain.stream(
            input,
            config={
            "configurable": {
                "session_id": self.chat_id,
            }
        })
        

class SourceDecider:
    def __init__(self, config:dict, user_id:str, chat_id:str) -> None:
        self.config = config
        self.llm = ChatGroq(api_key=apikey, **self.config)
        self.user_id = user_id
        self.chat_id = chat_id
        self.system_prompt = system_prompt_for_source_decide
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
        return self.conversational_rag_chain.invoke(
            input,
            config={
            "configurable": {
                "session_id": self.chat_id,
            }
        })
        

