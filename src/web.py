from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

class WebDriver:
    def __init__(self):
        """
        Initializes the WebDriver with Firefox options.
        """
        self.options = Options()
        self.driver = webdriver.Remote(options=self.options, command_executor="http://selenium:4444")

    def __clean_html__(self, html: str) -> str:
        """
        Cleans the HTML by removing unwanted tags and attributes.
        """
        soup = BeautifulSoup(html, 'html.parser')
        # Get rid of i, script, image, css, style, script, link
        for tag in soup.find_all(['style', 'script', 'link']):
            tag.decompose()
        return soup.body.prettify()


    def open_website(self, url):
        """
        Opens a website and returns the cleaned HTML source.
        """
        self.driver.get(url)
        source = self.driver.page_source
        return self.__clean_html__(source)

    def close(self):
        """
        Closes the WebDriver.
        """
        self.driver.quit()