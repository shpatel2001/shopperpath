import streamlit as st
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

@st.cache_data(show_spinner=False)
def interpret_item(item_name, category, dietary_tags, customer_notes):
    prompt = f"""
You are helping an Instacart shopper quickly understand an item before picking it.

Item: {item_name}
Category: {category}
Dietary tags: {dietary_tags}
Customer notes: {customer_notes}

Return a JSON object with:
- key_attributes: the 3–5 most important attributes
- confusion_risks: what might cause a shopper to pick the wrong item
- notes_summary: a short summary of customer notes
- shopper_tip: one helpful tip for picking this item correctly
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    return response.choices[0].message.content