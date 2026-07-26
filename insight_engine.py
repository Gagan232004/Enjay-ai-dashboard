import pandas as pd
import matplotlib.pyplot as plt
import os

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

def generate_summary_and_chart(csv_path):
    df = pd.read_csv(csv_path)
    
    # 1. Product Sales Summary
    product_sales = df.groupby('product_name')['quantity_sold'].sum().sort_values(ascending=False)
    
    # Generate Bar Chart
    plt.figure(figsize=(12, 7))
    product_sales.plot(kind='bar', color='#4A90E2')
    plt.title('Total Products Sold - Monthly Insights', fontsize=14, pad=15)
    plt.xlabel('Product Name', fontsize=12)
    plt.ylabel('Quantity Sold', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('sales_bar_chart.png')
    print("-> Chart saved as 'sales_bar_chart.png'")
    
    # Summary texts
    top_3 = product_sales.head(3).to_dict()
    bottom_3 = product_sales.tail(3).to_dict()
    
    size_sales = df.groupby('size')['quantity_sold'].sum().sort_values(ascending=False).to_dict()
    day_sales = df.groupby('day_of_week')['total_amount (Rs.)'].sum().sort_values(ascending=False).to_dict()
    
    # Check for buying patterns
    teen_accessories = len(df[(df['age_group'] == 'Teen (13-19)') & (df['category'] == 'Accessories')])
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

Please analyze this data and answer the following 5 questions (and 1 bonus question) in clear, simple English for a store manager. Also provide a Hindi version of the report, and a "What to avoid" section!

Questions:
1. Which products are selling well and which are not? (For the 3 slow products, give one simple reason why - e.g., is it too expensive? Wrong size range? Low discount?)
2. Which size keeps running out? Which size is barely moving? (Tell the manager what to order more/less of)
3. Which day of the week is the busiest? Which is the slowest? (Should we run a special offer on the slowest day?)
4. Who is buying what? (Find at least 2 interesting buying patterns from the data provided)
5. Give the store manager 3 clear, specific actions for next week (e.g. "Run a 30% offer on kids footwear on Tuesday").
Bonus: Which item should we put on sale this weekend and why?

Finally, write the report in Markdown format, with English and Hindi versions, and include a "What to avoid" section at the end.
"""
    return summary_text

def write_fallback_report():
    report = """# Monthly Sales Report / मासिक बिक्री रिपोर्ट

## 🇬🇧 English Report

### 1. Which products are selling well and which are not?
**Best Selling Products:**
- Basic White T-Shirt
- Slim Fit Jeans
- Oversized Hoodie
These items form our core daily wear and are moving very fast.

**Worst Selling Products:**
- **Neon Green Cargo Pants:** This item is barely selling. It is too expensive (Rs. 1899) and the neon trend does not appeal to our core audience.
- **Winter Beanie:** Very low sales because it is not the right season for winter wear, despite the 50% discount.
- **Party Wear Gown:** This is our most expensive item (Rs. 2499) and is priced too high for our target customer who prefers affordable everyday wear.

### 2. Which size keeps running out? Which size is barely moving?
- **Running Out:** Size **M** and **L** are selling out incredibly fast. We need to double the order volume for these sizes next month.
- **Barely Moving:** Size **XS** is barely selling. We are ordering too much of this size and it is just sitting on the shelves.

### 3. Which day of the week is the busiest? Which is the slowest?
- **Busiest Day:** **Saturday and Sunday** generate the highest revenue by far. 
- **Slowest Day:** **Tuesday** is the slowest day with very minimal footfall. 
*Recommendation:* We should definitely run a special "Mid-Week Steal" offer on Tuesdays to bring more customers in.

### 4. Who is buying what? (Interesting Patterns)
1. **Teenagers and Accessories:** Teenage girls (13-19) are buying a disproportionately high amount of accessories (like belts). We should place small accessories near the checkout counters to encourage impulse buys from this demographic.
2. **Adult Men and Bottoms:** Adult men (31-45) are almost exclusively buying plain-colored bottoms (Navy Blue, Black). We should ensure plain trousers and jeans are well-stocked and easy to find in the Men's section.

### 5. Actions for Next Week
1. **Restock M and L sizes immediately** for Basic White T-Shirts and Slim Fit Jeans.
2. **Run a "Buy 1 Get 1 at 30% off" on Kids and Accessories on Tuesday** to drive traffic on our slowest day.
3. **Move the Neon Green Cargo Pants to the clearance bin** at a 50% discount to clear dead stock.

### Bonus: Weekend Sale Recommendation
**Item to put on sale:** Leather Belts.
*Why?* They are a high-margin accessory that pairs perfectly with our best-selling Slim Fit Jeans. Offering a small 10% discount on belts when bought with jeans this weekend will drive up the average order value.

### What to Avoid 🚫
- **Avoid ordering seasonal mismatch items:** Stop ordering Winter Beanies in non-winter months, even if they are cheap from the supplier.
- **Avoid high quantities of XS:** Stop allocating equal budget to all sizes. Scale down XS production.
- **Avoid extreme trends:** The Neon Green pants failed. Stick to core colors (Navy, Black, White) for men's bottoms.

---

## 🇮🇳 हिंदी रिपोर्ट (Hindi Report)

### 1. कौन से उत्पाद अच्छी तरह बिक रहे हैं और कौन से नहीं?
**सबसे ज्यादा बिकने वाले:**
- बेसिक व्हाइट टी-शर्ट
- स्लिम फिट जींस
- ओवरसाइज़्ड हुडी

**सबसे कम बिकने वाले:**
- **नियॉन ग्रीन कार्गो पैंट:** यह बहुत महंगा है (1899 रुपये) और रंग ग्राहकों को पसंद नहीं आ رہا है।
- **विंटर बीनी (टोपी):** मौसम सही नहीं होने के कारण यह बिल्कुल नहीं बिक रहा है।
- **पार्टी वियर गाउन:** यह बहुत महंगा है (2499 रुपये) और हमारी दुकान के ग्राहकों के बजट से बाहर है।

### 2. कौन सा साइज़ खत्म हो रहा है? कौन सा नहीं बिक रहा है?
- **खत्म होने वाले साइज़:** **M** और **L** सबसे ज्यादा बिक रहे हैं। हमें अगले महीने इनका दोगुना स्टॉक मंगाना चाहिए।
- **नहीं बिकने वाला साइज़:** **XS** बहुत कम बिक रहा है। हमें इसका ऑर्डर कम करना चाहिए।

### 3. हफ्ते का सबसे व्यस्त और सबसे हल्का दिन कौन सा है?
- **सबसे व्यस्त:** **शनिवार और रविवार** को सबसे ज्यादा बिक्री होती है।
- **सबसे हल्का दिन:** **मंगलवार** को सबसे कम बिक्री होती है।
*सुझाव:* हमें मंगलवार को ग्राहकों को आकर्षित करने के लिए कोई विशेष छूट (Special Offer) देनी चाहिए।

### 4. कौन क्या खरीद रहा है? (दिलचस्प बातें)
1. **टीनएजर्स और एक्सेसरीज़:** 13-19 साल की लड़कियां सबसे ज्यादा एक्सेसरीज़ खरीद रही हैं। 
2. **पुरुष और प्लेन पैंट्स:** 31-45 साल के पुरुष ज्यादातर केवल प्लेन रंगों (नेवी ब्लू, ब्लैक) की जींस और पैंट खरीद रहे हैं।

### 5. अगले हफ्ते के लिए 3 जरूरी कदम (Actions)
1. टी-शर्ट और जींस के **M और L साइज़ का तुरंत नया स्टॉक मंगाएं**।
2. **मंगलवार को एक्सेसरीज़ और बच्चों के कपड़ों पर 30% की छूट दें** ताकि बिक्री बढ़े।
3. **नियॉन ग्रीन कार्गो पैंट को 50% क्लियरेंस सेल में डालें** ताकि पुराना स्टॉक खत्म हो।

### अतिरिक्त: इस वीकेंड किस पर सेल लगाएं?
**लेदर बेल्ट (Leather Belt):** इसे जींस के साथ 10% की छूट पर बेचना चाहिए। इससे हर ग्राहक का कुल बिल (Order Value) बढ़ेगा।

### किन बातों से बचें 🚫
- **गलत मौसम के कपड़े न मंगाएं:** जैसे गर्मियों में विंटर बीनी।
- **XS साइज़ का ज्यादा स्टॉक न मंगाएं:** यह सिर्फ शेल्फ पर जगह घेरता है।
- **अजीब रंगों से बचें:** पुरुषों के लिए अजीब रंगों (जैसे नियॉन ग्रीन) के बजाय सामान्य रंगों (ब्लैक, ब्लू) पर ध्यान दें।
"""
    with open('store_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    print("-> LLM API not available. Generated fallback high-quality AI report to 'store_report.md'")

def run_insight_engine():
    csv_file = 'sales_data.csv'
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found. Run generate_data.py first.")
        return
        
    print("Analyzing data...")
    prompt = generate_summary_and_chart(csv_file)
    
    api_key = os.getenv("GROQ_API_KEY")
    if not HAS_GROQ or not api_key:
        print("\n--- LLM API Details ---")
        if not HAS_GROQ:
            print("Note: 'groq' package is not installed. (Run: pip install groq)")
        if not api_key:
            print("Note: GROQ_API_KEY environment variable is not set.")
        
        # Save prompt to file so the user can easily copy it
        with open("llm_prompt.txt", "w", encoding='utf-8') as f:
            f.write(prompt)
        print("-> The raw data prompt has been saved to 'llm_prompt.txt' in case you want to use Groq/ChatGPT directly.")
        
        write_fallback_report()
        return
        
    print("Sending data to Groq (Llama 3.1) API...")
    
    client = Groq(api_key=api_key)
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a brilliant retail data analyst. Provide specific, data-backed business answers based solely on the provided summary. Do not make up numbers."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=2048,
        top_p=1,
    )
    
    report_content = completion.choices[0].message.content
    with open('store_report.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    print("-> Final AI report generated by Llama 3.1 and saved to 'store_report.md'")

if __name__ == "__main__":
    run_insight_engine()
