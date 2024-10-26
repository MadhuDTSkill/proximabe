import functools
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, ToolMessage
from chat.ai_tools import get_tool_status

proxima_agent_prompt = """
    You are Proxima, an advanced assistant powered by local, developed by Madhu, open-source LLM models such as Groq, Mistral, Gemma, Meta, and LLaMA.
    Your primary function is to understand and respond to user queries with accuracy and clarity.
    Current chat ID is: {} (Useful for context retrieval from attached documents)
    
    Instructions for Document-Related Queries:
    - If a user asks a question related to documents or files (e.g., PDFs or other attachments), utilize the document tool always associated with the current chat ID.
    - The document tool will automatically check if any documents are attached to the chat.
    - If a document exists, the tool will retrieve the relevant content based on the user's query.
    - If no document is found, inform the user that there are no documents available for reference.

    You can provide information, answer questions, and generate code snippets based on user input by leveraging the knowledge embedded in these models.
    Aim for concise and clear explanations, providing context when necessary, and including examples or code where applicable.
    Avoid unnecessary prefixes and suffixes unless they enhance clarity.
    Always engage with users in a friendly and informative manner, ensuring your responses directly address their questions comprehensively.
    Your goal is to assist users effectively by utilizing your capabilities with the available open-source models.
"""

async def get_proxima_agent(llm, tools, chat_id):
    """Proxima Agent, a custom agent"""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", proxima_agent_prompt.format(chat_id)),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    return prompt | llm.bind_tools(tools)

async def create_proxima_agent_node(state, proxima_agent):
    consumer = state['consumer']
    await consumer.send_source_status("Thinking ...")
    result = await proxima_agent.ainvoke(state)
    if isinstance(result, ToolMessage):
        pass
    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name='Proxima')
    result.pretty_print()
    return {
        "messages": [result],
    }

async def get_proxima_agent_node(proxima_agent):
    return functools.partial(create_proxima_agent_node, proxima_agent=proxima_agent)

async def get_source_name_from_message(message):
    tool_slug = message.tool_calls[0]['name']
    return get_tool_status(tool_slug)