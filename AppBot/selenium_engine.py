from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException
from langchain.agents import tool
from langchain.tools import StructuredTool
from langchain.pydantic_v1 import Field, create_model
import json

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

    #file upload elements
    file_upload_elements = {}
    
    def __init__(self, verbose: bool = False, file_upload_source_path: str = None) -> None:
        
        self.verbose = verbose

        self.file_upload_source_path = file_upload_source_path
        
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
                self.get_file_upload_elements,
                name="Get-File-Upload-Elements",
                desc="Get a list of all file upload elements on the current webpage.",
                tool_args={}
            ),
            self.create_tool(
                self.enter_text,
                name="Enter-Text",
                desc="Enter text into a text input field on the current webpage.",
                tool_args={"text_input_field": str, "text": str}
            ),
            self.create_tool(
                self.bulk_enter_text,
                name="Bulk-Enter-Text",
                desc="Enter text into multiple text input fields on the current webpage. Provide a json string with the text input field as the key and the text as the value for every text input field you want to fill out.",
                tool_args={"text_input_fields": str}
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
            ),
            self.create_tool(
                self.set_select_element_option,
                name="Set-Select-Element-Option",
                desc="Set an option for a select element on the current webpage.",
                tool_args={"select_element": str, "option": str}
            ),
            self.create_tool(
                self.upload_file,
                name="Upload-File",
                desc="Upload a file to a file upload element on the current webpage. Set the document to either `resume` or `transcript`.",
                tool_args={"file_upload_element": str, "document": str}
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

        return "Successfully navigated to URL: " + url

    def update_elements(self) -> None:
        
        self.text_input_elements = self.extract_input_fields()
        self.buttons = self.extract_buttons()
        self.href_links = self.extract_href_links()
        self.select_elements = self.extract_select_elements()
        self.file_upload_elements = self.extract_file_uploads()

    def format_element_key(self, key: str) -> str:

        return key.strip(" \n\t").replace(" ", "-").replace("\n", "-").replace("\t", "-")
    
    def extract_input_fields(self) -> dict:

        text_input_elements = self.webdriver.find_elements(By.XPATH, "//input[@type='text']")

        #filter non-displayed elements
        text_input_elements = [element for element in text_input_elements if element.is_displayed()]

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

        #filter non-displayed elements
        buttons = [button for button in buttons if button.is_displayed()]

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

        #filter non-displayed elements
        href_links = [link for link in href_links if link.is_displayed()]
        
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
        
        select_elements = [Select(webElement) for webElement in self.webdriver.find_elements(By.XPATH, "//select")]

        #filter non-displayed elements
        select_elements = [select_element for select_element in select_elements if select_element._el.is_displayed()]

        element_dict = {
            self.get_select_key(select_element): {"options": [selElem.get_attribute("value") for selElem in select_element.options], "element": select_element} for select_element in select_elements
            }

        if '' in element_dict:

            del element_dict['']

        return element_dict
    
    def get_select_key(self, select_element: Select) -> str:

        select_webElement = select_element._el
        
        if select_webElement.get_attribute("name"):

            key = select_webElement.get_attribute("name")

        elif select_webElement.get_attribute("id"):

            key = select_webElement.get_attribute("id")

        return self.format_element_key(key)
    
    def extract_file_uploads(self) -> dict:

        file_uploads = self.webdriver.find_elements(By.XPATH, "//input[@type='file']")

        #filter non-displayed elements
        file_uploads = [file_upload for file_upload in file_uploads if file_upload.is_displayed()]

        element_dict = {self.get_file_upload_key(file_upload): file_upload for file_upload in file_uploads}

        if '' in element_dict:

            del element_dict['']

        return element_dict

    def get_file_upload_key(self, file_upload) -> str:

        if file_upload.get_attribute("name"):

            key = file_upload.get_attribute("name")

        elif file_upload.get_attribute("id"):

            key = file_upload.get_attribute("id")

        return self.format_element_key(key)
    
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

        base_instruct = "The following select elements are available. Use the Get-Select-Element-Options tool to get the options for each select element. The Set-Select-Element-Option tool can be used to select an option for a select element."
        
        return base_instruct + "\n" + ", ".join(self.select_elements.keys())
    
    #TOOL FUNC: Get Select Element Options
    def get_select_element_options(self, select_element: str) -> list:

        if select_element not in self.select_elements:

            return f"Select element '{select_element}' not found on the current webpage."

        return self.select_elements[select_element]["options"]
    
    #TOOL FUNC: Get File Upload elements
    def get_file_upload_elements(self) -> str:

        if len(self.file_upload_elements) == 0:

            return "No file upload elements found on the current webpage."
        
        base_instruct = "The following file upload elements are available. Use the Upload-File tool to upload a file to them."
        
        return base_instruct + "\n" + ", ".join(self.file_uploads.keys())
    
    #TOOL FUNC: Enter Text
    def enter_text(self, text_input_field: str, text: str) -> None:

        try:

            self.text_input_elements[text_input_field].send_keys(text)

            self.update_elements()

            return f"Successfully entered text '{text}' into text input field '{text_input_field}'."

        except KeyError:

            return f"Text input field '{text_input_field}' not found on the current webpage."

    #TOOL FUNC: Bulk Enter Text
    def bulk_enter_text(self, text_input_fields: str) -> None:

        text_input_fields_dict = json.loads(text_input_fields)

        bulk_enter_successes = {}

        for text_input_field, text in text_input_fields_dict.items():

            enter_text_result = self.enter_text(text_input_field, text)

            bulk_enter_successes[text_input_field] = enter_text_result

        self.update_elements()

        if all([result.split(" ")[0] == "Successfully" for result in bulk_enter_successes.values()]):

            return "Successfully entered text into all text input fields."

        else:

            base_instruct = "The following text input fields were successfully filled out: \n"

            return base_instruct + "\n".join([f"{key}: {value}" for key, value in bulk_enter_successes.items() if value.split(" ")[0] == "Successfully"])
    
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

            return f"Successfully clicked link '{link}'."

        except KeyError:

            return f"Link '{link}' not found on the current webpage."

    #TOOL FUNC:
    def get_all_text(self) -> str:

        return self.webdriver.page_source

    #TOOL FUNC:
    def set_select_element_option(self, select_element: str, option: str) -> None:

        if select_element not in self.select_elements:

            return f"Select element '{select_element}' not found on the current webpage."
        
        select_element_obj = self.select_elements[select_element]["element"]

        try:
            
            select_element_obj.select_by_value(option)

        except NoSuchElementException:

            return f"Option '{option}' not found for select element '{select_element}'."

        self.update_elements()

        return f"Successfully selected option '{option}' for select element '{select_element}'."

    #TOOL FUNC: Upload File
    def upload_file(self, file_upload_element: str, document: str) -> None:

        if file_upload_element not in self.file_uploads:

            return f"File upload element '{file_upload_element}' not found on the current webpage."

        if document == "resume":

            file_path = self.file_upload_source_path + "resume.pdf"

        elif document == "transcript":

            file_path = self.file_upload_source_path + "transcript.pdf"

        else:

            return "Document must be either 'resume' or 'transcript'."

        try:

            self.file_uploads[file_upload_element].send_keys(file_path)

            self.update_elements()

            return f"Successfully uploaded file '{document}' to file upload element '{file_upload_element}'."

        except Exception as e:

            return f"Error uploading file '{document}' to file upload element '{file_upload_element}'. Error: {e}"
    
    