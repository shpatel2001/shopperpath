import streamlit as st
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

@st.cache_data(show_spinner=False)
def predict_stock_risk(item_name, historical_stock_risk, historical_sub_rate):
    prompt = f"""
You are helping an Instacart shopper understand stock risk for an item.

Item: {item_name}
Historical stock risk: {historical_stock_risk}
Historical substitution rate: {historical_sub_rate}

Return ONLY a single JSON object with:
- risk_level: low, medium, or high
- explanation: a short explanation based ONLY on the data
- shopper_action: one clear action the shopper should take

STRICT RULES:
- Return ONLY the JSON object.
- Do NOT provide multiple interpretations.
- Do NOT provide commentary outside the JSON.
- Do NOT explain your reasoning outside the JSON.
- Do NOT include markdown formatting.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    return response.choices[0].message.content