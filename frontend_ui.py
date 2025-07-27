# 📁 frontend_ui.py
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from utils import SCOPES
import json


def show_login():
    st.subheader("🔐 Connect your Gmail account")

    st.markdown("👉 Click the link below to log in with your Gmail:")
    st.markdown(
        "[🔗 Click here to login with Google](https://accounts.google.com/o/oauth2/auth)",
        unsafe_allow_html=True
    )

    # 📷 Login flow guidance image (you can also use a GIF link here)
    
    st.markdown("🔑 Paste the **full URL** you were redirected to (we'll extract the code):")
    auth_url = st.text_input("🔗 Redirected URL")

    if st.button("Submit Code"):
        if "code=" not in auth_url:
            st.error("❌ URL does not contain a valid authorization code.")
            return

        try:
            # ✅ Extract the authorization code from URL
            code = auth_url.split("code=")[1].split("&")[0]

            # ✅ Load credentials from Streamlit secrets
            config_str = st.secrets["gcp"]["client_config"]
            config = json.loads(config_str)

            flow = Flow.from_client_config(config, scopes=SCOPES, redirect_uri="https://smart-expense-tracker-8sugdqlzf2rp2f5mkpt5tl.streamlit.app")

            # ✅ Fetch token using the code
            flow.fetch_token(code=code)
            creds = flow.credentials
            st.session_state.credentials = creds

            # ✅ Get user's email from Gmail API
            service = build('gmail', 'v1', credentials=creds)
            user_info = service.users().getProfile(userId='me').execute()
            st.session_state.user_email = user_info['emailAddress']

            st.success(f"✅ Logged in as: {st.session_state.user_email}")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Authentication failed. Error: {str(e)}")


def setup_sidebar(default_start, default_end):
    start_date = st.sidebar.date_input("Start Date", default_start.date())
    end_date = st.sidebar.date_input("End Date", default_end.date())
    return start_date, end_date

def show_dashboard(df):
    st.markdown("### 🔢 Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Spent", f"₹{df['Amount'].sum():,.2f}" , help="Total amount spent in selected time range.")
    col2.metric("📄 Transactions", len(df))
    col3.metric("🏪 Unique Merchants", df['Merchant'].nunique())

    st.divider()
    st.markdown('<h2>📊 Visual Insights</h2>', unsafe_allow_html=True)
    st.markdown("---")
    col4, col5 = st.columns(2)

    # Daily Spend Trend
    with col4:
        st.subheader("📈 Daily Spend Trend")
        st.markdown("---")
        daily = df.groupby('Date')['Amount'].sum().reset_index()
        fig1, ax1 = plt.subplots()
        sns.lineplot(data=daily, x='Date', y='Amount', marker='o', ax=ax1, color='purple')
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Amount (₹)")
        plt.xticks(rotation=90)
        plt.tight_layout()
        st.pyplot(fig1)

    # Spend by Category - Better Pie Chart
    with col5:
        st.subheader("🥧 Spend by Category")
        st.markdown("---")
        category = df.groupby('Category')['Amount'].sum()
        fig2, ax2 = plt.subplots()
        explode = [0.1 if i == category.idxmax() else 0 for i in category.index]
        colors = sns.color_palette('Set2', len(category))
        ax2.pie(category, labels=category.index, autopct='%1.1f%%', startangle=140,
                shadow=True, explode=explode, colors=colors, textprops={'fontsize': 9})
        ax2.axis('equal')
        st.pyplot(fig2)

    # Top Merchants by Spend
    st.subheader("🏪 Top Merchants by Spend")
    st.markdown("---")
    merchant = df.groupby('Merchant')['Amount'].sum().sort_values(ascending=False).head(10).reset_index()
    fig3, ax3 = plt.subplots()
    sns.barplot(data=merchant, x='Amount', y='Merchant', palette='crest', ax=ax3)
    ax3.set_xlabel("Total Spent (₹)")
    ax3.set_ylabel("Merchant")
    st.pyplot(fig3)

    # Category-wise Transaction Count
    st.subheader("🔢 No. of Transactions per Category")
    st.markdown("---")
    txn_count = df['Category'].value_counts().reset_index()
    txn_count.columns = ['Category', 'Count']
    fig4, ax4 = plt.subplots()
    sns.barplot(data=txn_count, x='Count', y='Category', palette='Blues_d', ax=ax4)
    ax4.set_xlabel("Transaction Count")
    st.pyplot(fig4)

    # Transaction Table
    with st.expander("📋 Show Transaction Table"):
        st.dataframe(df[["Date", "Amount", "Merchant", "Category"]], use_container_width=True)

    csv_data = df[["Date", "Amount", "Merchant", "Category"]].to_csv(index=False).encode('utf-8')
    st.download_button("📁 Download Filtered Data", data=csv_data, file_name="filtered_expenses.csv", mime="text/csv")


#log out securely and clear all session data
def logout_button(location="main"):
    if location == "sidebar":
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout"):
            st.session_state.clear()
            st.success("You have been logged out.")
            st.rerun()
    else:
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.success("You have been logged out.")
            st.rerun()

def show_footer():
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; font-size:14px; color:gray;'>"
        "Made with ❤️ by <b>Akash Sare</b> | © 2025 Smart Expense Tracker"
        "</div>",
        unsafe_allow_html=True
    )
