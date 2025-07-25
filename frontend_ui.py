# 📁 frontend_ui.py
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from utils import SCOPES
from google.oauth2.credentials import Credentials
import os
import json


from google.oauth2.credentials import Credentials
import os
import json

def show_login():
    st.subheader("🔐 Connect your Gmail account")

    token_path = "token.json"
    if os.path.exists(token_path):
        # ✅ Load saved credentials from Flask login
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        st.session_state.credentials = creds

        # ✅ Extract user's email
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=creds)
        user_info = service.users().getProfile(userId='me').execute()
        st.session_state.user_email = user_info['emailAddress']

        st.success(f"✅ Logged in as: {st.session_state.user_email}")
        return

    # 🔁 If token.json not yet created, guide user
    st.warning("Please login via the Flask Auth Server first.")
    st.markdown("👉 [Click here to login](https://your-flask-app.onrender.com/login)")


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



