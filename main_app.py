# 📁 main_app.py
from database import init_db, fetch_transactions_db
init_db()
import streamlit as st
from frontend_ui import setup_sidebar, show_dashboard, show_login, logout_button, show_footer
from gmail_fetcher import fetch_transaction_emails_by_date
from utils import SCOPES
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
import pandas as pd
from datetime import datetime, timedelta
import os
import json

# ✅ UI setup
st.set_page_config(page_title="Smart Expense Tracker",  page_icon="favicon.png", layout="wide")
st.title("📊 Smart Personal Expense Dashboard")

# ✅ User login check
if "credentials" not in st.session_state or "user_email" not in st.session_state:
    show_login()
    st.stop()

user_email = st.session_state.user_email

# ✅ Sidebar date filters
st.sidebar.header("📅 Filter by Date")
default_start = datetime.now() - timedelta(days=15)
default_end = datetime.now()
start_date, end_date = setup_sidebar(default_start, default_end)

# ✅ Initialize session storage for fetched data
if "fetched_df" not in st.session_state:
    st.session_state.fetched_df = pd.DataFrame()

# ✅ When Fetch Button is clicked 
if st.sidebar.button("🔄 Fetch Transactions"):
    with st.spinner("Checking local database first..."):
        df = fetch_transactions_db(user_email, start_date, end_date)

        if df.empty:
            st.info("⏳ Not found in DB. Fetching from Gmail...")
            df = fetch_transaction_emails_by_date(
                st.session_state.credentials,
                start_date,
                end_date,
                user_email
            )

        if df.empty:
            st.warning("No transactions found for the selected date range." \
            "\n\n🔍 If you've made UPI, GPay, or app-based payments, please check if you received confirmation emails." \
            "\n\n📩 This app relies on email notifications to detect transactions.")

            st.stop()

        st.session_state.fetched_df = df
        st.success("✅ Fetched and updated dashboard!")
        st.rerun()

# ✅ Logout option
logout_button(location="sidebar")

# ✅ If no fetch yet, load from CSV fallback
df = st.session_state.fetched_df

if df.empty:
    csv_path = f"data/{user_email}/transactions.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        st.session_state.fetched_df = df
        st.info("📁 Loaded last saved transactions from CSV.")
    else:
        st.warning("No data found. Please fetch transactions using the sidebar.")
        st.stop()

# ✅ Show dashboard
show_dashboard(df)

# ✅ Show footer
show_footer()
