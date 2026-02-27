import streamlit as st
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

@st.cache_data(show_spinner=False)
def generate_substitution(item_name, category, brand, dietary_tags, customer_notes):
    prompt = f"""
You are helping an Instacart shopper choose the best substitution for an item.

Item: {item_name}
Category: {category}
Brand: {brand}
Dietary tags: {dietary_tags}
Customer notes: {customer_notes}

Return a JSON object with:
- best_substitution: the single best alternative
- reasoning: why this is the best choice
- fallback_options: 2 additional acceptable alternatives
- avoid: what NOT to substitute and why
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    return response.choices[0].message.content