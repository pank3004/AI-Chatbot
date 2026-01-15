# type: ignore
from langgraph.graph import StateGraph, START, END
# from langchain_groq import ChatGroq
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_cerebras import ChatCerebras

from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
from langgraph.graph.message import add_messages
# from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
import sqlite3
import time
import requests

load_dotenv()

# llm=ChatGroq(model='llama-3.1-8b-instant')
# llm=ChatGoogleGenerativeAI(model='gemini-2.5-pro')
llm = ChatCerebras(model="llama-3.3-70b")


# Tools------------------------------------------------------------------------------------------------------------------
search_tool = DuckDuckGoSearchRun()

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=UK5088BQE3F2YLNI"
    r = requests.get(url)
    return r.json()



tools = [search_tool, get_stock_price, calculator]
llm_with_tools = llm.bind_tools(tools)
#--------------------------------------------------------------------------------------------------------------------------

class ChatState(TypedDict): 
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    """LLM node that may answer or request a tool call."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)


graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

# add edges: 
graph.add_edge(START, 'chat_node')
graph.add_conditional_edges('chat_node', tools_condition)
graph.add_edge('tools', 'chat_node')

conn=sqlite3.connect(database='chatbot.db', check_same_thread=False)
cheakpointer=SqliteSaver(conn=conn)

chatbot=graph.compile(checkpointer=cheakpointer)


            # if when we don't want threads in sorted order 


# CONFIG={'configurable': {'thread_id': 'thread_12'}}
# response=chatbot.invoke({'messages': [HumanMessage(content='what is the capital of india give only name?')]}, config=CONFIG)
# print(response)
# print(cheakpointer.list(None))   # object

def retrieve_all_threads(): 
    all_threads=set()
    for cheakpoint in cheakpointer.list(None): 
        all_threads.add(cheakpoint.config['configurable']['thread_id'])
    return list(all_threads)


            # when we want thread ids in sorted order
# problem : 
    # one more problem i am facing in my chat bot when i referesh the page the chat history 
    # arrengement changed ... i want alway latest history at top then second latest and so on .. 
    # but currently when i do not referesh the page then the order is mentained but after referesh 
    # it changed latest chat history go somewhere at mid ..
# that's why: this method used: 

# CONFIG={'configurable': {'thread_id': 'thread_3', 'last_activity': time.time()}}
# response=chatbot.invoke({'messages': [HumanMessage(content='hy my name is panchujji')]}, config=CONFIG)
# print(response)
# print(cheakpointer.list(None))   # object

# def retrieve_all_threads(): 
#     items={}
#     for cheakpoint in cheakpointer.list(None):

#         thread_id=cheakpoint.config['configurable']['thread_id']
#         last_activity=cheakpoint.metadata['last_activity']
#         items[thread_id]=last_activity

#     sorted_thread_ids=sorted(items, key=lambda k: items[k])

#     return sorted_thread_ids

