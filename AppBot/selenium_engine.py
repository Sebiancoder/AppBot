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

    #all select elements
    select_elements = {}

    #links
    href_links = {}
    
    def __init__(self, verbose: bool = False) -> None:
        
        self.verbose = verbose
        
        self.tools = [
            self.create_tool(
                self.navigate_to_url,
                name="Navigate-to-URL",
                desc="Navigate to the provided URL. URL must be fully complete with http or https.",
                tool_args={"url": str}
            ),
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
                self.get_select_elements,
                name="Get-Select-Elements",
                desc="Get a list of all select elements on the current webpage",
                tool_args={}
            ),
            self.create_tool(
                self.get_select_element_options,
                name="Get-Select-Element-Options",
                desc="Get a list of all options for a select element on the current webpage.",
                tool_args={"select_element": str}
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
            ),
            self.create_tool(
                self.get_all_text,
                name="Get-All-Text",
                desc="Get all text on the current webpage.",
                tool_args={}
            )
        ]

        self.init_driver()

    def init_driver(self) -> None:

        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        
        self.webdriver = webdriver.Chrome(options=chrome_options)
        self.webdriver.implicitly_wait(0)

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

        if self.verbose:

            print("Text Input Fields")
            print(self.text_input_elements)
            print("Buttons")
            print(self.buttons)
            print("HREF Links")
            print(self.href_links)

        return "Successfully navigated to URL: " + url

    def update_elements(self) -> None:

        if self.verbose:

            print("Updating elements...")
        
        self.text_input_elements = self.extract_input_fields()
        self.buttons = self.extract_buttons()
        self.href_links = self.extract_href_links()
        self.select_elements = self.extract_select_elements()

    def format_element_key(self, key: str) -> str:

        return key.strip(" \n\t").replace(" ", "-").replace("\n", "-").replace("\t", "-")
    
    def extract_input_fields(self) -> dict:

        text_input_elements = self.webdriver.find_elements(By.XPATH, "//input[@type='text']")

        element_dict = {self.get_text_input_key(element): element for element in text_input_elements}

        if '' in element_dict:

            del element_dict['']

        return element_dict
    
    def get_text_input_key(self, element) -> str:

        if element.get_attribute("placeholder"):

            key = element.get_attribute("placeholder")

        elif element.get_attribute("name"):

            key = element.get_attribute("name")

        elif element.get_attribute("value"):

            rkey = element.get_attribute("value")

        else:

            key = element.get_attribute("id")

        return self.format_element_key(key)

    def extract_buttons(self) -> dict:

        buttons = self.webdriver.find_elements(By.XPATH, "//button")

        element_dict = {self.get_button_key(button): button for button in buttons}

        if '' in element_dict:

            del element_dict['']

        return element_dict

    def get_button_key(self, button) -> str:

        if button.get_attribute("text"):

            key = button.get_attribute("text")

        else:

            key = button.get_attribute("id")

        return self.format_element_key(key)

    def extract_href_links(self) -> dict:

        href_links = self.webdriver.find_elements(By.XPATH, "//a")

        element_dict = {self.get_link_key(link): link for link in href_links}

        if '' in element_dict:

            del element_dict['']

        return element_dict

    def get_link_key(self, link) -> str:

        if link.get_attribute("text"):

            key = link.get_attribute("text")

        elif link.get_attribute("name"):

            key = link.get_attribute("name")

        elif link.get_attribute("href"):

            key = link.get_attribute("href")

        else:

            key = link.get_attribute("id")

        return self.format_element_key(key)

    def extract_select_elements(self) -> dict:

        if self.verbose:

            print("Extracting select elements...")
        
        select_elements = self.webdriver.find_elements(By.XPATH, "//select")

        if self.verbose:

            print(f"found {len(select_elements)} select elements")

        element_dict = {self.get_select_key(select_element): {"options": self.get_select_options(select_element), "element": select_element} for select_element in select_elements}

        if '' in element_dict:

            del element_dict['']

        return element_dict
    
    def get_select_key(self, select_element) -> str:

        if select_element.get_attribute("name"):

            key = select_element.get_attribute("name")

        elif select_element.get_attribute("id"):

            key = select_element.get_attribute("id")

        if self.verbose:

            print(f"Select key: {key}")

        return self.format_element_key(key)
    
    def get_select_options(self, select_element) -> list:

        options = select_element.find_elements(By.XPATH, "//option")

        if self.verbose:

            print(f"found {len(options)} options")

        return [option.get_attribute("text") for option in options]
    
    #TOOL FUNC: Get Text Input Elements
    def get_text_input_elements(self) -> str:

        if len(self.text_input_elements) == 0:

            return "No text input elements found on the current webpage."
        
        return ", ".join(self.text_input_elements.keys())

    #TOOL FUNC: Get Buttons
    def get_buttons(self) -> str:

        if len(self.buttons) == 0:

            return "No buttons found on the current webpage."
        
        base_instruct = "The following buttons are available. Use the Click-Button tool to click on them."
        
        return base_instruct + "\n" ", ".join(self.buttons.keys())

    #TOOL FUNC: Get HREF Links
    def get_href_links(self) -> str:

        if len(self.href_links) == 0:

            return "No href links found on the current webpage."
        
        base_instruct = "The following HREF links are available. Use the Click-HREF-Link tool to click on them."
        
        return base_instruct + "\n" + ", ".join(self.href_links.keys())

    #TOOL FUNC: Get Select Elements
    def get_select_elements(self) -> str:

        if len(self.select_elements) == 0:

            return "No select elements found on the current webpage."

        return ", ".join(self.select_elements.keys())
    
    #TOOL FUNC: Get Select Element Options
    def get_select_element_options(self, select_element: str) -> list:

        if select_element not in self.select_elements:

            return f"Select element '{select_element}' not found on the current webpage."

        return self.select_elements[select_element]["options"]
    
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

            self.webdriver.execute_script("arguments[0].click();", self.buttons[button])

            self.update_elements()

            return f"Successfully clicked button '{button}'."

        except KeyError:

            return f"Button '{button}' not found on the current webpage."

    #TOOL FUNC:
    def click_href_link(self, link: str) -> None:

        try:

            self.webdriver.execute_script("arguments[0].click();", self.href_links[link])

            self.update_elements()

            print("done updating elements")

            return f"Successfully clicked link '{link}'."

        except KeyError:

            return f"Link '{link}' not found on the current webpage."

    #TOOL FUNC:
    def get_all_text(self) -> str:

        return self.webdriver.page_source

    def set_select_element_option(self, select_element: str, option: str) -> None:

        if select_element not in self.select_elements:

            return f"Select element '{select_element}' not found on the current webpage."
        
        select_element = self.select_elements[select_element]["element"]

        select_element.select_by_visible_text(option)

        self.update_elements()

        return f"Successfully selected option '{option}' for select element '{select_element}'."
    
    