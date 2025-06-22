# Building a Web Agent: How I Taught a Bot to Surf the Web

https://github.com/user-attachments/assets/4c3500d2-6db6-4215-a2cc-3e9fa45694c2

In our daily lives, we constantly interact with the web. We open pages, click on buttons, and type in forms. These actions feel intuitive to us, but for a machine, they are complex tasks. I set out to build a web agent that could automate these interactions, an autonomous bot capable of navigating the digital world.

The key was to break down our complex behaviors into a simple, understandable protocol for a machine. I realized that most of our web interactions boil down to three fundamental actions: **seeing**, **typing**, and **clicking**.

By abstracting these actions, I was able to create a powerful agent that can understand a user's request and execute it on its own. Let's dive into how it works.

## Step 1: Seeing the Web

A human user "sees" a webpage, taking in its layout, text, and interactive elements. For the agent, "seeing" means parsing the raw HTML of a page. However, raw HTML is incredibly noisy, filled with scripts, styles, and tracking pixels that are irrelevant to the task at hand.

To solve this, I built a "vision" system for the agent in the `webAgent/web.py` file.

First, it uses `Selenium` to get the page source. Then, it aggressively cleans it with `BeautifulSoup`:

1.  **Remove the Noise**: It strips out all hidden elements, scripts, and styles.
2.  **Convert to Markdown**: The cleaned HTML body is converted into Markdown using the `markdownify` library. This format is much cleaner and easier for a Large Language Model (LLM) to understand than raw HTML.
3.  **Isolate Interactive Elements**: All interactive elements like `<button>`, `<input>`, and `<textarea>` are extracted and listed separately. This helps the agent quickly identify what it can interact with.

```python web-agent/src/webAgent/web.py#L112-L141
    def __clean_html(self, html: str) -> str:
        """
        Cleans the HTML by removing unwanted tags and attributes.

        :param html: The HTML source to clean.
        :return: The cleaned markdown source.
        """
        soup = BeautifulSoup(html, "html.parser")

        # Remove hidden elements
        for tag in list(
            soup.find_all(
                lambda tag: (
                    tag.has_attr("hidden")
                    or tag.get("type", "").lower() == "hidden"
                    or "display:none" in "".join(tag.get("style", "").lower().split())
                    or "visibility:hidden" in "".join(tag.get("style", "").lower().split())
                )
            )
        ):
            tag.decompose()

        # Get all interactive elements in html only
        interactive_elements = soup.find_all(
            lambda tag: (
                tag.name in ["button", "input", "textarea", "select", "datalist", "area"]
                or tag.has_attr("contenteditable")
            )
        )
        interactive_md = "\n\n## Interactive Elements\n"
        for el in interactive_elements:
            interactive_md += f"\n```html\n{el.prettify()}```\n"
            el.decompose()

        # Convert to markdown
        md = markdownify(soup.body.prettify())
        result = md + interactive_md
        return result
```

To reliably perform actions, the agent needs a consistent way to target elements. Since many HTML elements lack a unique `id`, I wrote a small JavaScript snippet that is executed after every page load to assign a unique, predictable ID to every element on the page.

```python web-agent/src/webAgent/web.py#L143-L154
    def __generate_ids(self):
        self.driver.execute_script(
            """
            const elements = document.body.querySelectorAll('*'); // Select all elements inside body
            let idCounter = 1;

            elements.forEach(el => {
                if (!el.id) {
                    el.id = `custom-id-${idCounter++}`;
                }
            });
            """
        )
```

Now that the agent can "see," it needs to be able to act.

## Step 2: Clicking and Typing

With a clean, Markdown-based view of the page and unique IDs for every element, the agent is ready to perform the other two fundamental actions: clicking and typing.

These are handled by two core functions in the `WebDriver` class:

*   `click_action(element_id: str, next_step: str)`: This function takes the ID of an element, finds it on the page, and clicks it.
*   `type_action(element_id: str, value: str, next_step: str)`: This function finds an input element by its ID and types a given value into it.

