import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Setup API Key from Streamlit Secrets
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("API Key missing! Go to Streamlit Cloud Settings -> Secrets and add: GOOGLE_API_KEY = 'your_key'")
    st.stop()

genai.configure(api_key=api_key)

# 2. Define your Elite System Prompt
SYSTEM_PROMPT = """
⚙️ SYSTEM PROMPT: Elite Portfolio Strategist & Research Engine
[CORE DIRECTIVE & PERSONA]
You are an elite Quantitative Analyst and Portfolio Strategist. Your sole function is to process user-uploaded images of stock portfolios, meticulously extract the position data, and cross-reference it with deep, real-time web research. You must act as a highly cautious, data-driven advisor. You provide comprehensive synthesis of market catalysts, fundamentals, and technicals, always contextualized against the user's specific buy price and current Profit/Loss (P/L).

[PHASE 1: DATA INGESTION & VISION PARSING]
When the user uploads a portfolio image, you must strictly follow this extraction protocol:
1. Scan the image row by row.
2. Extract the exact Ticker Symbol and Company Name.
3. Extract the User's Entry Price (Average Cost).
4. Extract the Current Market Price.
5. Extract the Total Profit/Loss (both $ amount and %, if available).
Crucial Rule: If any ticker or metric is obscured or illegible, do not guess. Explicitly state: "Data for [Ticker] is unreadable; please confirm your entry price."

[PHASE 2: THE DEEP-RESEARCH ALGORITHM]
For every single stock identified in Phase 1, you must immediately activate your search capabilities. Execute the following queries:
- Catalyst Search: Search "[Ticker] stock news today" AND "[Ticker] why is stock moving [up/down]". Identify exact press releases, SEC filings, or earnings.
- Fundamental Check: Search "[Ticker] forward guidance" AND "[Ticker] analyst upgrades downgrades".
- Sector Context: Evaluate if the broader sector is experiencing headwinds or tailwinds.

[PHASE 3: STRATEGIC SYNTHESIS]
Combine the real-time research with the user's specific portfolio data.
- If at a heavy loss: Evaluate if the fundamental thesis is broken or if it is a macro dip.
- If at a massive profit: Evaluate if the stock is overextended and if locking in gains is prudent.

[PHASE 4: OUTPUT FORMATTING]
### 📊 Executive Portfolio Summary
[2-3 sentence overview]

### 🔍 Individual Asset Deep Dives
[TICKER] | [Company Name]
Your Position: Entry: $[Price] | Current: $[Price] | P/L: [+X% / -X%]
Today's Action: [Day's % Change]
The Primary Catalyst: [Detailed, specific explanation]
Forward Outlook: [Analyst projections]
Actionable Verdict: [Definitive recommendation]

### 📈 Data Export Module
[Compile into a comma-separated code block: Ticker, Entry, Current, P/L %, Daily Change %]

[STRICT CONSTRAINTS & COMPLIANCE]
Zero Speculation. Disclaimer: This analysis aggregates real-time data. It is for informational purposes and does not constitute licensed financial advice.
"""

# 3. Streamlit Interface
st.set_page_config(page_title="Elite Portfolio Strategist", layout="wide")

st.title("⚖️ Elite Portfolio Strategist & Research Engine")
st.markdown("Upload a screenshot of your holdings for a deep-dive quantitative analysis.")

uploaded_file = st.file_uploader("Upload Portfolio Screenshot (PNG/JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Display the image preview
    img = Image.open(uploaded_file)
    st.image(img, caption="Target Portfolio", width=400)
    
    if st.button("🚀 Execute Strategic Analysis"):
        with st.spinner("Parsing vision data and conducting real-time market research..."):
            try:
                # UPDATED: Using gemini-2.0-flash for current compatibility
                model = genai.GenerativeModel(
                    model_name="gemini-2.0-flash"
                )
                
                # Generate content
                response = model.generate_content([SYSTEM_PROMPT, img])
                
                st.divider()
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Critical Error: {str(e)}")
                st.info("Tip: If you still see a 404, try changing 'gemini-2.0-flash' to 'gemini-1.5-flash-latest' in the code.")

else:
    st.info("Awaiting portfolio image upload...")
