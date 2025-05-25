from bs4 import BeautifulSoup
from loguru import logger
from markdownify import markdownify
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


class WebDriver:
    def __init__(self):
        """
        Initializes the WebDriver with Firefox options.
        """
        self.options = Options()
        self.driver = webdriver.Remote(options=self.options, command_executor="http://localhost:4444")
        self.latest_source = self.driver.page_source

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
        Open only the base URL (no path or query parameters).
        If the URL is unknown, use https://google.com to search for the page.

         Args:
            url: The target base URL (e.g., "https://google.com")
            next_step: A descriptive string for the next step and expected outcome.

         Returns:
            The updated source of the page after the
            action and subsequent changes have completed + next_step
        """

        self.driver.get(url)
        logger.info("🔧 1/2 Action: open_website")
        change = self.wait_for_change(f"🔧 2/2 Action: open_website | Next Step: {next_step}")
        return f"Result: \n{change}, Next Step: {next_step}"

    def click_action(self, element_id: str, next_step: str) -> str:
        """
        Clicks an element identified by its ID.

        Args:
            element_id: The ID of the HTML element to click.
            next_step: A descriptive string for the next step and expected outcome.

        Returns:
            The updated source of the page after the
            action and subsequent changes have completed + next_step
        """

        element = self.driver.find_element(By.ID, element_id)
        ActionChains(self.driver).move_to_element(element).click().perform()
        logger.info("🔧 1/2 Action: click_action")
        change = self.wait_for_change(f"🔧 2/2 Action: click_action | Next Step: {next_step}")
        return f"Result: \n{change}, Next Step: {next_step}"

    def type_action(self, element_id: str, value: str, next_step: str) -> str:
        """
        Insert a given value into an element identified by its ID.

        Args:
            element_id: The ID of the HTML element to type into.
            value: The string value to be inserted into the element.
            next_step: A descriptive string for the next step and expected outcome.

        Returns:
            The updated source of the page after the
            action and subsequent changes have completed + next_step
        """

        element = self.driver.find_element(By.ID, element_id)
        ActionChains(self.driver).move_to_element(element).send_keys(value).perform()
        logger.info("🔧 1/2 Action: type_action")
        change = self.wait_for_change(f"🔧 2/2 Action: type_action | Next Step: {next_step}")
        return f"Result: \n{change}, Next Step: {next_step}"

    def wait_for_change(self, log: str = None) -> str:
        """
        Wait for source to change.

        :return: The Markdown page after the change.
        """
        last_source = self.latest_source
        if last_source == self.driver.page_source:
            self.driver.implicitly_wait(3)
            return self.wait_for_change()
        else:
            if log:
                logger.info(log)

            self.__generate_ids()
            self.latest_source = self.driver.page_source
            self.latest_url = self.driver.current_url
            response = f"Current Website: {self.latest_url}\nSource: {self.__clean_html(self.latest_source)}"
            return response

    def close(self):
        """
        Closes the website & WebDriver.
        This function is called when the agent is done.
        """
        logger.info("🔧 Action: close | Closing driver...")
        self.driver.quit()
