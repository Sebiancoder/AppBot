import langchain
import langchain.agents as LangChainAgents
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from extendedchatopenai import ExtendedChatOpenAI
from selenium_engine import SeleniumEngine
import argparse

class AppBot:

    def __init__(self, verbose: bool = False):

        #LLM
        self.llm = ExtendedChatOpenAI(
            model="gpt-4", 
            api_key_filename="openai_api_key.txt", 
            temperature=0
        )

        self.agent_prompt = ChatPromptTemplate.from_messages([
            ("system", 
            """
                You are a powerful assistant that has been tasked with filling out job applications. 
                You have access to a web browser and can navigate to any website. 
                You can also type and click on elements, but you must only interact with elements that you have determined to exist using the tools available to you.
            """),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        self.selenium_engine = SeleniumEngine()
        self.selenium_engine.init_driver()

        self.agent_llm = self.llm.bind_tools(self.selenium_engine.get_tools())

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

        self.agent_executor = LangChainAgents.AgentExecutor(agent=self.agent, tools=self.selenium_engine.get_tools(), verbose=verbose)

    def invoke_agent(self, input_text: str) -> None:

        self.agent_executor.invoke({"input": input_text})

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--text", help="Some text")
    args = parser.parse_args()

    if args.text:

        input_text = args.text

    else:

        input_text = "What is the first sentence on the wikipedia page for the country of Iraq?"

    appbot = AppBot(verbose=True)
    appbot.invoke_agent(input_text)