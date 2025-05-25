import os

import streamlit as st

from webAgent import Agent, WebDriver

agent = Agent(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL")
)

st.title("Web Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if "tool_calls" in message:
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# I want to receive news from blog.google, subscribe, my email is rofly@gmail.com

if prompt := st.chat_input("What is up?"):
    with st.spinner("Wait for it...", show_time=True):
        web = WebDriver()
        agent.add_tool(web.open_website)
        agent.add_tool(web.click_action)
        agent.add_tool(web.type_action)
        agent.add_tool(web.close)

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        agent_response = agent.send(model=os.getenv("MODEL_NAME"), messages=st.session_state.messages)
        response = st.write_stream(agent_response)
    st.session_state.messages.append({"role": "assistant", "content": response})
