import streamlit as st
import pandas as pd
import plotly.express as px
import os
from groq import Groq
from fpdf import FPDF
import io

# --- Page Config ---
st.set_page_config(page_title="AI Retail Analyzer", page_icon="🛍️", layout="wide")

# --- Functions ---
def generate_summary_prompt(df):
    product_sales = df.groupby('product_name')['quantity_sold'].sum().sort_values(ascending=False)
    top_3 = product_sales.head(3).to_dict()
    bottom_3 = product_sales.tail(3).to_dict()
    size_sales = df.groupby('size')['quantity_sold'].sum().sort_values(ascending=False).to_dict()
    day_sales = df.groupby('day_of_week')['total_amount (Rs.)'].sum().sort_values(ascending=False).to_dict()
    
    # Try to safely extract demographic patterns if those columns exist
    teen_accessories = 0
    adult_men_bottoms = 0
    if 'age_group' in df.columns and 'category' in df.columns:
        teen_accessories = len(df[(df['age_group'] == 'Teen (13-19)') & (df['category'] == 'Accessories')])
    if 'age_group' in df.columns and 'customer_gender' in df.columns and 'category' in df.columns:
        adult_men_bottoms = len(df[(df['age_group'] == 'Adult (31-45)') & (df['customer_gender'] == 'Male') & (df['category'] == 'Bottoms')])
    
    summary_text = f"""
Sales Summary for the Month:
Total Sales Records: {len(df)}

1. Product Performance:
Top 3 Selling Products: {top_3}
Bottom 3 Selling Products: {bottom_3}

2. Size Performance:
Quantity Sold by Size: {size_sales}

3. Day of Week Revenue:
Revenue by Day: {day_sales}

4. Interesting Demographics Context:
- Teenagers buying accessories: {teen_accessories} transactions
- Adult men buying bottoms: {adult_men_bottoms} transactions

Please analyze this data and answer the following 5 questions (and 1 bonus question) in clear, simple English for a store manager. 

CRITICAL INSTRUCTIONS FOR FORMATTING:
- For Question 4 (Buying Patterns), DO NOT just repeat the numbers. You MUST write 2 detailed bullet points explaining the demographic trend and giving a specific store layout or stocking recommendation (e.g. placing accessories near the checkout counter).
- Include the Bonus question: Which item should we put on sale this weekend and why?
- You MUST provide the ENTIRE report in English.
- At the very end, include a "What to Avoid 🚫" section with 3 strict warnings.

Questions:
1. Which products are selling well and which are not? (For the 3 slow products, give one simple reason why)
2. Which size keeps running out? Which size is barely moving? 
3. Which day of the week is the busiest? Which is the slowest? 
4. Who is buying what? (Find 2 interesting demographic buying patterns and give actionable store advice)
5. Give the store manager 3 clear, specific actions for next week.
"""
    return summary_text

def generate_pdf(text_content):
    # Replace common smart punctuation
    replacements = {
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '—': '-', '–': '-', '…': '...', '•': '-',
        '₹': 'Rs.', '🚫': ''
    }
    for k, v in replacements.items():
        text_content = text_content.replace(k, v)
        
    # Keep ONLY basic ASCII and Devanagari to prevent FPDF crashes
    safe_chars = []
    for c in text_content:
        o = ord(c)
        if o < 128 or (0x0900 <= o <= 0x097F) or c in '\n\r\t':
            safe_chars.append(c)
    text_content = "".join(safe_chars)
    
    # Create PDF using fpdf2
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Add a built-in font that supports basic latin
    pdf.set_font("Helvetica", size=12)
    
    # Title
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(200, 10, txt="AI Retail Sales Report", ln=True, align='C')
    pdf.ln(10)
    
    # Body
    pdf.add_font("NotoSansDevanagari", fname="NotoSansDevanagari-Regular.ttf")
    pdf.set_font("Helvetica", size=11)
    # Enable fallback font so Hindi Devanagari renders correctly
    pdf.set_fallback_fonts(["NotoSansDevanagari"])
    
    # Write the full Unicode text natively
    pdf.multi_cell(0, 7, txt=text_content)
    
    return bytes(pdf.output())

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Configuration")
    st.info("Upload your store's CSV file to generate live AI insights.")
    
    # Try to intelligently get the API key from environment or secrets first
    env_api_key = os.getenv("GROQ_API_KEY", "")
    try:
        if not env_api_key and "GROQ_API_KEY" in st.secrets:
            env_api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
        
    api_key = st.text_input("Groq API Key", type="password", value=env_api_key, placeholder="gsk_...", help="Leave blank if already configured in Streamlit Secrets or Environment Variables.")
    uploaded_file = st.file_uploader("Upload Sales Data (CSV)", type=['csv'])

