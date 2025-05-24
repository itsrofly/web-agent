from bs4 import BeautifulSoup
from markdownify import markdownify
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class WebDriver:
    def __init__(self):
        """
        Initializes the WebDriver with Firefox options.
        """
        self.options = Options()
        self.driver = webdriver.Remote(options=self.options, command_executor="http://localhost:4444")

    def __clean_html(self, html: str) -> str:
        """
        Cleans the HTML by removing unwanted tags and attributes.

        :param html: The HTML source to clean.
        :return: The cleaned markdown source.
        """
        soup = BeautifulSoup(html, "html.parser")

        # Remove hidden elements
        for tag in list(soup.find_all(
            lambda tag: (
                tag.has_attr("hidden") or
                tag.get("type", "").lower() == "hidden" or
                "display:none" in "".join(tag.get("style", "").lower().split()) or
                "visibility:hidden" in "".join(tag.get("style", "").lower().split())
            )
        )):
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
        print(result)
        exit(1)
        return result

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

    def open_website(self, url) -> str:
        """
        Open only the base URL (no path or query parameters).
        If the URL is unknown, use https://google.com to search for the page.

        :param url: The Base URL, e.g. https://google.com
        :return: The full content of the page converted to Markdown,
                 including a section at the end listing all interactive elements
                 (buttons, inputs, links, etc.) with their attributes and inner HTML.
        """
        self.driver.get(url)
        self.__generate_ids()
        source = self.driver.page_source
        self.latest_source = source
        self.latest_url = self.driver.current_url
        response = f"Current Website: {self.latest_url}\n Source:  {self.__clean_html(self.latest_source)}"
        return response

    def execute_action(self, script: str) -> str:
        """
        Execute JavaScript on the page with strict element interaction rules:
        - Use only element IDs to interact with elements (click, fill forms, etc.).
          Other selectors (querySelector, classes, tags, attributes, type, etc.) are not allowed.
        - Always target the site’s search bar by its element ID only.
          Do not rely on generic selectors or assumptions.
        - Use defensive code: always check if elements with given IDs exist before interacting,
          and handle cases where elements are missing or inaccessible.

        :param script: The JavaScript code to execute. Raw, no escapes or formatting, no break lines. Just clean, ready-to-run JavaScript.
        :return: The Markdown page after executing the script.
        """
        self.driver.execute_script(script)
        return self.wait_for_change()

    def wait_for_change(self) -> str:
        """
        Wait for source to change.

        :return: The Markdown page after the change.
        """
        last_source = self.latest_source
        if last_source == self.driver.page_source:
            self.driver.implicitly_wait(3)
            return self.wait_for_change()
        else:
            self.__generate_ids()
            self.latest_source = self.driver.page_source
            self.latest_url = self.driver.current_url
            response = f"Current Website: {self.latest_url}\n Source:  {self.__clean_html(self.latest_source)}"
            return response

    def close(self):
        """
        Closes the website & WebDriver.
        This function is called when the agent is done.
        """
        self.driver.quit()
