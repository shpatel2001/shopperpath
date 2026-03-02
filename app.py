import streamlit as st
import pandas as pd

from modules.route_optimizer import generate_route
from modules.ai_item_interpreter import interpret_item
from modules.ai_substitutions import generate_substitution
from modules.ai_stock_risk import predict_stock_risk
from modules.parser import validate_and_clean
from modules.utils import format_json_output

# -------------------------------------------------
# GLOBAL PAGE CONFIG + CUSTOM CSS
# -------------------------------------------------
st.set_page_config(page_title="ShopperPath", layout="wide")

st.markdown("""
<style>
/* Global font + spacing */
body {
    font-family: 'Inter', sans-serif;
}

/* Card container */
.card {
    background: #ffffff10;
    padding: 1.2rem 1.4rem;
    border-radius: 12px;
    border: 1px solid #ffffff20;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

/* Section headers */
h3, h4 {
    margin-top: 0.5rem !important;
}

/* Cleaner buttons */
.stButton>button {
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
}

/* Dataframe spacing */
.block-container {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Helper to wrap content in a card
def card(content):
    st.markdown(f"<div class='card'>{content}</div>", unsafe_allow_html=True)

# -------------------------------------------------
# TITLE
# -------------------------------------------------
st.title("🛒 ShopperPath – Shopper Buying Assistant")

# -------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------
uploaded_file = st.file_uploader("Upload your order CSV", type=["csv"])

if not uploaded_file:
    st.info("Upload a CSV to begin.")
    st.stop()

# -------------------------------------------------
# LOAD + CLEAN CSV
# -------------------------------------------------
df = pd.read_csv(uploaded_file)

try:
    df = validate_and_clean(df)
except Exception as e:
    st.error(f"CSV Error: {e}")
    st.stop()

card("### 📄 Order Preview")
st.dataframe(df, use_container_width=True)

# -------------------------------------------------
# TABS
# -------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview",
    "Route",
    "Item Interpreter",
    "Substitutions",
    "Stock Risk",
    "Shopper Report"
])

# -------------------------------------------------
# 1. OVERVIEW
# -------------------------------------------------
with tab1:
    card("""
    ### 🧾 Order Overview

    **Total items:** {0}  
    **Categories:** {1}  
    **Brands:** {2}
    """.format(
        len(df),
        df["category"].nunique(),
        df["brand"].nunique()
    ))

    card("### 🛍️ Items by Category")
    st.dataframe(df.groupby("category")["item_name"].count().reset_index(), use_container_width=True)

# -------------------------------------------------
# 2. ROUTE OPTIMIZER
# -------------------------------------------------
with tab2:
    card("### 🧭 Optimized Store Route")

    if st.button("Generate Route"):
        with st.spinner("Optimizing route..."):
            route, total_time = generate_route(df)
            st.session_state["route_results"] = (route, total_time)

    if "route_results" in st.session_state:
        route, total_time = st.session_state["route_results"]

        card(f"### ⏱️ Estimated Total Shop Time: **{total_time} minutes**")

        for section in route:
            card(f"""
            #### 🛒 {section['aisle']} — {section['num_items']} item(s)
            **Estimated time:** {section['time_estimate']} min  
            **Items:** {section['items']}
            """)
    else:
        st.info("Click **Generate Route** to see the optimized picking order.")

# -------------------------------------------------
# 3. ITEM INTERPRETER
# -------------------------------------------------
with tab3:
    card("### 🔍 Item Interpreter")

    if st.button("Interpret Items"):
        with st.spinner("Interpreting items..."):
            results = []
            for _, row in df.iterrows():
                result = interpret_item(
                    item_name=row["item_name"],
                    category=row["category"],
                    dietary_tags=row["dietary_tags"],
                    customer_notes=row["customer_notes"]
                )
                results.append((row["item_name"], result))
            st.session_state["interpret_results"] = results

    if "interpret_results" in st.session_state:
        for item, interpretation in st.session_state["interpret_results"]:
            card(f"""
            ### 🛍️ {item}
            <pre>{format_json_output(interpretation)}</pre>
            """)
    else:
        st.info("Click **Interpret Items** to generate item insights.")

# -------------------------------------------------
# 4. SUBSTITUTION ENGINE
# -------------------------------------------------
with tab4:
    card("### 🔄 Substitution Engine")

    if st.button("Generate Substitutions"):
        with st.spinner("Generating substitutions..."):
            subs = []
            for _, row in df.iterrows():
                result = generate_substitution(
                    item_name=row["item_name"],
                    category=row["category"],
                    brand=row["brand"],
                    dietary_tags=row["dietary_tags"],
                    customer_notes=row["customer_notes"]
                )
                subs.append((row["item_name"], result))
            st.session_state["subs_results"] = subs

    if "subs_results" in st.session_state:
        for item, result in st.session_state["subs_results"]:
            card(f"""
            ### 🔁 {item}
            <pre>{format_json_output(result)}</pre>
            """)
    else:
        st.info("Click **Generate Substitutions** to generate alternatives.")

# -------------------------------------------------
# 5. STOCK RISK
# -------------------------------------------------
with tab5:
    card("### 📉 Stock Risk Predictor")

    if st.button("Predict Stock Risk"):
        with st.spinner("Predicting stock risk..."):
            risks = []
            for _, row in df.iterrows():
                result = predict_stock_risk(
                    item_name=row["item_name"],
                    historical_stock_risk=row["historical_stock_risk"],
                    historical_sub_rate=row["historical_substitution_rate"]
                )
                risks.append((row["item_name"], result))
            st.session_state["risk_results"] = risks

    if "risk_results" in st.session_state:
        for item, result in st.session_state["risk_results"]:
            card(f"""
            ### ⚠️ {item}
            <pre>{format_json_output(result)}</pre>
            """)
    else:
        st.info("Click **Predict Stock Risk** to generate risk insights.")

# -------------------------------------------------
# 6. SHOPPER REPORT
# -------------------------------------------------
with tab6:
    card("### 📝 Final Shopper Report")

    if st.button("Generate Shopper Report"):
        with st.spinner("Compiling report..."):
            sample_items = df['item_name'].tolist()[:10]

            report_prompt = f"""
            Create a concise, shopper-friendly report summarizing this Instacart order.
            Include:
            - What type of order this is
            - Key categories
            - Any items that may require extra attention
            - General shopping strategy

            Items: {sample_items}
            """

            report = interpret_item(
                item_name="Shopper Report",
                category="N/A",
                dietary_tags="N/A",
                customer_notes=report_prompt
            )

            st.session_state["shopper_report"] = report

    if "shopper_report" in st.session_state:
        card(f"### 🧾 Shopper Report<br><br>{st.session_state['shopper_report']}")
    else:
        st.info("Click to generate a final summary for the entire order.")