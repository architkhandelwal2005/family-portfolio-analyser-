import streamlit as st
import google.generativeai as genai
import yfinance as yf
import pandas as pd
import os

# 1. Setup API Key (Pulling from Streamlit Secrets for Cloud Deployment)
# Go to Streamlit Cloud -> Settings -> Secrets and add: GOOGLE_API_KEY = "your_key_here"
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("API Key not found. Please set GOOGLE_API_KEY in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)

def get_portfolio_analysis(data_summary):
    """Uses Gemini to provide buy/sell/hold insights."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Analyze this family stock portfolio data and provide brief advice: {data_summary}"
    response = model.generate_content(prompt)
    return response.text

# --- Streamlit UI ---
st.title("📈 Family Portfolio Analyser")

# Input for stock tickers
tickers_input = st.text_input("Enter Stock Tickers (comma separated, e.g., AAPL, TSLA, MSFT)", "AAPL, GOOGL")
tickers = [t.strip().upper() for t in tickers_input.split(",")]

if st.button("Analyze Portfolio"):
    with st.spinner("Fetching market data..."):
        try:
            # Fetch data using yfinance
            data = yf.download(tickers, period="5d", interval="1d")['Close']
            
            if not data.empty:
                st.subheader("Current Market Prices")
                st.dataframe(data.tail(1))
                
                # Prepare summary for AI
                summary = data.tail(1).to_string()
                
                st.subheader("AI Analysis & Strategy")
                analysis = get_portfolio_analysis(summary)
                st.write(analysis)
            else:
                st.warning("No data found for these tickers.")
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
