from agent import Agent
from web import WebDriver
from dotenv import load_dotenv
import os

"""
Load variables from environment and .env file
"""
load_dotenv()

def main():
    web = WebDriver()
    try:
        agent = Agent(api_key=os.getenv("OPENAI_API_KEY"))

        agent.add_tool(web.open_website)
        agent.add_tool(web.execute_action)
        agent.add_tool(web.wait_for_change)
        agent.add_tool(web.close)

        agent_response = agent.send(
            model="o4-mini",
            prompt="Find in Qwik framework doc how to use $server()"
        )
        for response in agent_response:
            print(response, end="")
        web.close()
    except Exception as e:
        print(f"An error occurred: {e}")
        web.close()


if __name__ == "__main__":
    main()
