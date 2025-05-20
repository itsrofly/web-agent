from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

class WebDriver:
    def __init__(self):
        """
        Initializes the WebDriver with Firefox options.
        """
        self.options = Options()
        self.driver = webdriver.Remote(
            options=self.options, command_executor="http://localhost:4444"
        )

    def __clean_html__(self, html: str) -> str:
        """
        Cleans the HTML by removing unwanted tags and attributes.

        :param html: The HTML source to clean.
        :return: The cleaned HTML source.
        """
        soup = BeautifulSoup(html, "html.parser")
        # Get rid of i, script, image, css, style, script, link
        for tag in soup.find_all(["style", "script", "link", "svg", "path"]):
            tag.decompose()
        return soup.body.prettify()

    def open_website(self, url) -> str:
        """
        Opens a website and returns the cleaned HTML source.
        If you don't know the URL, use google.com and search for the page.
        It is highly encouraged that you use the links that are in the source.

        :param url: The URL of the website to open.
        :return: The cleaned HTML source of the website.
        """
        self.driver.get(url)
        source = self.driver.page_source
        self.latest_source = source
        response = f"Current Website: {self.driver.current_url}\n Source:  {self.__clean_html__(source)}"
        return response

    def execute_action(self, script: str) -> str:
        """
        Inject JavaScript code into the page and execute it.
        Non-defensive & Assumptive Code are not allowed.

        :param script: The JavaScript code to execute.
        :return: The cleaned HTML source of the page after executing the script.
        """
        self.driver.execute_script(script)
        return self.wait_for_change()

    def wait_for_change(self) -> str:
        """
        Wait for source to change.
        This function is called when the agent is waiting for a change in the source.

        :return: The cleaned HTML source of the page after the change.
        """
        last_source = self.latest_source
        if last_source == self.driver.page_source:
            self.driver.implicitly_wait(3)
            return self.wait_for_change()
        else:
            return self.open_website(self.driver.current_url)

    def close(self):
        """
        Closes the website & WebDriver.
        This function is called when the agent is done.
        """
        self.driver.quit()
