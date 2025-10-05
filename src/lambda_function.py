import os
import json
import requests
from bs4 import BeautifulSoup
from collections import Counter
from jira import JIRA
import re
from wordfreq import zipf_frequency

# Google Translate API設定（環境変数）
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

# --- Jira コメント投稿 ---
def post_comment_to_jira(issue_key, table_markdown):
    jira_user = os.environ['JIRA_USER']
    jira_token = os.environ['JIRA_TOKEN']
    jira_server = os.environ['JIRA_URL']
    
    jira = JIRA(server=jira_server, basic_auth=(jira_user, jira_token))
    jira.add_comment(issue_key, table_markdown)

# --- 難易度の高い単語抽出 ---
def extract_difficult_words(text, top_n=10):
    words = re.findall(r'\b[a-zA-Z]{5,}\b', text)
    words = [w.lower() for w in words]
    counts = Counter(words)
    
    scored = []
    for w in counts:
        zipf = zipf_frequency(w, 'en')  # 1～7 小さいほど珍しい
        score = 7 - zipf # 珍しさをスコア化
        scored.append((w, score))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    top_words = [w for w, s in scored[:top_n]]
    return top_words

# --- Google Translate APIで日本語訳取得 ---
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
        return "翻訳不可"

# --- Markdown表作成 ---
def generate_markdown_table(word_list):
    table = "| 順位 | 英単語 | 日本語訳 |\n"
    for i, word in enumerate(word_list, 1):
        translation = translate_word(word)
        table += f"| {i} | {word} | {translation} |\n"
    return table

# --- Lambdaハンドラー ---
def lambda_handler(event, context):
    try:
        # HTTP APIではeventがそのままdictになる場合がある
        if 'body' in event and event['body']:
            data = json.loads(event['body'], strict=False)
        else:
            data = event  # すでにdictの場合
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