```python web-agent/src/webAgent/web.py#L187-L225
    def click_action(self, element_id: str, next_step: str) -> str:
        """
        Clicks an element identified by its ID.

        Args:
            element_id: The ID of the HTML element to click.
            next_step: A descriptive string for the next step after this action.

        Returns:
            The updated source of the page after the
            action and subsequent changes have completed + next_step
        """

        logger.info(f"🔧 1/2 Action: click_action | Id: {element_id}\n")
        try:
            element = self.driver.find_element(By.ID, element_id)
            self.driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", element)
            change = self.wait_for_change(f"🔧 2/2 Action: click_action | Next Step: {next_step}\n")
            return f"Result: \n{change}, Next Step: {next_step}"
        except Exception as e:
            logger.error(f"🔧 2/2 Action: click_action | Error: {e}\n")
            return f"Result: Error clicking element {element_id}: {e}"

    def type_action(self, element_id: str, value: str, next_step: str) -> str:
        """
        Insert a given value into an element identified by its ID.

        Args:
            element_id: The ID of the HTML element to type into.
            value: The string value to be inserted into the element.
            next_step: A descriptive string for the next step after this action.

        Returns:
            The updated source of the page after the
            action and subsequent changes have completed + next_step
        """
        logger.info(f"🔧 1/2 Action: type_action | Id: {element_id} | Value: {value}\n")
        try:
            element = self.driver.find_element(By.ID, element_id)
            self.driver.execute_script(
                "arguments[0].scrollIntoView(true); arguments[0].value = arguments[1];", element, value
            )
            change = self.wait_for_change(f"🔧 2/2 Action: type_action | Next Step: {next_step}\n")
            return f"Result: \n{change}, Next Step: {next_step}"
        except Exception as e:
            logger.error(f"🔧 2/2 Action: type_action | Error: {e}\n")
            return f"Result: Error typing into element {element_id}: {e}"
```

After each action, the agent calls `wait_for_change`, which waits for the page to update, then generates new IDs, and returns the newly "seen" page content. This creates a continuous loop of seeing and acting.

## Step 3: The Brain of the Operation

The `WebDriver` class handles the mechanics, but the `Agent` class in `webAgent/agent.py` is the brain. It uses an LLM (like models from OpenAI) to make decisions.

Here's the workflow:

1.  **The Goal**: The user provides a high-level goal, like "Find the latest news on blog.google.com and subscribe to it with my email."
2.  **Tooling Up**: The agent's functions (`open_website`, `click_action`, `type_action`, and `handle_close`) are exposed to the LLM as "tools" it can use. The `add_tool` method dynamically generates a JSON schema from Python type hints, so the LLM knows exactly what arguments each function expects.
3.  **The Loop**:
    *   The `Agent` sends the user's goal and the current "view" of the webpage to the LLM.
    *   The LLM analyzes the information and decides which tool to use next. For example, it might first call `open_website` with the URL `https://blog.google.com`.
    *   The `Agent` executes the function call, and the `WebDriver` performs the action.
    *   The page updates, and the new, cleaned Markdown content is sent back to the LLM.
    *   The LLM then "sees" the new page and decides the next step, perhaps calling `click_action` on a "Subscribe" button it identified.
    *   This loop of `see -> think -> act` continues until the user's goal is achieved.
4.  **Mission Complete**: Once the task is done, the LLM calls the `handle_close` function, which gracefully shuts down the browser.

## Bringing It All Together

The entire experience is wrapped in a simple Streamlit interface defined in `webAgent/main.py`. This allows you to choose your browser, provide a task, and watch the agent work its magic in real-time.

By reducing the complexity of web browsing to a simple `see, type, click` protocol, I was able to build an autonomous agent that can intelligently navigate the web. It's a powerful demonstration of how combining the raw capabilities of `Selenium` with the reasoning power of modern LLMs can create truly smart and useful automation.
