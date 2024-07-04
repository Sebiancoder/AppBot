# AppBot

An LLM-powered Selenium Agent for filling out job applications.

AppBot is built on the langchain LLM Agent framework. It consists of Selenium-based tools to automatically apply to job applications online.

The longer-term vision for this project is to have an LLM Agent that can independently find and apply to job openings, while being resilient to unexpected web events, non-standard job application websites, and errors.

## Setup

To install, clone this repository. Then run:

`pip install -r requirements.txt`

to install all required dependencies. 

In addition, to use this project, you need an OpenAI Key. You can set the key by setting the environment variable `OPENAI_API_KEY` to point to your key. Alternatively, you can put your key in a file entitled `openai_api_key.txt` in the `secrets` folder.
