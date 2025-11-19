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


    response=chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=CONFIG)
    ai_message=response['messages'][-1].content
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    with st.chat_message('assistant'): 
        st.text(ai_message)