# --- Main App ---
st.title("🛍️ AI-Powered Retail Analyzer")
st.markdown("Upload your store data and let the AI generate interactive visualizations and a comprehensive PDF report instantly.")

if uploaded_file is None:
    st.warning("👈 Please upload a CSV file from the sidebar to begin.")
    st.stop()

# --- Process Uploaded Data ---
try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Error reading CSV file: {e}")
    st.stop()

# Validate columns
required_columns = ['product_name', 'quantity_sold', 'total_amount (Rs.)', 'day_of_week', 'size']
missing_cols = [col for col in required_columns if col not in df.columns]
if missing_cols:
    st.error(f"Uploaded CSV is missing required columns: {', '.join(missing_cols)}")
    st.stop()

# --- Title and Overview ---
total_revenue = df['total_amount (Rs.)'].sum()
total_items = df['quantity_sold'].sum()
busiest_day = df.groupby('day_of_week')['total_amount (Rs.)'].sum().idxmax()
top_product = df.groupby('product_name')['quantity_sold'].sum().idxmax()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"₹ {total_revenue:,.0f}")
col2.metric("Items Sold", f"{total_items}")
col3.metric("Busiest Day", busiest_day)
col4.metric("Top Product", top_product)

st.markdown("---")

# --- Charts Section ---
st.subheader("📊 Dynamic Visual Analytics")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("**Revenue by Day of the Week**")
    day_sales = df.groupby('day_of_week')['total_amount (Rs.)'].sum().reset_index()
    # Sort days properly if possible
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_sales['day_of_week'] = pd.Categorical(day_sales['day_of_week'], categories=days_order, ordered=True)
    day_sales = day_sales.sort_values('day_of_week')
    
    fig_day = px.bar(day_sales, x='day_of_week', y='total_amount (Rs.)', 
                     color='total_amount (Rs.)', color_continuous_scale='Blues')
    st.plotly_chart(fig_day, use_container_width=True)

with chart_col2:
    st.markdown("**Size Performance (Inventory Health)**")
    size_sales = df.groupby('size')['quantity_sold'].sum().reset_index()
    fig_size = px.funnel(size_sales, x='quantity_sold', y='size', 
                         color='size', color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_size, use_container_width=True)

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.markdown("**Top & Bottom Products**")
    prod_sales = df.groupby('product_name')['quantity_sold'].sum().sort_values().reset_index()
    fig_prod = px.bar(prod_sales, x='quantity_sold', y='product_name', orientation='h',
                      color='quantity_sold', color_continuous_scale='RdYlGn')
    st.plotly_chart(fig_prod, use_container_width=True)

with chart_col4:
    if 'age_group' in df.columns and 'category' in df.columns:
        st.markdown("**Demographics (Age vs Category)**")
        demo_sales = df.groupby(['age_group', 'category'])['quantity_sold'].sum().reset_index()
        fig_demo = px.bar(demo_sales, x='age_group', y='quantity_sold', color='category', 
                          barmode='stack', color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_demo, use_container_width=True)
    else:
        st.info("Upload data with 'age_group' and 'category' to see demographics.")

st.markdown("---")

# --- AI Report Generation ---
st.subheader("🤖 Generate AI Store Report")

if st.button("Generate AI Insights", type="primary"):
    if not api_key:
        st.error("Please enter your Groq API Key in the sidebar first!")
    else:
        with st.spinner("Analyzing data and generating report via Llama 3.3..."):
            try:
                client = Groq(api_key=api_key)
                prompt = generate_summary_prompt(df)
                
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a brilliant retail data analyst. Provide specific, data-backed business answers based solely on the provided summary. Do not make up numbers. You MUST format your response to match the exact structure, tone, and headings of the following example report. Here is the strict template you must follow:\n\n" + open("store_report.md", "r", encoding="utf-8").read()
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=2048,
                )
                
                report_content = completion.choices[0].message.content
                st.session_state['generated_report'] = report_content
                st.success("Report generated successfully!")
            except Exception as e:
                st.error(f"Failed to generate report: {e}")

# Display Report and Download Button
if 'generated_report' in st.session_state:
    report = st.session_state['generated_report']
    
    st.markdown("### Executive Summary")
    st.markdown(report)
    
    # Generate PDF bytes
    pdf_bytes = generate_pdf(report)
    
    st.download_button(
        label="📄 Download Report as PDF",
        data=pdf_bytes,
        file_name="AI_Store_Report.pdf",
        mime="application/pdf",
        type="primary"
    )
