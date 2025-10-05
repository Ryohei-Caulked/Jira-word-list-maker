# Jira-word-list-maker
This project automates English vocabulary extraction from transcripts and posts the results as a formatted comment in Jira. The system automatically analyzes the transcript and generates a list of advanced English words with Japanese translations.

## 🔄 Workflow

1. Trigger – A Jira Automation rule sends a webhook (HTTP POST) to an AWS API Gateway endpoint when a Subtask is created or updated.

2. Processing – The API Gateway invokes an AWS Lambda function written in Python. The Lambda securely loads credentials from environment variables.

3. Transcript Retrieval – The Lambda scrapes the English transcript from the TED Talk URL.

4. Vocabulary Extraction – Using the wordfreq library, the system identifies 100 high-difficulty words, ranked by rarity and linguistic complexity.

5. Translation and Formatting – Each word is translated into Japanese via the Google Translate API. Accent positions are marked for easier pronunciation learning.

6. Jira Comment – The vocabulary list is formatted into a Markdown-style table and automatically posted as a comment in the related Jira issue.

## ✅ Key Features

- Fully automated vocabulary generation directly from English texts or transcripts.

- Difficulty-based selection using frequency data from wordfreq.

- Language-learning optimized, including Japanese translations and accent markers.

- Secure integration with environment-based API keys for Jira and Google Translate.

- Scalable and serverless architecture using AWS Lambda and API Gateway.

## ⚙️ Technology Stack

| Component | Role |
| :----: | ---- |
|AWS Lambda | Executes transcript scraping and vocabulary analysis. |
|Amazon API Gateway | Receives webhooks from Jira Automation. |
|Jira API | Posts formatted vocabulary lists as comments. |
|Google Translate API | Provides Japanese translations. |
|wordfreq (Python) | Calculates linguistic difficulty scores. |
|S3 Layer Deployment | Manages large Python dependencies efficiently. |