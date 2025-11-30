import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from backend import chatbot
import uuid


st.title('AI-Chatbot')

# -------------------------------------------------utility functiokn: 
def generate_thread_id(): 
    thread_id=uuid.uuid4()
    return thread_id

def add_thread(thread_id): 
    if thread_id not in st.session_state['thread_history']: 
        st.session_state['thread_history'].append(thread_id)

def reset_chat(): 
    thread_id=generate_thread_id()
    st.session_state['thread_id']=thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history']=[]


def load_conversations(thread_id): 
    state=chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
     # Check if messages key exists in state values, return empty list if not
    return state.values.get('messages', [])
#----------------------------------------------------session state----------------------------------------------------
if 'message_history' not in st.session_state: 
    st.session_state['message_history']=[]

if 'thread_id' not in st.session_state: 
    st.session_state['thread_id']=generate_thread_id()

if 'thread_history' not in st.session_state: 
    st.session_state['thread_history']=[]

add_thread(st.session_state['thread_id'])


#--------------------------------------------------side bar-------------------------------

with st.sidebar:
    st.title('AI Chatbot')
    if st.button('New Chat'): 
        reset_chat()

    st.header('Chat History')
    for thread_id in st.session_state['thread_history'][::-1]: 
        if st.button(str(thread_id)): 
            st.session_state['thread_id']=thread_id
            messages=load_conversations(thread_id)
            temp_messages=[]
            for msg in messages: 
                if isinstance(msg, HumanMessage): 
                    role='user'
                else: 
                    role='assistant'
                temp_messages.append({'role': role, 'content': msg.content})

            st.session_state['message_history']=temp_messages


#---------------------------------------input output--------------------------------------------------------------


for message in st.session_state['message_history']: 
    with st.chat_message(message['role']): 
        st.text(message['content'])

user_input=st.chat_input("Ask Anything")

if user_input: 

    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'): 
        st.text(user_input)

    CONFIG={'configurable': {'thread_id': st.session_state['thread_id']}}

    # first add the message to message_history
    with st.chat_message("assistant"):
        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):
                if isinstance(message_chunk, AIMessage):
                    # yield only assistant tokens
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})

