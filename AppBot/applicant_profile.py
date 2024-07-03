import json
from langchain.agents import tool
from langchain.tools import StructuredTool
from langchain.pydantic_v1 import Field, create_model

class ApplicantProfile:

    tools = []
    
    def __init__(self, applicantID: str):

        self.applicantID = applicantID
        self.applicant_json = self.load_applicant_json()

        self.tools = [
            self.create_tool(
                self.get_applicant_json,
                name="Get-Applicant-JSON",
                desc="Get information about the current applicant in json format.",
                tool_args={}
            )
        ]

    def get_tools(self) -> list:

        return self.tools

    def load_applicant_json(self) -> dict:

        with open(f"../applicants/{self.applicantID}/{self.applicantID}.json", "r") as f:

            return json.load(f)

    def create_tool(self, tool_function, name: str = None, desc: str = None, tool_args: dict = None) -> StructuredTool:

        pydanticified_args = {description:(arg_type, Field(description=description)) for (description, arg_type) in tool_args.items()}
        
        return StructuredTool.from_function(
            func=tool_function,
            name=name,
            description=desc,
            args_schema=create_model("Model", **pydanticified_args)
        )

    #TOOL FUNC
    def get_applicant_json(self) -> dict:

        return str(self.applicant_json)