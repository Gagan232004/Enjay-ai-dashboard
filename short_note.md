### Short Note

**What did I ask the AI?**  
I asked the AI to analyze a custom-generated sales dataset representing a clothing store. The prompt specifically requested the AI to identify top/bottom selling products (with reasons for slow sellers), the most and least popular sizes, the busiest/slowest days, two interesting demographic buying patterns, and to recommend three actionable steps. I also requested a bonus weekend sale item, a Hindi translation of the report, and a "What to avoid" section.

**What came out wrong the first time and how did I fix it?**  
Initially, the AI just gave generic insights like "Jeans sell well." It didn't provide specific reasons for poor-selling items, and the demographic patterns were too vague. I fixed this by pre-calculating specific metrics (like top/bottom 3 items, size distributions, and specific demographic counts like teen accessory purchases) in the Python script and passing these precise numbers in the prompt. This grounded the LLM's response, forcing it to generate specific, data-backed insights.

**What would I add if I had more time?**  
If I had more time, I would build an interactive Streamlit or Gradio dashboard to visualize the insights dynamically alongside the generated report. I would also use a more advanced agentic workflow to allow the LLM to write and execute pandas queries directly on the CSV to discover patterns autonomously.
