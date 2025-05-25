from typing import Literal

from bs4 import BeautifulSoup
from loguru import logger
from markdownify import markdownify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.safari.service import Service as SafariService


class WebDriver:
    def __init__(
        self,
        browser_name: Literal["Remote", "Firefox", "Chrome", "Edge", "Safari"] = "Firefox",
        command_executor: str = "http://localhost:4444",
        headless: bool = False,
        executable_path: str = None,
    ):
        """
        Manages a Selenium WebDriver instance for browser automation.

        This class provides an interface to control a web browser, supporting
        different browser types (Firefox, Chrome, Edge, and Remote via Selenium Grid).
        It allows for actions like opening websites, clicking elements, typing into fields,
        and retrieving page source, which is then cleaned and converted to Markdown.

        Args:
            browser_name: The name of the browser to use.
                Defaults to "Firefox".
                Supported values: "Remote", "Firefox", "Chrome", "Edge", "Safari".
            command_executor: The URL of the Selenium Grid hub or standalone server
                if `browser_name` is "Remote". Defaults to "http://localhost:4444".
            headless: If True, the browser will run in headless mode (no GUI).
                Defaults to False.
            executable_path: Optional path to the browser driver executable.
                If not provided, Selenium will try to find it in the system PATH.
                Defaults to None.

        Raises:
            ValueError: If an unsupported `browser_name` is provided.
        """
        self.driver = None
        if browser_name == "Firefox":
            options = FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            service = FirefoxService(executable_path=executable_path) if executable_path else None
            self.driver = webdriver.Firefox(options=options, service=service)
        elif browser_name == "Chrome":
            options = ChromeOptions()
            if headless:
                options.add_argument("--headless")
            service = ChromeService(executable_path=executable_path) if executable_path else None
            self.driver = webdriver.Chrome(options=options, service=service)
        elif browser_name == "Edge":
            options = EdgeOptions()
            if headless:
                options.add_argument("--headless")
            service = EdgeService(executable_path=executable_path) if executable_path else None
            self.driver = webdriver.Edge(options=options, service=service)
        elif browser_name == "Safari":
            options = SafariOptions()
            service = SafariService(executable_path=executable_path) if executable_path else None
            self.driver = webdriver.Safari(options=options, service=service)
        elif browser_name == "Remote":
            options = FirefoxOptions()
            self.driver = webdriver.Remote(command_executor=command_executor, options=options)
        else:
            raise ValueError(f"Unsupported browser: {browser_name}. Choose from 'Firefox', 'Chrome', 'Edge', 'Safari', 'Remote'.")
        if self.driver:
            self.latest_source = self.driver.page_source
        else:
            self.latest_source = ""

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

    def open_website(self, url: str, next_step: str) -> str:
        """
        If the URL is unknown, use https://www.google.com/search?q={value} to search for the page.

         Args:
            url: The target URL (e.g., "https://google.com")
            next_step: A descriptive string for the next step after this action.

         Returns:
            The updated source of the page after the
            action and subsequent changes have completed + next_step
        """
        logger.info(f"🔧 1/2 Action: open_website | Url: {url}")
        self.driver.get(url)
        change = self.wait_for_change(f"🔧 2/2 Action: open_website | Next Step: {next_step}")
        return f"Result: \n{change}, Next Step: {next_step}"

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

        logger.info(f"🔧 1/2 Action: click_action | Id: {element_id}")
        element = self.driver.find_element(By.ID, element_id)
        if not element:
            return f"Result: Element id {element_id} not found!"
        element = self.driver.find_element(By.ID, element_id)
        self.driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", element)
        change = self.wait_for_change(f"🔧 2/2 Action: click_action | Next Step: {next_step}")
        return f"Result: \n{change}, Next Step: {next_step}"

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
        logger.info(f"🔧 1/2 Action: type_action | Id: {element_id} | Value: {value}")
        element = self.driver.find_element(By.ID, element_id)
        if not element:
            return f"Result: Element id {element_id} not found!"
        self.driver.execute_script(
            "arguments[0].scrollIntoView(true); arguments[0].value = arguments[1];", element, value
        )
        change = self.wait_for_change(f"🔧 2/2 Action: type_action | Next Step: {next_step}")
        return f"Result: \n{change}, Next Step: {next_step}"

    def wait_for_change(self, log: str = None, counter=0) -> str:
        """
        Wait for source to change.

        :return: The Markdown page after the change.
        """
        last_source = self.latest_source
        if last_source == self.driver.page_source and counter < 3:
            self.driver.implicitly_wait(3)
            return self.wait_for_change(log, counter + 1)
        else:
            if log:
                logger.success(log)

            self.__generate_ids()
            self.latest_source = self.driver.page_source
            self.latest_url = self.driver.current_url
            response = f"Current Website: {self.latest_url}\nSource: {self.__clean_html(self.latest_source)}"
            return response

    def close(self) -> str:
        """
        Closes the website & WebDriver.
        This function is called when the agent is done.
        """
        logger.info("🔧 Action: close | Closing driver...")
        self.driver.quit()
        return "Web driver is cloed!, No further actions can be taken until the user's next message"
