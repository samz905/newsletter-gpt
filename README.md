# Newsletter Summarizer

This project is a FastAPI application that receives an email, checks if it's a newsletter, and if it is, it summarizes the content and sends it to a Notion page. The application is triggered by an API call from Zapier when a new email arrives.

## Setup

1. Clone the repository to your local machine.

2. Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory of the project and add your OpenAI API key, Notion API key, and Notion database ID:

```env
OPENAI_API_KEY=your_openai_api_key
NOTION_KEY=your_notion_key
NOTION_DATABASE_ID=your_notion_database_id
```

4. Run the FastAPI application:

```bash
uvicorn main:app --reload
```

## Zapier Setup

To set up Zapier to trigger the API call when a new email arrives, follow these steps:

1. Create a new Zap in Zapier.

2. For the trigger, choose the Email app and the "New Inbound Email" trigger event.

3. Set up the trigger by choosing your email account.

4. For the action, choose the Webhooks app and the "POST" action event.

5. Set up the action by entering the URL of your FastAPI application and the necessary data from the email.

6. Test your Zap and turn it on.

Now, whenever a new email arrives in your inbox, Zapier will trigger an API call to your FastAPI application, which will check if the email is a newsletter, summarize it if it is, and send the summary to a Notion page.

Please replace `your_openai_api_key`, `your_notion_key`, and `your_notion_database_id` with your actual keys. Also, adjust the setup instructions as needed based on your actual project setup.