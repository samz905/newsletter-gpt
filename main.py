import openai
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import requests
from datetime import datetime, timezone

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

NOTION_KEY = os.getenv("NOTION_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

headers = {
    "Authorization": "Bearer " + NOTION_KEY,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

models = ["gpt-3.5-turbo-0613", "gpt-3.5-turbo", "gpt-4-0613"]

app = FastAPI()

function_descriptions = [
    {
        "name": "categorise_email",
        "description": "Based on the contents of the email, the function categorises the email as either a newsletter or not",
        "parameters": {
            "type": "object",
            "properties": {
                "is_newsletter": {
                    "type": "boolean",
                    "description": "Accepts a true value if the contents of the email is a newsletter"
                }
            },
            "required": ["is_newsletter"]
        }
    },
    {
        "name": "summary_title",
        "description": "Based on the summary given in the query, the function creates a title for the summary",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Generated title for the summary containing less than 100 characters"
                }
            },
            "required": ["title"]
        }
    }
]


def doc_creator(content):
    """
    Create documents from text content.

    Args:
        content (str): The input text content.

    Returns:
        list: The list of created documents.
    """
    # Initialize the text splitter
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=150)

    # Split the content into chunks
    split_content = text_splitter.split_text(content)

    # Split the first chunk by newline character
    split_content = split_content[0].split("\n")

    # Create documents from the split content
    docs = text_splitter.create_documents(split_content)

    return docs


def generate_summary(content):
    """
    Generate a summary of the given content.

    Args:
        content (str): The content to generate a summary from.

    Returns:
        str: The generated summary.
    """
    # Create documents from content
    documents = doc_creator(content)

    # Initialize the ChatOpenAI model
    model = ChatOpenAI(model="gpt-3.5-turbo-0613", temperature=0.5)

    # Load and initialize the summarization chain
    chain = load_summarize_chain(model, chain_type="map_reduce")

    # Generate the summary using the chain
    summary = chain.run(documents)

    return summary


def generate_short_summary(content):
    """
    Generate a short summary of the given content.

    Args:
        content (str): The content to summarize.

    Returns:
        str: The generated short summary.
    """

    # Define the prompt template
    prompt_template = """Write a concise summary in less than 500 characters of the text given below. If it is a 
    newsletter, refer to it as a newsletter. If it isn't a newsletter, simply make summary say "This isn't a newsletter".
    If it is a newsletter, the summary should be less than 500 characters long and refer to the original text as a 
    newsletter, otherwise simply output the summary as "This isn't a newsletter". 

    TEXT: 
    {text}

    SUMMARY OF NEWSLETTER IN LESS THAN 500 CHARACTERS:"""

    # Generate the summary using the load_summarize_chain function
    summary = load_summarize_chain(
        ChatOpenAI(model=models[0], temperature=0.5),
        chain_type="stuff",
        prompt=PromptTemplate(template=prompt_template, input_variables=["text"])
    ).run(doc_creator(content))

    return summary


def summarise_newsletter(content):
    # Generate a short summary of the newsletter content
    short_summary = generate_short_summary(content)
    print(short_summary)

    # Prompt the user to generate a title for the summary content
    query_title = f"Please generate a title in less than 100 characters for the following newsletter summary content: {short_summary}"
    messages_title = [{"role": "user", "content": query_title}]

    # Generate the title using an AI model
    title = openai.ChatCompletion.create(
        model=models[0],
        messages=messages_title,
        temperature=0.5,
        functions=function_descriptions,
        function_call={"name": "summary_title"}
    )

    # Extract the generated title from the AI response
    title_json = json.loads(title["choices"][0]["message"]["function_call"]["arguments"])
    title = title_json["title"]

    # Generate the final summary of the newsletter content
    final_summary = generate_summary(content)

    # Create a summary object with the title and final summary
    summary_object = {
        "title": title,
        "summary": final_summary
    }

    return summary_object


def create_notion_page(data: dict) -> requests.Response:
    """
    Creates a new page in Notion using the provided data.

    Args:
        data (dict): The data to be sent in the request body.

    Returns:
        requests.Response: The response object containing the server's response to the request.
    """
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_NOTION_API_TOKEN"
    }
    response = requests.post(url, headers=headers, json=data)
    return response


def send_to_notion(summary_obj: dict):
    """
    Sends the given summary object to Notion.

    Args:
        summary_obj (dict): The summary object to send.

    """
    # Check if the summary object is not empty
    if summary_obj:
        # Extract the required values from the summary object
        title = summary_obj["title"]
        summary = summary_obj["summary"]
        published_date = datetime.now().astimezone(timezone.utc).isoformat()
        
        # Create the data payload to send to Notion
        data = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": {
                "Name": {"title": [{"text": {"content": title}}]},
                "Published": {"date": {"start": published_date, "end": None}}
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": summary
                                }
                            }
                        ]
                    }
                }
            ]
        }

        # Call the create_notion_page function with the data payload
        create_notion_page(data)


class Email(BaseModel):
    from_email: str
    content: str


@app.get("/")
def read_root():
    """
    Get request handler for the root endpoint.
    
    Returns:
        dict: A dictionary with the message "Hello" and "World".
    """
    return {"Hello": "World"}


@app.post("/")
def email_to_notion(email: Email):
    """
    This function handles an incoming email and sends it to Notion.
    
    Args:
        email (Email): The email object containing the email content.
    """
    # Get the email content
    content = email.content
    
    # Generate a short summary of the email content
    summary = generate_short_summary(content)
    
    # Create a query to ask if the email is a newsletter or not
    query = f"Please check if this email is a newsletter or not: {summary}"
    
    # Create messages for OpenAI chat completion
    messages = [
        {"role": "user", "content": query}
    ]
    
    # Make a request to OpenAI chat completion
    response = openai.ChatCompletion.create(
        model=models[0],
        messages=messages,
        functions=function_descriptions,
        function_call={"name": "categorise_email"}
    )
    
    # Extract the value of is_newsletter from the response
    is_newsletter = json.loads(response.choices[0]["message"]["function_call"]["arguments"])["is_newsletter"]
    
    # If the email is a newsletter, summarize it and send to Notion
    if is_newsletter:
        summary_obj = summarise_newsletter(content)
        send_to_notion(summary_obj)
