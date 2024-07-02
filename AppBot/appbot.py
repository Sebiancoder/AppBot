import langchain
import langchain.agents as LangChainAgents
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community import get_openai_callback
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from extendedchatopenai import ExtendedChatOpenAI
from selenium_engine import SeleniumEngine
from applicant_profile import ApplicantProfile
import argparse

class AppBot:

    def __init__(self, verbose: bool = False, applicant_id: str = None):

        self.applicant_id = applicant_id
        
        #LLM
        self.llm = ExtendedChatOpenAI(
            model="gpt-3.5-turbo", 
            api_key_filename="openai_api_key.txt", 
            temperature=0
        )

        self.agent_prompt = ChatPromptTemplate.from_messages([
            ("system", 
            """
                You are a powerful assistant that has been tasked with filling out job applications. 
                You have access to a web browser and can navigate to any website. 
                You can type and click on elements, but you must only interact with elements that you have determined to exist using the tools available to you.
                You have access to the applicant's profile information via a tool.
                Make sure you use the right tool for the job. For example, to click a link, make sure you use the link clicking tool instead of the button clicking tool.
            """),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        #selenium agent
        self.selenium_engine = SeleniumEngine(verbose=verbose)
        
        #applicant profile
        self.applicant_profile = ApplicantProfile(applicantID=self.applicant_id)

        all_tools = self.selenium_engine.get_tools() + self.applicant_profile.get_tools()

        self.agent_llm = self.llm.bind_tools(all_tools)

        self.agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                    x["intermediate_steps"]
                ),
            }
            | self.agent_prompt
            | self.agent_llm
            | OpenAIToolsAgentOutputParser()
        )

        self.agent_executor = LangChainAgents.AgentExecutor(agent=self.agent, tools=all_tools, verbose=verbose)

    def invoke_agent(self, input_text: str) -> None:

        with get_openai_callback() as openai_callback:

            self.agent_executor.invoke({"input": input_text})
        
            print("Agent Execution Complete.")
            print("Total Tokens Used: ", openai_callback.total_tokens)
            print("Prompt Tokens Used: ", openai_callback.prompt_tokens)
            print("Completion Tokens Used: ", openai_callback.completion_tokens)
            print("Total Cost: ", openai_callback.total_cost)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--text", help="Some text")
    args = parser.parse_args()

    if args.text:

        input_text = args.text

    else:

        input_text = "Use the tools available to you to fill out job applications."

    appbot = AppBot(verbose=True, applicant_id="test")
    appbot.invoke_agent(input_text)