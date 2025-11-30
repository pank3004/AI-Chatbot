import streamlit as st
from langchain_core.messages import HumanMessage
from backend import chatbot


CONFIG={'configurable': {'thread_id': '1'}}

st.title('AI-Chatbot')

if 'message_history' not in st.session_state: 
    st.session_state['message_history']=[]


for message in st.session_state['message_history']: 
    with st.chat_message(message['role']): 
        st.text(message['content'])

#--------------------------------------------------side bar-------------------------------
user_input=st.chat_input("Ask Anything")
with st.sidebar:
    st.markdown("### 💬 my ai assistant")
    st.markdown("Small demo using **Streamlit + LangChain/LangGraph**.")

    st.markdown("---")
    if st.button("🗑️ New chat"):
        st.session_state["message_history"] = []
        st.rerun()

    st.markdown("###### Tips")
    st.markdown(
        "- Ask coding / ML doubts\n"
        "- Practice interview questions\n"
        "- Explain concepts in simple terms"
    )


if user_input: 

    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'): 
        st.text(user_input)

    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config= CONFIG,
                stream_mode= 'messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})

