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

content = """
    Today I am excited to present to you a special guest post by Fariborz, Nanne, and Max who wrote a piece on how to reduce conflict between data scientists and their business stakeholders while they worked at the ING Bank. At the time, Fariborz and Nanne were data scientists and Max was their chapter lead.
    The AiEdge Newsletter is a reader-supported publication. To receive new posts and support my work, consider becoming a free or paid subscriber.
    Building a successful AI product needs all hands on deck. Especially, the data science (DS) team and the business side have to collaborate well. Many times AI products fail simply due to conflicts between these two stakeholders.
    We believe that the risk of conflict is highest when beginning a project. This is when uncertainty is at its highest. We refer to this stage of data science workflow as disruptive research.
    To mitigate this risk, we propose a two-fold solution:
    Educating business stakeholders about disruptive research and its uncertainties.
    Nurturing trust between the DS team and their business stakeholders.
    Motivation
    Let us assume the following scenario: the goal is to develop a churn prediction algorithm for a payment product. The data science (DS) team breaks down the work into the following parts: data understanding, data preparation, modeling, evaluation, deployment, and business understanding (“Managing Data Science“ [ https://substack.com/redirect/b9e48629-8d22-4b72-9777-f23a574e4b51?j=eyJ1IjoicWs0dW8ifQ.rugtfuSAc3th6kFTqMFbCT2IXBjnqEf5sWnG25NBsBA ]). The DS team adheres to the SCRUM way of working. They plan to understand and prepare the data in the next two weeks. Two weeks have passed, and the DS task is not complete. The data are complex, and the team had a wrong estimation of how long it would take to prepare it. For the next sprint, they make another estimation to finish the same task. Two more weeks passed, and the task is still not done; unforeseen problems showed up in the data collection. The business stakeholders (and possibly the PM) are non-technical people and not intimately familiar with how data is processed, or algorithms are developed. The project is delayed and the expected results are not delivered. Business stakeholders become anxious. And this is when the risk of conflict is highest.
    Is the DS team bad at time estimation, or are they set up for failure? We believe that the leading cause of this conflict is something more profound. This contribution identifies two root causes:
    Misconceptions about the DS work, and
    Lack of trust between the DS team and their business stakeholders.
    To address these issues, we first establish the nature of the DS work and identify at which stage conflicts can arise. Then we discuss how to grow and nurture trust.
    The nature of data science work
    In the previous example, the DS team was set up for failure. The task of understanding and preparing the data is so uncertain that it was impossible to estimate when it will be done. But that begs the question, are all aspects of the DS work highly uncertain to the extent that they are unplannable? To answer this question, let us dissect the DS work. Generally speaking, the lifecycle of the DS work has three stages: disruptive research, productionalization, and incremental research — see Figure 1. In this section, we introduce each stage. And we identify the one in which conflicts usually arise. We skip the productionalization stage as it is discussed in literature such as “Putting Machine Learning Models into Production“ [ https://substack.com/redirect/4c4d78a7-6c76-4482-9d8c-b2b2110ccb27?j=eyJ1IjoicWs0dW8ifQ.rugtfuSAc3th6kFTqMFbCT2IXBjnqEf5sWnG25NBsBA ]. This stage is about taking a minimum viable algorithm and deploying it to production. 
    Two research stages
    We argue that DS research is about developing algorithms to solve specific business problems (Appendix A). We divide this endeavor into two parts: incremental and disruptive research. Incremental research improves existing algorithms, while disruptive research develops new ones.
    Incremental research
    Incremental research usually improves an existing algorithm. Therefore, it starts with a solid background: a well-defined problem, a fair understanding of the data, and a strong baseline. For this reason, scrum usually works well when doing incremental research. We make reference to available literature, such as “Don't Just Track Your ML Experiments, Version Them“ [ https://substack.com/redirect/87a0b32f-f6be-4da8-8b3d-3df27a3322be?j=eyJ1IjoicWs0dW8ifQ.rugtfuSAc3th6kFTqMFbCT2IXBjnqEf5sWnG25NBsBA ].
    Disruptive research
    In contrast to incremental research, disruptive research usually starts with nothing but a business idea. At the start, the problem is not well-defined. It is not clear which data to use and which metric to optimize. As a result, disruptive research is a highly uncertain endeavor; therefore, it is hardly plannable. A new DS project can be like mapping out unknown land: One does not know what lies ahead.
    The concept that we refer to as disruptive research is implicitly mentioned in the literature. For instance, Godsey (“Are we there yet?“ [ https://substack.com/redirect/8cc46056-bf69-4089-982f-32140f79aaa0?j=eyJ1IjoicWs0dW8ifQ.rugtfuSAc3th6kFTqMFbCT2IXBjnqEf5sWnG25NBsBA ]) mentions: “the need to acknowledge which parts of your project have the most uncertainty and to make plans to mitigate it.”. He later discusses the need to modify execution plans in process in “Think Like a Data Scientist“ [ https://substack.com/redirect/007f4cc4-7356-49c6-ae9b-679c6307481d?j=eyJ1IjoicWs0dW8ifQ.rugtfuSAc3th6kFTqMFbCT2IXBjnqEf5sWnG25NBsBA ].
    Why conflicts arise during disruptive research
    Circling back to the example of the motivation section, the task of understanding and preparing the data is a part of disruptive research. That is why the DS team consistently failed to promise a good estimation for its completion.
    Most of the conflicts arise during this stage. As discussed in the previous section, disruptive research is highly uncertain. The source of this uncertainty has three dimensions:
    Feasibility (data and modeling),
    Desirability, and
    Viability.
    Feasibility: At the early stages of disruptive research, we have little understanding of data availability and completeness. As a result, it is difficult to choose an adequate modeling technique.
    Desirability: At this stage desirability is also unknown. Are users actually willing to use the proposed solution?
    Viability: And finally, the viability is not certain. It highly depends on the solution and its desirability.
    During disruptive research, feasibility, desirability, and viability are highly uncertain. For this reason, it is usually impossible to estimate how long or how much effort it will take to deliver the final results.
    Scrum, the de facto framework for managing uncertain processes, requires the estimation of results one can achieve in a sprint (usually two weeks). However, we argue that this becomes impossible when there is so much uncertainty. One can make plans of which experiments to perform but cannot guarantee the outcome. This can be especially problematic in a high-pressure working environment. Sticking to scrum in a very literal way results in making unkeepable promises. In doing so, scrum can become a source of conflict rather than a solution.
    A two-fold solution
    To develop a healthy relationship between the DS team and its business stakeholders, we must first establish a common understanding of the disruptive research process.
    Part 1: Disruptive research process
    Developing an algorithm can be seen as a three-stage process, as depicted in Figure 2. The first stage is to check if the outcome is probably feasible, desirable, and viable. The second stage is to set up a research environment. And the last one is to develop the algorithm. In the following sections, we demonstrate this process in more detail.
    Meeting feasibility, desirability and viability prerequisites
    Making DS products can take several months. Hence, before any commitment, it is imperative to check if the project has a fair chance of success.
    Doing so is not trivial. However, checking if we can fail early is straightforward. This is done through some initial checks: desirability, feasibility, and viability checks.
    Desirability: Interviewing end-users is an excellent way to assess if a product is desirable. For instance, during an interview, one can show end users a mock-up user interface that shows the algorithm’s results. If the end-user is confident that such results are useless, then there is little point in going down this path.
    Feasibility: To check if an idea is (un)feasible, the DS team can check if the simplified version of the problem is solvable by hand. For instance, suppose the DS team wants to predict stock prices one week in advance. They can take one stock and see if they could have predicted its today’s price one week ago. They probably fail to make an accurate prediction. Therefore this task is unfeasible.
    Viability: The viability of an algorithm covers many topics. For instance, an algorithm should perform within legal, ethical, and compliance constraints. Or, using a user’s geolocation data without their consent is unethical and illegal. Or, if important stakeholders are not on board, the project is probably not viable. Another issue may be: are the right people available for the job?
    By doing these checks, we ensure that we know the stakeholders, understand end-user pain points, assess the availability and the quality of data, and educate ourselves regarding the subject matter. This helps failing early. It also helps when building a research environment.
    Building a research environment
    Algorithm development has a set of requirements:
    A business-aware problem statement,
    Business-aware evaluation metrics,
    Access to the right subject matter experts, and
    Access to a data warehouse that contains curated data and a computing environment for modeling.
    We refer to the collection of these requirements as the research environment. Before developing an algorithm, the DS team builds this environment. And in the future, if need be, they enrich it.
    At the beginning, when there is little understanding of the problem, the team has to deal with the issue of a cold start. For instance, it is unclear how comprehensive the problem statement is, which data to use, and how to build and evaluate the algorithm. Initially, the DS team should build a baseline algorithm to deal with this cold start. The goodness of this algorithm is unimportant. The goal is to produce a simple end-to-end algorithm, i.e., from the data to the metrics.
    Building this algorithm creates an initial version of the research environment. Specifically, the DS team consults stakeholders to devise an initial version of the problem statement and evaluation metric. Then, the DS team (quite possibly with the help of engineers) builds a database containing the datasets they initially perceive as required and starts a computing cluster. The DS team can develop a more advanced algorithm using this environment. And enrich it if need be.
    Algorithm development process
    Developing an algorithm is an iterative procedure that resembles the scientific method. Broadly speaking, the procedure is as depicted in Figure 3.
    Here we go through these steps with a detailed example of forecasting sales. Devising a hypothesis is about coming up with conjectures through endeavors such as consultation with subject matter experts, literature study, explanatory data analysis, and getting intuitions from outcomes of previous experiments.
    For example, through consultation with subject matter experts, the DS team uncover that promotion campaigns impact sales. The literature study informs them that autoregressive models are suitable for time series forecasting. The explanatory data analysis suggests that the sales data is quarterly seasonal. With these conjectures, the DS team forms a hypothesis, essentially the blueprint for an algorithm.
    The DS team then operationalizes the hypothesis by implementing the new algorithm and testing it. For instance, they might develop an autoregressive model that leverages sales seasonality. And they backtest it using an out-of-time validation scheme. While backtesting might suffice here, in other scenarios, one might need to run an online controlled experiment (e.g., A/B testing). In terms of metrics, the DS team could strive to optimize one metric (e.g., number of sales) while ensuring others do not cross a given threshold.
    The algorithm is deployed to production if the minimum business requirements are met. Otherwise, the DS team draws conclusions from their experiments and iterates. These conclusions, together with the previous conjectures, help the DS team devise a new hypothesis. For instance, the DS team could realize that the autoregressive model fails to address outliers. So they could decide to use another type of model. Developing another model, ideally, takes only a couple of days. For this reason, we refer to these iterations as short-term, as depicted in Figure 3.
    An iteration can also take a long time. These are the ones that require updating the research environment. For instance, the DS team could realize that while the algorithm forecasts an increase in sales, sales drop. When investigating the reason, the DS team figures out that the shops ran out of stock. For this reason, they conclude that they need warehouse data as well. Acquiring, understanding, cleaning, and processing warehouse data could lead to weeks of work. For this reason, we refer to these iterations as long-term, as depicted in Figure 3. Before committing to these long-term iterations, having a go/no-go session is a good idea. In this session, the effort to do the iteration is compared against the value of the potential outcome. If the return on investment is (too) low, the project can be stopped.
    Once the alg
"""


