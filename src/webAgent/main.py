import os

import streamlit as st

from webAgent import Agent, WebDriver

agent = Agent(api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL"))

st.title("Web Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if "tool_calls" in message:
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# I want to receive news from blog.google, subscribe, my email is rofly@gmail.com

webdriver_options = ["Firefox", "Chrome", "Edge", "Remote"]
selected_webdriver = st.sidebar.selectbox("Choose your WebDriver:", webdriver_options, index=0)

if "selected_webdriver" not in st.session_state or st.session_state.selected_webdriver != selected_webdriver:
    st.session_state.selected_webdriver = selected_webdriver

executable_path_input = st.sidebar.text_input(
    "Driver Executable Path (optional):", key="executable_path", placeholder="/path/to/your/geckodriver_or_chromedriver"
)


def handle_close() -> str:
    """
    Closes the website & WebDriver.
    This function is called when the agent is done.
    """
    if "web" in st.session_state:
        st.session_state.web.close()
        del st.session_state["web"]


if prompt := st.chat_input("What is up?"):
    with st.spinner("Wait for it...", show_time=True):
        if "web" not in st.session_state:
            st.session_state.web = WebDriver(
                browser_name=st.session_state.selected_webdriver,
                executable_path=st.session_state.executable_path if st.session_state.executable_path else None,
            )
        agent.add_tool(st.session_state.web.open_website)
        agent.add_tool(st.session_state.web.click_action)
        agent.add_tool(st.session_state.web.type_action)
        agent.add_tool(handle_close)

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        agent_response = agent.send(model=os.getenv("MODEL_NAME"), messages=st.session_state.messages)
        response = st.write_stream(agent_response)
    st.session_state.messages.append({"role": "assistant", "content": response})
