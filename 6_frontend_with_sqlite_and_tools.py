# type: ignore
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from backend_with_sqlite_and_tools import chatbot, retrieve_all_threads
import uuid
import time


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
    st.session_state['thread_titles'][thread_id]='Current Chat'


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
    st.session_state['thread_history']=retrieve_all_threads()

if 'thread_titles' not in st.session_state:
    st.session_state['thread_titles'] = {}
    for t_id in st.session_state['thread_history']:
        messages = load_conversations(t_id)

        # default
        title = "Current Chat"
        for msg in messages:
            if isinstance(msg, HumanMessage):
                short_title = msg.content.strip()
                if len(short_title) > 27:
                    short_title = short_title[:24] + "..."
                title = short_title or "Current Chat"
                break

        st.session_state['thread_titles'][t_id] = title

add_thread(st.session_state['thread_id'])

if st.session_state['thread_id'] not in st.session_state['thread_titles']: 
    st.session_state['thread_titles'][st.session_state['thread_id']]='Current Chat'


#--------------------------------------------------side bar-------------------------------

with st.sidebar:
    st.title('AI Chatbot')
    if st.button('🖊️ New Chat'): 
        reset_chat()

    st.header('Chat History')
    for thread_id in st.session_state['thread_history'][::-1]: 
        title=st.session_state['thread_titles'].get(thread_id, str(thread_id)[:8])
        if st.button(title, key=f"thread_{thread_id}"): 
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
        st.markdown(message['content'])

user_input=st.chat_input("Ask Anything")

if user_input: 

    current_thread=st.session_state['thread_id']
    existing_title=st.session_state['thread_titles'].get(current_thread, 'Current Chat')
    if existing_title=='Current Chat': 
        short_title=user_input.strip()
        if len(short_title)>27: 
            short_title=short_title[:24]+"..."
        st.session_state['thread_titles'][current_thread]=short_title or 'Current Chat'

    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'): 
        st.text(user_input)

    CONFIG={'configurable': {'thread_id': st.session_state['thread_id'], 'last_activity': time.time()}}

    # Assistant streaming block
    with st.chat_message("assistant"):
        # Use a mutable holder so the generator can set/modify it
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                # Lazily create & update the SAME status container when any tool runs
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                # Stream ONLY assistant tokens
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        # Finalize only if a tool was actually used
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished", state="complete", expanded=False
            )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})