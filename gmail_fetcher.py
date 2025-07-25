
# 📁 gmail_fetcher.py
import re
import base64
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pandas as pd
import os

from database import insert_transactions
from utils import (CATEGORY_KEYWORDS, IGNORED_KEYWORDS, MERCHANT_PATTERNS, AMOUNT_PATTERNS)

def extract_amount(text):
    for pattern in AMOUNT_PATTERNS:
        match = re.search(pattern, text)
        if match:
            amt = match.group().replace("Rs.", "").replace("INR", "").replace("₹", "").strip()
            return re.sub(r'[^\d.]', '', amt)
    return "Not Found"

def extract_merchant(text, fallback_text=None):
    for pattern in MERCHANT_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            merchant = match.group(1).strip()
            return re.sub(r'[^A-Za-z0-9& ]', '', merchant).title()
    if fallback_text:
        fallback_match = re.search(r'(finzoomers|cashe|myntra|flipkart|zomato|swiggy|paytm|amazon|axio)', fallback_text, re.IGNORECASE)
        if fallback_match:
            return fallback_match.group(1).title()
    return "Unknown"

def get_category(merchant, body, subject):
    combined = f"{merchant} {body} {subject}".lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in combined for keyword in keywords):
            return category
    return "Misc"

def clean_date(raw_date):
    try:
        parsed = datetime.strptime(raw_date, "%a, %d %b %Y %H:%M:%S %z")
        return parsed.strftime('%Y-%m-%d')
    except Exception:
        return "Unknown"

def get_email_body(payload):
    parts = payload.get("parts", [])
    for part in parts:
        if part.get("mimeType") == "text/plain":
            data = part["body"]["data"]
            return base64.urlsafe_b64decode(data).decode("utf-8")
        elif part.get("mimeType") == "text/html":
            data = part["body"]["data"]
            decoded = base64.urlsafe_b64decode(data).decode("utf-8")
            return BeautifulSoup(decoded, "html.parser").get_text()
    return "No content found."

def fetch_transaction_emails_by_date(_creds, start_date, end_date, user_email):
    service = build('gmail', 'v1', credentials=_creds)
    query = f"after:{start_date.strftime('%Y/%m/%d')} before:{(end_date + timedelta(days=1)).strftime('%Y/%m/%d')} subject:(debited OR transaction OR spent OR UPI OR purchase OR payment)"
    results = service.users().messages().list(userId='me', q=query, maxResults=100).execute()
    messages = results.get('messages', [])

    email_data = []
    user_dir = os.path.join("data", user_email)
    os.makedirs(user_dir, exist_ok=True)

    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        payload = msg_detail.get("payload", {})
        headers = payload.get("headers", [])
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "No Date")
        body = get_email_body(payload)

        if any(kw in subject.lower() or kw in body.lower() for kw in IGNORED_KEYWORDS):
            continue

        amount = extract_amount(body)
        if amount in ["Not Found", None, ""]:
            with open(os.path.join(user_dir, "unmatched_logs.txt"), "a", encoding='utf-8') as f:
                f.write(f"\n\n[Skipped Email] Subject: {subject}\nBody: {body[:200]}...")
            continue

        merchant = extract_merchant(body, subject)
        category = get_category(merchant, body, subject)
        body_preview = body.replace("\n", " ")[:100]
        formatted_date = clean_date(date)

        email_data.append({
            "Date": formatted_date,
            "Amount": amount,
            "Merchant": merchant,
            "Category": category,
            "Subject": subject,
            "Body_Preview": body_preview
        })
    if not email_data:
        return pd.DataFrame() 
    
    df = pd.DataFrame(email_data)
    
    if 'Date' not in df.columns or df.empty:
        return pd.DataFrame()


    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

    df.to_csv(os.path.join(user_dir, "transactions.csv"), index=False)

    # ✅ INSERT INTO DATABASE (DEDUPE HANDLED)
    inserted = insert_transactions(user_email, email_data)
    print(f"[LOG] {inserted} new transactions inserted into DB.")

    return df
