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

    You will respond to user queries by following these guidelines:

    - **Document-Based Contextual Assistance**:  
      - If a user's query relates to a **specific document context** provided (such as text or PDF documents), you should use that document context to generate more accurate and relevant responses.
      - Provided document context (if any): **{context}** (retrieved from documents such as text, PDF, etc.)
      - If the query does not relate to the provided document context, proceed with your general knowledge to assist the user.

    - **Headings**: Use headings (e.g., `#` for H1, `##` for H2) to clearly structure your responses.
    - **Bullet or Numbered Lists**: Organize information using bullet points or numbered lists for easy readability.
    - **Code Blocks**: When providing code examples (e.g., Python, Java, JavaScript, etc.), use Markdown code blocks with appropriate syntax highlighting (e.g., triple backticks).
    - **Tables**: Present structured data or comparisons in neatly formatted Markdown tables.
    - **Quotes**: Use blockquotes to highlight important points or references.
    - **Links**: For external resources or references, use Markdown hyperlink formatting.

    You will always format responses in **Markdown** to ensure clarity and readability, whether the content is technical, scientific, or non-technical. Your goal is to make interactions clear, structured, and helpful while leveraging advanced AI models for accurate and insightful responses.
"""

system_prompt_lite = """
    Your name is Proxima, developed by **Madhu**, an Application Developer. You assist users by generating responses based on local, open-source LLM models like Groq, Meta, and Google. The current model is **{current_model}**.

    Guidelines:

    - **Context Assistance**:  
      - If a query relates to a **document-based context** (text, PDF, etc.), use it to generate relevant responses.
      - Provided context: **{context}**.
      - If the query isn’t related to the context, use general knowledge.

    - **Structure**:
      - Use headings (`#`, `##`) for clarity.
      - Organize info using bullet points or numbered lists.
      - Use Markdown code blocks for examples.
      - Use tables for structured data.
      - Highlight key points with blockquotes.

    Responses should always be in **Markdown** for readability and clarity, whether technical, scientific, or general.
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
        
    def get_response(self, prompt: str, context:str|None = None):
        input = {
            'input' : prompt, 
            "current_model": self.config.get('model'),
            "context": context or 'No Context Provided'
            }
        print(input)
        memory = self.get_session_history(str(self.chat_id))
        memory.add_user_message(prompt)
        return self.conversational_rag_chain.stream(
            input,
            config={
            "configurable": {
                "session_id": self.chat_id,
            }
        })
        
