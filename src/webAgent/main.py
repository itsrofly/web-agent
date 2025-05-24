import os

import streamlit as st

from webAgent import Agent, WebDriver

agent = Agent(api_key=os.getenv("OPENAI_API_KEY"), base_url="http://127.0.0.1:1234/v1")

st.title("Web Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Subscribe me to Deeplearning.AI newsletter, this is my e-mail address: rofly@gmail.com
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
        with st.spinner("Wait for it...", show_time=True):
            agent_response = agent.send(model="qwen3-32b", messages=st.session_state.messages, think="/think")
        response = st.write_stream(agent_response)

    web.close()
    st.session_state.messages.append({"role": "assistant", "content": response})
