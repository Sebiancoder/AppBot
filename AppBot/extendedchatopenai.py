import langchain
from langchain_openai import ChatOpenAI
import os

class ExtendedChatOpenAI(ChatOpenAI):

    def __init__(self, model: str = "gpt-4", api_key_filename: str= None, **kwargs):
        
        if "OPENAI_API_KEY" in os.environ:

            super().__init__(model=model, api_key=os.environ["OPENAI_API_KEY"], **kwargs)
        
        else:

            if api_key_filepath is None:
                
                raise ValueError("api_key_filepath is required if OPENAI_API_KEY is not in the environment")
            
            api_key = self.load_api_key_from_file(api_key_filename)

            super().__init__(model=model, api_key=api_key, **kwargs)

    def load_api_key_from_file(self, filename: str) -> str:

        with open(f"secrets/{filename}", "r") as f:

            return f.read().strip()