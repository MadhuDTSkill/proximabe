from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
import os

apikey = os.getenv('GROQ_API_KEY')
llm = ChatGroq(api_key=apikey,temperature=0.3,model='llama3-70b-8192')
system_prompt = """
Based on the user message "{{user_message}}", create a title or name that summarizes the overall topic or theme of the conversation. The title should be concise, clear, and directly related to the main subject discussed in the user message. 

If the topic is scientific or technical, the title should reflect a high-level overview of the subject matter (e.g., "Black Hole Overview" for a discussion on black holes). The generated title should avoid unrelated or off-topic themes, focusing entirely on the core content of the user message. 

The response should be the title or name itself without any prefixes, suffixes, or additional text. It should start directly with the generated title or name for the conversation.
"""

qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

chain = qa_prompt | llm | StrOutputParser()

def get_name(user_message):
    input = f"""
        **User Message** : {user_message}
        """
    return chain.invoke({"input": input})