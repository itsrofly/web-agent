from web import WebDriver


def main():
    # Initialize the WebDriver
    web_driver = WebDriver()
    print(web_driver.open_website("https://www.google.com"))


if __name__ == "__main__":
    main()

