# type: ignore
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
# from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
from langgraph.graph.message import add_messages
# from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import time

load_dotenv()

llm=ChatGroq(model='llama-3.1-8b-instant')
# llm=ChatGoogleGenerativeAI(model='gemini-2.5-pro')

class ChatState(TypedDict): 
    messages: Annotated[list[BaseMessage], add_messages]

def chat_model(state: ChatState): 
    response=llm.invoke(state['messages'])
    return {'messages': [response]}

# define graph
graph=StateGraph(ChatState)

# add nodes: 
graph.add_node('chat_model', chat_model)

# add edges: 
graph.add_edge(START, 'chat_model')
graph.add_edge('chat_model', END)


conn=sqlite3.connect(database='chatbot.db', check_same_thread=False)
cheakpointer=SqliteSaver(conn=conn)

chatbot=graph.compile(checkpointer=cheakpointer)


            # if when we don't want threads in sorted order 


# CONFIG={'configurable': {'thread_id': 'thread_3'}}
# response=chatbot.invoke({'messages': [HumanMessage(content='hy my name is panchujji')]}, config=CONFIG)
# print(response)
# print(cheakpointer.list(None))   # object

# def retrieve_all_threads(): 
#     all_threads=set()
#     for cheakpoint in cheakpointer.list(None): 
#         all_threads.add(cheakpoint.config['configurable']['thread_id'])
#     return list(all_threads)


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

def retrieve_all_threads(): 
    items={}
    for cheakpoint in cheakpointer.list(None):

        thread_id=cheakpoint.config['configurable']['thread_id']
        last_activity=cheakpoint.metadata['last_activity']
        items[thread_id]=last_activity

    sorted_thread_ids=sorted(items, key=lambda k: items[k])

    return sorted_thread_ids