import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

class WebDriver:
    def __init__(self):
        self.options = Options()
        self.driver = webdriver.Remote(options=self.options, command_executor="http://localhost:4444")

    def open_website(self, url):
        self.driver.get(url)
        source = self.driver.page_source
        soup = BeautifulSoup(source, 'html.parser')
        # Get rid of i, script, image, css, style
        for tag in soup.find_all(['img', 'style']):
            tag.decompose()
        return soup.body
    
    def close(self):
        self.driver.quit()