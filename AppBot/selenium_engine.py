from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from langchain.agents import tool
from langchain.tools import StructuredTool
from langchain.pydantic_v1 import Field, create_model

class SeleniumEngine():

    #tools
    tools = []
    
    #all input elements
    text_input_elements = {}

    #all clickable elements
    buttons = {}

    #links
    href_links = {}
    
    def __init__(self) -> None:
        
        self.tools = [
            self.create_tool(
                self.navigate_to_url,
                name="Navigate-to-URL",
                desc="Navigate to the provided URL. URL must be fully complete with http or https.",
                tool_args={"url": str}),
            self.create_tool(
                self.get_text_input_elements,
                name="Get-Text-Input-Elements",
                desc="Get a list of all text input elements on the current webpage.",
                tool_args={}
            ),
            self.create_tool(
                self.get_buttons,
                name="Get-Buttons",
                desc="Get a list of all buttons on the current webpage.",
                tool_args={}
            ),
            self.create_tool(
                self.get_href_links,
                name="Get-HREF-Links",
                desc="Get a list of all href links on the current webpage.",
                tool_args={}
            ),
            self.create_tool(
                self.enter_text,
                name="Enter-Text",
                desc="Enter text into a text input field on the current webpage.",
                tool_args={"text_input_field": str, "text": str}
            ),
            self.create_tool(
                self.click_button,
                name="Click-Button",
                desc="Click a button on the current webpage.",
                tool_args={"button": str}
            ),
            self.create_tool(
                self.click_href_link,
                name="Click-HREF-Link",
                desc="Click a href link on the current webpage.",
                tool_args={"link": str}
            )
        ]

    def init_driver(self) -> None:

        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        
        self.webdriver = webdriver.Chrome(options=chrome_options)

    def create_tool(self, tool_function, name: str = None, desc: str = None, tool_args: dict = None) -> StructuredTool:

        pydanticified_args = {description:(arg_type, Field(description=description)) for (description, arg_type) in tool_args.items()}
        
        return StructuredTool.from_function(
            func=tool_function,
            name=name,
            description=desc,
            args_schema=create_model("Model", **pydanticified_args)
        )

    def get_tools(self) -> list[StructuredTool]:

        return self.tools

    #TOOL FUNC: Navigate to URL
    def navigate_to_url(self, url: str) -> None:
        """Navigate to the provided URL. URL must be fully complete with http or https."""
        
        self.webdriver.get(url)

        self.update_elements()

        print(self.text_input_elements.keys())
        print(self.buttons.keys())
        print(self.href_links.keys())

        return "Successfully navigated to URL: " + url

    def update_elements(self) -> None:

        self.text_input_elements = self.extract_input_fields()
        self.buttons = self.extract_buttons()
        self.href_links = self.extract_href_links()

    def extract_input_fields(self) -> dict:

        text_input_elements = self.webdriver.find_elements(By.XPATH, "//input[@type='text']")

        return {self.get_text_input_key(element): element for element in text_input_elements}

    def get_text_input_key(self, element) -> str:

        if element.get_attribute("placeholder"):

            return element.get_attribute("placeholder")

        elif element.get_attribute("name"):

            return element.get_attribute("name")

        elif element.get_attribute("value"):

            return element.get_attribute("value")

        else:

            return element.get_attribute("id")

    def extract_buttons(self) -> dict:

        buttons = self.webdriver.find_elements(By.XPATH, "//button")

        return {self.get_button_key(button): button for button in buttons}

    def get_button_key(self, button) -> str:

        if button.get_attribute("text"):

            return button.get_attribute("text")

        else:

            return button.get_attribute("id")

    def extract_href_links(self) -> dict:

        href_links = self.webdriver.find_elements(By.XPATH, "//a")

        return {self.get_link_key(link): link for link in href_links}

    def get_link_key(self, link) -> str:

        if link.get_attribute("text"):

            return link.get_attribute("text")

        elif link.get_attribute("name"):

            return link.get_attribute("name")

        elif link.get_attribute("href"):

            return link.get_attribute("href")

        else:

            return link.get_attribute("id")

    #TOOL FUNC: Get Text Input Elements
    def get_text_input_elements(self) -> str:

        if len(self.text_input_elements) == 0:

            return "No text input elements found on the current webpage."
        
        return ", ".join(self.text_input_elements.keys())

    #TOOL FUNC: Get Buttons
    def get_buttons(self) -> str:

        if len(self.buttons) == 0:

            return "No buttons found on the current webpage."
        
        return ", ".join(self.buttons.keys())

    #TOOL FUNC: Get HREF Links
    def get_href_links(self) -> str:

        if len(self.href_links) == 0:

            return "No href links found on the current webpage."
        
        return ", ".join(self.href_links.keys())

    #TOOL FUNC: Enter Text
    def enter_text(self, text_input_field: str, text: str) -> None:

        try:

            self.text_input_elements[text_input_field].send_keys(text)

            self.update_elements()

            return f"Successfully entered text '{text}' into text input field '{text_input_field}'."

        except KeyError:

            return f"Text input field '{text_input_field}' not found on the current webpage."

    #TOOL FUNC: Click Button
    def click_button(self, button: str) -> None:

        try:

            self.buttons[button].click()

            self.update_elements()

            return f"Successfully clicked button '{button}'."

        except KeyError:

            return f"Button '{button}' not found on the current webpage."

    def click_href_link(self, link: str) -> None:

        try:

            self.href_links[link].click()

            self.update_elements()

            return f"Successfully clicked link '{link}'."

        except KeyError:

            return f"Link '{link}' not found on the current webpage."
    