import openai
import textwrap
# from langchain.chains.summarize import load_summarize_chain
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.docstore.document import Document
# from langchain.chat_models import ChatOpenAI
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

def summarise_newsletter(content):
    # text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=150)
    # split_content = text_splitter.split_documents(content)

    # print(len(split_content))

    # llm = ChatOpenAI(model="gpt-3.5-turbo-0613", temperature=0.5)

    # docs = [Document(page_content=t) for t in split_content]

    # chain = load_summarize_chain(llm, chain_type="map_reduce")
    # summary = chain.run(docs[0])

    # # Split the text into chunks of approximately 500 characters each
    # split_content = textwrap.wrap(content, width=500)

    # print(len(split_content))

    # # Generate prompts for each chunk and summarize them
    # summary = []
    # for chunk in split_content:
    #     response = openai.Completion.create(
    #         engine="text-davinci-002",
    #         prompt=chunk,
    #         temperature=0.5,
    #         max_tokens=100
    #     )
    #     print(response.choices[0].text.strip())
    #     summary.append(response.choices[0].text.strip())

    # # Join the summaries together
    # summary = ' '.join(summary)

    query_title=f"Please generate a title in less than 100 characters for the following newsletter summary content: {content}"
    messages_title = [{"role": "user", "content": query_title}]

    title = openai.ChatCompletion.create(
        model=models[0],
        messages=messages_title,
        temperature=0.5,
        functions = function_descriptions,
        function_call={
            "name": "summary_title"
        }
    )

    title_json = json.loads(title["choices"][0]["message"]["function_call"]["arguments"])
    title = title_json["title"]

    summary_object = {
        "title": title,
        "summary": content
    }

    print(summary_object)


def create_notion_page(data: dict):
    create_url = "https://api.notion.com/v1/pages"

    res = requests.post(create_url, headers=headers, data=json.dumps(data))

    print("Notion response:", res.json())

    return res


def send_to_notion(summary_obj: dict):
    if summary_obj:
        title = summary_obj["title"]
        summary = summary_obj["summary"]
        published_date = datetime.now().astimezone(timezone.utc).isoformat()
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

        create_notion_page(data)


class Email(BaseModel):
    from_email: str
    content: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/")
def email_to_notion(email: Email):
    content = email.content
    query = f"Please check if this email is a newsletter or not: {content[:500]} "

    messages = [{"role": "user", "content": query}]

    response = openai.ChatCompletion.create(
        model=models[0],
        messages=messages,
        functions = function_descriptions,
        function_call={
            "name": "categorise_email"
        }
    )

    # Another way
    # response = openai.ChatCompletion.create(
    #     model="gpt-4-0613",
    #     messages=messages,
    #     functions = [function_descriptions[0]]
    # )

    arguments = response.choices[0]["message"]["function_call"]["arguments"]
    json_args = json.loads(arguments)

    is_newsletter = json_args["is_newsletter"]

    if is_newsletter:
        summary_obj = summarise_newsletter(content[:500])
        send_to_notion(summary_obj)
