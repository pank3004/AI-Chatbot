from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
# from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver


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

cheakpointer=InMemorySaver()

chatbot=graph.compile(checkpointer=cheakpointer)

# CONFIG={'configurable': {'thread_id': '1'}}
# response=chatbot.invoke({'messages': [HumanMessage(content='what is the capital of india')]}, config=CONFIG)

# print(response['messages'][-1].content)



# streaming: 

# CONFIG={'configurable': {'thread_id': '1'}}
# for message_chunk, metadata in chatbot.stream(
#     {'messages': [HumanMessage(content='write a essay of ai of 500 words')]}, 
#     config=CONFIG, 
#     stream_mode='messages'
# ):
#      if message_chunk.content:
#         print(message_chunk.content, end=" ", flush=True)
     
    

