import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import io

# --- Configuration ---
# Your API key must be wrapped in quotation marks!
genai.configure(api_key="AIzaSyCJvXsx6AsOzYzz82CF9ZwSqlJwco5IYok")

# --- Auto-Detect Model (Fix for 404 Errors) ---
# Instead of guessing, we ask Google exactly which models your API key is allowed to use.
available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

if 'models/gemini-1.5-flash' in available_models:
    selected_model = 'gemini-1.5-flash'
elif 'models/gemini-1.5-flash-latest' in available_models:
    selected_model = 'gemini-1.5-flash-latest'
elif 'models/gemini-1.5-pro' in available_models:
    selected_model = 'gemini-1.5-pro'
else:
    selected_model = available_models[0].replace('models/', '') if available_models else 'gemini-1.5-flash'

model = genai.GenerativeModel(selected_model)

# --- Bug Fix: Constructing backticks dynamically to prevent UI cut-offs ---
fence = "`" * 3

# --- The System Prompt ---
SYSTEM_PROMPT = f"""
You are an elite Quantitative Analyst and Portfolio Strategist. 
Analyze the uploaded portfolio image. Cross-reference the extracted positions with real-time web research (catalysts, fundamentals, sector context).
Evaluate the user's current Profit/Loss (P/L) for each position to provide actionable advice.

Output format MUST strictly follow this:
1. Executive Portfolio Summary
2. Individual Asset Deep Dives (Entry, Current, P/L, Today's Action, Primary Catalyst, Forward Outlook, Actionable Verdict).
3. Data Export Module: At the very end, provide ONLY a raw, comma-separated CSV block wrapped in {fence}csv tags containing: Ticker,Entry_Price,Current_Price,PL_Percentage. Do not include $ or % symbols in the CSV numbers.
"""

# --- Streamlit UI ---
st.set_page_config(page_title="Family Portfolio Analyzer", layout="wide")
st.title("📈 The Family Portfolio Analyzer")
st.write("Upload a screenshot of your stock brokerage app to get real-time, personalized analysis.")

uploaded_file = st.file_uploader("Upload Portfolio Screenshot (PNG/JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Portfolio", use_container_width=True)
    
    if st.button("Analyze Portfolio"):
        with st.spinner("Executing deep web research and analyzing positions..."):
            try:
                # Call the Gemini API with the image and prompt
                response = model.generate_content([SYSTEM_PROMPT, image])
                full_text = response.text
                
                # Using the dynamic fence to safely split the text
                split_target = f"{fence}csv"
                end_target = f"{fence}"
                
                # Split the text to separate the markdown analysis from the CSV data
                if split_target in full_text:
                    analysis_part, csv_part = full_text.split(split_target)
                    csv_data = csv_part.split(end_target)[0].strip()
                else:
                    analysis_part = full_text
                    csv_data = None

                # Display the Markdown Analysis
                st.markdown(analysis_part)

                # --- EDA & Visualization ---
                if csv_data:
                    st.divider()
                    st.subheader("📊 Visual Performance Breakdown")
                    
                    # Load the CSV data directly into a pandas DataFrame
                    df = pd.read_csv(io.StringIO(csv_data))
                    
                    # Create a bar chart of Profit/Loss percentages using matplotlib
                    fig, ax = plt.subplots(figsize=(10, 5))
                    colors = ['green' if val > 0 else 'red' for val in df['PL_Percentage']]
                    ax.bar(df['Ticker'], df['PL_Percentage'], color=colors)
                    
                    ax.set_ylabel('Profit / Loss (%)')
                    ax.set_title('Current P/L per Asset')
                    ax.axhline(0, color='black', linewidth=1)
                    plt.xticks(rotation=45)
                    
                    st.pyplot(fig)
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")