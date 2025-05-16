from web import WebDriver
from agent import Agent

def main():
    agent = Agent(
        'http://192.168.1.240:8081/v1/',
        api_key="lm-studio"
    )

    agent_response = agent.send(
        model="qwen3-32b",
        prompt="What is the capital of France?"
    )
    print(f"Agent Response: {agent_response}")

if __name__ == "__main__":
    main()

