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
        try:
            agent_response = agent.send(model="gemini-2.5-flash-preview-05-20", messages=st.session_state.messages)
        except:
            agent_response = "Something didn't go right please check the log!"
            web.close()
        response = st.write_stream(agent_response)

    web.close()
    st.session_state.messages.append({"role": "assistant", "content": response})
