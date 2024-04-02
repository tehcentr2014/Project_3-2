import openai
import os
from dotenv import find_dotenv, load_dotenv
import time
import logging
from datetime import datetime
import requests
import json
import streamlit as st

def removeDuplicates(text):
    # Split text into words
    words = text.split()

    # Remove duplicates
    unique_words = list(set(words))

    # Join unique words back into text
    result_text = ' '.join(unique_words)

    return result_text

def run_app():
    st.title('Content Marketing Assistant')
    st.text('This app will help you automatically create product descriptions in just 2 steps:')
    st.header('Step 1. Enter Keywords and Remove Duplicates')

    # Get input text from user
    text_input = st.text_area('Enter text:', '')


    if st.button('Remove Duplicates'):
        result = removeDuplicates(text_input)
        st.write('Result:', result)

if __name__ == '__main__':
    run_app()

# Initialize the OpenAI client
client = openai.OpenAI()
OPENAI_API_KEY="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"
model = "gpt-3.5-turbo-16k"

# Function to enter keywords by client
def get_keywords(keywords):
    keywords = input("Enter keywords: ")
    return keywords

class AssistantManager:
    assistant_id = "asst_sfcyRCDVLOViMwC3xL6P1tut"
    thread_id = "thread_xZUzMFIfmZngA5UA61Bqf4aZ"

    def __init__(self, model: str = model):
        self.client = client
        self.model = model
        self.assistant = None
        self.thread = None
        self.run = None
        self.summary = None

        # Retrieve existing assistant and thread if IDs are already set
        if AssistantManager.assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(
                assistant_id=AssistantManager.assistant_id
            )
        if AssistantManager.thread_id:
            self.thread = self.client.beta.threads.retrieve(
                thread_id=AssistantManager.thread_id
            )

    def create_assistant(self, name, instructions, tools):
        if not self.assistant:
            assistant_obj = self.client.beta.assistants.create(
                name=name, instructions=instructions, tools=tools, model=self.model
            )
            AssistantManager.assistant_id = assistant_obj.id
            self.assistant = assistant_obj
            print(f"AssisID:::: {self.assistant.id}")

    def create_thread(self):
        if not self.thread:
            thread_obj = self.client.beta.threads.create()
            AssistantManager.thread_id = thread_obj.id
            self.thread = thread_obj
            print(f"ThreadID::: {self.thread.id}")

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
            print(f"SUMMARY-----> {role.capitalize()}: ==> {response}")

            # for msg in messages:
            #     role = msg.role
            #     content = msg.content[0].text.value
            #     print(f"SUMMARY-----> {role.capitalize()}: ==> {content}")

    def call_required_functions(self, required_actions):
        if not self.run:
            return
        tool_outputs = []

        for action in required_actions["tool_calls"]:
            func_name = action["function"]["name"]
            arguments = json.loads(action["function"]["arguments"])

            if func_name == "get_keyword":
                output = get_keyword(topic=arguments["topic"])
                print(f"STUFFFFF;;;;{output}")
                final_str = ""
                for item in output:
                    final_str += "".join(item)

                tool_outputs.append({"tool_call_id": action["id"], "output": final_str})
            else:
                raise ValueError(f"Unknown function: {func_name}")

        print("Submitting outputs back to the Assistant...")
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id, run_id=self.run.id, tool_outputs=tool_outputs
        )

    # for streamlit
    def get_summary(self):
        return self.summary

    def wait_for_completion(self):
        if self.thread and self.run:
            while True:
                time.sleep(5)
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id, run_id=self.run.id
                )
                print(f"RUN STATUS:: {run_status.model_dump_json(indent=4)}")

                if run_status.status == "completed":
                    self.process_message()
                    break
                elif run_status.status == "requires_action":
                    print("FUNCTION CALLING NOW...")
                    self.call_required_functions(
                        required_actions=run_status.required_action.submit_tool_outputs.model_dump()
                    )

    # Run the steps
    def run_steps(self):
        run_steps = self.client.beta.threads.runs.steps.list(
            thread_id=self.thread.id, run_id=self.run.id
        )
        print(f"Run-Steps::: {run_steps}")
        return run_steps.data


def main():
    # news = get_keyword("bitcoin")
    # print(news[0])
    manager = AssistantManager()

    # Streamlit interface
    st.header("Step 2. Generate Description")

    with st.form(key="user_input_form"):
        instructions = st.text_input("Enter keywords:")
        submit_button = st.form_submit_button(label="Create description")

        if submit_button:
            manager.create_assistant(
                name="Content AI Assistent",
                instructions="You are a personal article summarizer Assistant who knows how to take a list of article's titles and descriptions and then write a short summary of all the news articles",
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

            # Add the message and run the assistant
            manager.add_message_to_thread(
                role="user", content=f"write the product description according to the {instructions}?"
            )
            manager.run_assistant(instructions="""You are the best Content Marketing Assistant, who will create product descriptions using the keyword provided by the client in the message. 
    The product description must have:
    1) Title from 150 to 200 characters long
    2) 5 Bullet points from 120 to 150 characters each
    3) Description from 900 to 1000 characters long""",
    )

            # Wait for completions and process messages
            manager.wait_for_completion()

            summary = manager.get_summary()

            st.write(summary)

            #t.text("Run Steps:")
            #st.code(manager.run_steps(), line_numbers=True)


if __name__ == "__main__":
    main()
