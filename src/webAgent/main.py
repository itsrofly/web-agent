import os

import streamlit as st

from webAgent import Agent, WebDriver

agent = Agent(api_key=os.getenv("GEMINI_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

st.title("Web Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# I want to receive news from blog.google, subscribe, my email is rofly@gmail.com

if prompt := st.chat_input("What is up?"):
    with st.spinner("Wait for it...", show_time=True):
        web = WebDriver()
        agent.add_tool(web.open_website)
        agent.add_tool(web.execute_action)
        agent.add_tool(web.close)

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        agent_response = agent.send(model="gemini-2.5-pro-preview-05-06", messages=st.session_state.messages)
        response = st.write_stream(agent_response)

    web.close()
    st.session_state.messages.append({"role": "assistant", "content": response})
