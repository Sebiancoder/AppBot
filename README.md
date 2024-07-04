# AppBot

An LLM-powered Selenium Agent for filling out job applications.

AppBot is built on the langchain LLM Agent framework. It consists of Selenium-based tools to automatically apply to job applications online.

The longer-term vision for this project is to have an LLM Agent that can independently find and apply to job openings, while being resilient to unexpected web events, non-standard job application websites, and errors.

## Setup

To install, clone this repository. Then run:

`pip install -r requirements.txt`

to install all required dependencies. 

In addition, to use this project, you need an OpenAI Key. You can set the key by setting the environment variable `OPENAI_API_KEY` to point to your key. Alternatively, you can put your key in a file entitled `openai_api_key.txt` in a folder entitled `secrets` in the root directory.

## Usage

To use AppBot, first provide your information in the `applicants` folder, including a json file with your basic information, your resume, and your transcript. The exact schema of the json does not matter much, as this is just passed directly to the LLM agent when the agent requests it. See the example_applicant folder for an example.

To run AppBot, run the following in the AppBot directory:

`python appbot.py -c "Specific Instructions here"

It is helpful to provide links to job postings, or a link to a website containing job postings as a specific instruction, otherwise the agent may struggle to find jobs to apply to.

This project is still in active development, and as such, it is likely to not be fully functioning or break easily. Any contributions are welcome!
