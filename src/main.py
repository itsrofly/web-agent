from agent import Agent
from web import WebDriver


def main():
    web = WebDriver()
    try:
        agent = Agent("http://192.168.1.253:8081/v1/", api_key="lm-studio")

        agent.add_tool(web.open_website)
        agent.add_tool(web.execute_action)
        agent.add_tool(web.wait_for_change)
        agent.add_tool(web.close)

        agent_response = agent.send(
            model="deepseek-r1-distill-llama-70b",
            prompt="Find the music Identidade by LW on youtube.com and play it. Wait for the video to finish and then tell me when it is done.",
        )
        for response in agent_response:
            print(response, end="")
    except Exception as e:
        print(f"An error occurred: {e}")
        web.close()


if __name__ == "__main__":
    main()
