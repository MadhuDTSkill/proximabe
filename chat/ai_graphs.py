import os, asyncio
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph, START
from typing import Any
from base_app.consonants import WorkFlowState
from base_app.functions import get_proxima_agent, get_proxima_agent_node, get_source_name_from_message
from .ai_tools import wikipedia_tool, duckduckgo_search_tool, web_url_tool, madhu_biography_tool, calculator_tool, document_tool

async def get_tool_node(tools: list):
    return ToolNode(tools=tools)

async def router(state):
    messages = state["messages"]
    last_message = messages[-1]
    try:
        if last_message.tool_calls:
            consumer = state['consumer']
            source_status = await get_source_name_from_message(last_message)
            await consumer.send_source_status(source_status)
            return "call_tool"
    except:
        pass
    return "forward"

def sync_router_wrapper(state):
    return asyncio.run(router(state))



class ProximaAgentStateGraph:
    def __init__(self, consumer: Any, config: dict, user_id: str, chat_id: str):
        self.chat_id = chat_id
        self.consumer = consumer
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            **config
        )
        self.all_tools = [wikipedia_tool, web_url_tool, duckduckgo_search_tool, madhu_biography_tool, calculator_tool, document_tool]

    async def init_tools(self):
        tools = [wikipedia_tool]
        return tools

    async def create_graph(self):
        graph = StateGraph(WorkFlowState)
        proxima_agent = await get_proxima_agent(self.llm, self.all_tools, self.chat_id)
        proxima_agent_node = await get_proxima_agent_node(proxima_agent)

        # adding nodes to graph
        graph.add_node('Proxima', proxima_agent_node)
        graph.add_node("Tools", await get_tool_node(self.all_tools))

        # adding edges to graph        
        graph.add_edge(START, "Proxima")
        graph.add_edge("Tools", "Proxima")

        # adding conditional edges to graph
        graph.add_conditional_edges(
            "Proxima",
            sync_router_wrapper,
            {
                "call_tool": "Tools",
                "forward": END,
            }
        )
        return graph.compile()

    async def init_graph(self):
        graph = await self.create_graph()
        return graph

    async def get_image(self, graph):
        graph_png = await graph.get_graph(xray=True).draw_mermaid_png()
        image_file = "sequential_multiagent_graph.png"
        with open(image_file, "wb") as file:
            file.write(graph_png)
        return 'Saved image to ' + image_file

    async def get_results(self, graph, query, history_messages):
        messages = history_messages + [HumanMessage(content=query)]   
        # for i in messages:
        #     i.pretty_print()
        # return []
        result = await graph.ainvoke(
            {
                "messages": messages,
                "consumer": self.consumer
            },
        )
        return result['messages']

    async def get_result(self, graph, query, history):
        results = await self.get_results(graph, query, history_messages=history.messages)
        return results[-1].content

    async def get_response(self, query: str, history) -> str:
        graph = await self.init_graph()
        return await self.get_result(graph, query, history)
