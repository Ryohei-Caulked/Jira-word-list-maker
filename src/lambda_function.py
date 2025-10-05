import os
import json
import requests
from collections import Counter
from jira import JIRA
import re
from wordfreq import zipf_frequency

# Google Translate API Setting (As environmental variables)
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

# --- Post Jira Comment ---
def post_comment_to_jira(issue_key, table_markdown):
    #Auth Information for JIRA (As environmental variables)
    jira_user = os.environ['JIRA_USER']
    jira_token = os.environ['JIRA_TOKEN']
    jira_server = os.environ['JIRA_URL']
    
    jira = JIRA(server=jira_server, basic_auth=(jira_user, jira_token))
    jira.add_comment(issue_key, table_markdown)

# --- Difficulty-based selection using frequency data from wordfreq ---
def extract_difficult_words(text, top_n=10):
    words = re.findall(r'\b[a-zA-Z]{5,}\b', text)
    words = [w.lower() for w in words]
    counts = Counter(words)
    
    scored = []
    for w in counts:
        zipf = zipf_frequency(w, 'en')
        score = 7 - zipf
        scored.append((w, score))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    top_words = [w for w, s in scored[:top_n]]
    return top_words

# --- Translate English words to JPN by Google Translate API ---
def translate_word(word):
    url = f"https://translation.googleapis.com/language/translate/v2"
    params = {
        "q": word,
        "target": "ja",
        "format": "text",
        "key": GOOGLE_API_KEY
    }
    response = requests.get(url, params=params)
    result = response.json()
    try:
        return result['data']['translations'][0]['translatedText']
    except:
        return "Translation Failed"

# --- Generate Markdown tabale ---
def generate_markdown_table(word_list):
    table = "| Rank | English | JPN |\n"
    for i, word in enumerate(word_list, 1):
        translation = translate_word(word)
        table += f"| {i} | {word} | {translation} |\n"
    return table

# --- Lambda ---
def lambda_handler(event, context):
    try:
        if 'body' in event and event['body']:
            data = json.loads(event['body'], strict=False)
        else:
            data = event
        issue_key = data.get("issueKey")
        transcriptField = data.get("transcriptField")

        if not issue_key:
            return {"statusCode": 400, "body": "issueKey are required"}
        elif not transcriptField:
            return {"statusCode": 400, "body": "transcriptField are required"}
        
        top_words = extract_difficult_words(transcriptField, top_n=30)
        markdown_table = generate_markdown_table(top_words)
        post_comment_to_jira(issue_key, markdown_table)
        
        return {"statusCode": 200, "body": "Comment posted successfully"}
    except Exception as e:
        return {"statusCode": 500, "body": f"Error: {str(e)}"}