content2 = """
    Welcome to this month's edition of our AI-focused newsletter. We've got some exciting updates and insights to share with you!

    1. AI Breakthroughs:
    This month, OpenAI released a new language model, GPT-4, which has shown remarkable improvements in understanding and generating human-like text. Read more about it here.

    2. AI in Healthcare:
    AI continues to revolutionize healthcare. A recent study showed that AI algorithms can now predict the onset of Alzheimer's disease earlier and more accurately than ever before. Check out the full story here.

    3. AI Ethics:
    The debate around AI ethics continues to heat up. A recent conference brought together leading thinkers in the field to discuss the future of AI governance. Find out what they had to say here.

    4. AI Spotlight:
    This month, we're featuring an interview with Dr. Jane Doe, a leading researcher in AI for climate change. She shares her insights on how AI can help us combat global warming. Read the interview here.

    5. AI Learning Resources:
    Whether you're an AI expert or just getting started, we've got something for you. Check out these resources:

    "Understanding Neural Networks" - a beginner-friendly guide
    "Advanced Machine Learning Techniques" - a deep dive into the latest ML strategies
    "AI for Social Good" - exploring how AI can solve societal problems
    We hope you find these updates informative and inspiring. As always, if you have any questions or suggestions, feel free to reach out to us at ai-newsletter@substack.com.

    Stay curious and keep learning!

    Best,
    The AI Newsletter Team
"""

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

    print(docs[1])

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
    prompt_template = """Write a concise summary in less than 500 characters of the text given below. If it is a newsletter, refer to it as a newsletter. If it isn't a newsletter, 
    simply make summary say "This isn't a newsletter". If it is a newsletter, the summary should be less than 500 
    characters long and refer to the original text as a newsletter, otherwise simply output the summary as 
    "This isn't a newsletter". 

    TEXT: 
    {text}

    SUMMARY OF NEWSLETTER IN LESS THAN 500 CHARACTERS:"""

    docs = doc_creator(content)
    print("Docss", docs[1])

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

    print(summary_object["summary"])

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
def email_to_notion(content):
    """
    This function handles an incoming email and sends it to Notion.
    
    Args:
        email (Email): The email object containing the email content.
    """

    # Generate a short summary of the email content
    summary = generate_short_summary(content)

    print(summary)
    
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
        summarise_newsletter(content)
        # send_to_notion(summary_obj)


email_to_notion(content)
