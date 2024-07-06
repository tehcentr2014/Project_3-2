import openai
import os
from dotenv import find_dotenv, load_dotenv
import time
import logging
from datetime import datetime
import requests
import json
import streamlit as st

# Utility Functions
def remove_duplicates(text):
    words = text.split()
    unique_words = list(set(words))
    result_text = ' '.join(unique_words)
    return result_text

def load_env_variables():
    load_dotenv(find_dotenv())

# OpenAI Assistant Manager
class AssistantManager:
    assistant_id = "asst_sfcyRCDVLOViMwC3xL6P1tut"
    thread_id = "thread_xZUzMFIfmZngA5UA61Bqf4aZ"

    def __init__(self, model):
        self.client = openai.OpenAI()
        self.model = model
        self.assistant = None
        self.thread = None
        self.run = None
        self.summary = None
        self.retrieve_existing_assistant()
        self.retrieve_existing_thread()

    def retrieve_existing_assistant(self):
        if AssistantManager.assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(
                assistant_id=AssistantManager.assistant_id
            )

    def retrieve_existing_thread(self):
        if AssistantManager.thread_id:
            self.thread = self.client.beta.threads.retrieve(
                thread_id=AssistantManager.thread_id
            )

    def create_assistant(self, name, instructions, tools):
        if not self.assistant:
            assistant_obj = self.client.beta.assistants.create(
                name=name, instructions=instructions, tools=tools, model=self.model
            )
            self.assistant = assistant_obj
            AssistantManager.assistant_id = assistant_obj.id

    def create_thread(self):
        if not self.thread:
            thread_obj = self.client.beta.threads.create()
            self.thread = thread_obj
            AssistantManager.thread_id = thread_obj.id

    def add_message_to_thread(self, role, content):
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id, role=role, content=content
            )

    def run_assistant(self, instructions):
        if self.thread and self.assistant:
            self.run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions=instructions,
            )

    def process_message(self):
        if self.thread:
            messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
            summary = []

            last_message = messages.data[0]
            role = last_message.role
            response = last_message.content[0].text.value
            summary.append(response)

            self.summary = "\n".join(summary)

    def call_required_functions(self, required_actions):
        if not self.run:
            return
        tool_outputs = []

        for action in required_actions["tool_calls"]:
            func_name = action["function"]["name"]
            arguments = json.loads(action["function"]["arguments"])

            if func_name == "get_keywords":
                output = get_keywords(topic=arguments["topic"])
                final_str = ''.join(output)
                tool_outputs.append({"tool_call_id": action["id"], "output": final_str})
            else:
                raise ValueError(f"Unknown function: {func_name}")

        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id, run_id=self.run.id, tool_outputs=tool_outputs
        )

    def wait_for_completion(self):
        if self.thread and self.run:
            while True:
                time.sleep(5)
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id, run_id=self.run.id
                )
                if run_status.status == "completed":
                    self.process_message()
                    break
                elif run_status.status == "requires_action":
                    self.call_required_functions(run_status.required_actions.submit_tool_outputs.model_dump())

    def get_summary(self):
        return self.summary

    def run_steps(self):
        run_steps = self.client.beta.threads.runs.steps.list(
            thread_id=self.thread.id, run_id=self.run.id
        )
        return run_steps.data

# Streamlit Interface
def display_step1():
    st.header('Step 1. Enter Keywords and Remove Duplicates')

    text_input = st.text_area('Enter text:', '')
    if st.button('Remove Duplicates'):
        result = remove_duplicates(text_input)
        st.write('Result:', result)

def display_step2(manager):
    st.header("Step 2. Generate Description")

    with st.form(key="user_input_form"):
        instructions = st.text_input("Enter keywords:")
        submit_button = st.form_submit_button(label="Create description")

        if submit_button:
            manager.create_assistant(
                name="Content AI Assistant",
                instructions="Create product descriptions using provided keywords.",
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "get_keywords",
                            "description": "Get the list of keywords for the given topic",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "keywords": {
                                        "type": "string",
                                        "description": "The list of keywords",
                                    }
                                },
                                "required": ["keywords"],
                            },
                        },
                    }
                ],
            )
            manager.create_thread()

            manager.add_message_to_thread(
                role="user", content=f"Create product description using these keywords: {instructions}"
            )
            manager.run_assistant(instructions="""Create product descriptions using provided keywords.
            Descriptions must include: 
            1) Title (150-200 characters)
            2) Five bullet points (120-150 characters each)
            3) Description (900-1000 characters)
            """)
            manager.wait_for_completion()

            summary = manager.get_summary()
            st.write(summary)

def main():
    load_env_variables()

    st.title('Content Marketing Assistant')
    st.text('Automatically create product descriptions in 2 steps.')
    
    display_step1()
    
    manager = AssistantManager(model="gpt-3.5-turbo-16k")
    display_step2(manager)

if __name__ == "__main__":
    main()