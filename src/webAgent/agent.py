import inspect
import json
import re
from typing import Callable, Dict, Generator, List, Literal, get_args, get_origin

from openai import OpenAI


class Agent:
    _tools = {}

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1/"):
        """
        Initialize the Agent with the OpenAI API key and base URL.

        :param base_url: The base URL for the OpenAI API.
        :param api_key: The API key for authentication.
        """
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def send(
        self,
        model,
        prompt: str = None,
        messages: list[str] = [],
        think: Literal["/no_think", "/think"] = "/no_think",
        system_prompts: list[str] = [
            """
        You are a web assistant and your job is to perform tasks set by the user on your own, interacting with pages using JavaScript.
        Cite all sources you find clearly by site name and link.
        Always check the source information outside the interactive elements, as the action might have already been completed even if the interactive elements are still present.
        After completing the tasks, close WebDriver and reply to the user
        """,
        ],
    ) -> Generator:
        """
        Send a prompt to the model and return the response.

        :param model: The model to use for the request.
        :param prompt: The prompt to send to the model.
        :return: The response from the model.
        """
        if prompt:
            messages.append({"role": "user", "content": prompt})

        for i, sprompt in enumerate(system_prompts):
            if i < len(system_prompts) - 1:
                system_prompts[i] = re.sub(r"%%.*?%%", "...", sprompt)
            else:
                system_prompts[i] = sprompt

        stream = self.client.chat.completions.create(
            model=model,
            messages=[
                *[{"role": "system", "content": message} for message in system_prompts],
                {"role": "user", "content": think},
                *messages,
            ],
            tools=[
                {
                    "type": tool["type"],
                    tool["type"]: {
                        "name": name,
                        "description": tool["description"],
                        "parameters": tool["parameters"],
                        "strict": tool["strict"],
                    },
                }
                for name, tool in self._tools.items()
            ],
            tool_choice="auto",
            temperature=0.5,
            stream=True,
        )

        final_tool_calls = {}
        for chunk in stream:
            chunk.choices[0]
            # Check if the chunk contains a tool call
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
            elif chunk.choices[0].delta.tool_calls:
                # Store all tools
                for tool_call in chunk.choices[0].delta.tool_calls or []:
                    index = tool_call.index
                    if index not in final_tool_calls:
                        final_tool_calls[index] = tool_call
                    if final_tool_calls[index].function.arguments != tool_call.function.arguments:
                        # Prevent duplicate arguments using gemini models
                        final_tool_calls[index].function.arguments += tool_call.function.arguments

        for index, tool_call in final_tool_calls.items():
            # Call the function with the arguments
            tool = self._tools[tool_call.function.name]
            args = json.loads(tool_call.function.arguments)
            result = tool["function"](**args)
            messages.append({"role": "assistant", "content": [], "tool_calls": [tool_call]})
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(result)})
            # Send the result back to the model
            yield " "
            for result in self.send(
                model=model,
                prompt=prompt,
                messages=messages,
                system_prompts=system_prompts,
            ):
                yield result

    def add_tool(self, func: Callable[..., str], strict: bool = False) -> None:
        """
        Add a tool to the agent.

        :param func: The function to add as a tool.
        :param strict: Whether to use strict mode for the tool.
        """
        name = func.__name__
        description = inspect.getdoc(func)
        if description is None:
            description = "No description provided."
        parameters = self.__get_tool_parameters(func, strict)
        self._tools[name] = {
            "type": "function",
            "name": name,
            "description": description,
            "parameters": parameters,
            "strict": strict,
            "function": func,
        }

    def __get_tool_parameters(self, func: Callable[..., str], strict: bool) -> dict:
        """
        Dynamically creates a JSON schema for function parameters based on type hints.

        :param func: The function to get the parameters from.
        :return: A dictionary representing the JSON schema of the parameters.
        """
        sig = inspect.signature(func)
        properties = {}
        required = []

        for name, param in sig.parameters.items():
            param_type = param.annotation
            schema = {}

            if param.annotation == inspect.Parameter.empty:
                # Default to 'string' for parameters without type hints
                schema["type"] = "string"
            elif hasattr(param_type, "__origin__") and param_type.__origin__ == Literal:
                schema["type"] = "string"  # Literals are often strings
                schema["enum"] = list(param_type.__args__)
            elif param_type is str:
                schema["type"] = "string"
            elif param_type is int:
                schema["type"] = "integer"
            elif param_type is float:
                schema["type"] = "number"
            elif param_type is bool:
                schema["type"] = "boolean"
            elif get_origin(param_type) in [list, List]:  # Handle list types
                schema["type"] = "array"
                # Process the type of items in the list
                if get_args(param_type):
                    item_type = get_args(param_type)[0]
                    # For now, let's handle simple types.
                    if item_type is str:
                        schema["items"] = {"type": "string"}
                    elif item_type is int:
                        schema["items"] = {"type": "integer"}
                    elif item_type is float:
                        schema["items"] = {"type": "number"}
                    elif item_type is bool:
                        schema["items"] = {"type": "boolean"}
                    # Handle List[Dict]
                    elif get_origin(item_type) in [dict, Dict]:
                        schema["items"] = {
                            "type": "object",
                            "additionalProperties": not strict,
                        }
                else:
                    schema["items"] = {"type": "string"}  # Default for list with no specified item type
            elif get_origin(param_type) in [dict, Dict]:  # Handle dict types
                schema["type"] = "object"
                # For a generic Dict, OpenAI functions usually expect 'object' without specific properties
                # For a truly generic dictionary, you might use additionalProperties.
                # Allows any properties
                schema["additionalProperties"] = not strict
            else:
                # For any other unhandled complex types, or if strictness requires it,
                # one might raise an error or log a warning.
                # For now, we'll skip assigning a type, or could default to string if absolutely necessary.
                pass

            properties[name] = schema
            if param.default == inspect.Parameter.empty:
                required.append(name)
        parameters_schema = {"type": "object", "properties": properties}
        if required:
            parameters_schema["required"] = required
        return parameters_schema
