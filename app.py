import streamlit as st
import pandas as pd

from modules.route_optimizer import generate_route
from modules.ai_item_interpreter import interpret_item
from modules.ai_substitutions import generate_substitution
from modules.ai_stock_risk import predict_stock_risk
from modules.parser import validate_and_clean
from modules.utils import format_json_output

st.set_page_config(page_title="ShopperPath", layout="wide")

st.title("🛒 ShopperPath – Instacart Shopper Assistant")

# File upload
uploaded_file = st.file_uploader("Upload your order CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Clean + validate CSV
    try:
        df = validate_and_clean(df)
    except Exception as e:
        st.error(f"CSV Error: {e}")
        st.stop()

    st.subheader("Order Preview")
    st.dataframe(df)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Overview",
        "Route",
        "Item Interpreter",
        "Substitutions",
        "Stock Risk",
        "Shopper Report"
    ])

    # -------------------------
    # 1. SIMPLE OVERVIEW SUMMARY
    # -------------------------
    with tab1:
        st.subheader("Order Overview")

        total_items = len(df)
        unique_categories = df["category"].nunique()
        unique_brands = df["brand"].nunique()

        st.markdown(f"""
        ### 🧾 Summary
        - **Total items:** {total_items}
        - **Categories:** {unique_categories}
        - **Brands:** {unique_brands}
        """)

        st.markdown("### 🛍️ Items by Category")
        st.dataframe(df.groupby("category")["item_name"].count().reset_index())

    # -------------------------
    # 2. ROUTE OPTIMIZER
    # -------------------------
    with tab2:
        st.subheader("Optimized Store Route")

        if st.button("Generate Route"):
            with st.spinner("Optimizing route..."):
                route, total_time = generate_route(df)
                st.session_state["route_results"] = (route, total_time)

        if "route_results" in st.session_state:
            route, total_time = st.session_state["route_results"]

            st.write(f"### Estimated Total Shop Time: {total_time} minutes")

            for section in route:
                st.markdown(f"#### 🛒 {section['aisle']} — {section['num_items']} item(s)")
                st.write(f"Estimated time: {section['time_estimate']} min")
                st.write(section["items"])
                st.markdown("---")
        else:
            st.info("Click 'Generate Route' to see the optimized picking order.")

    # -------------------------
    # 3. ITEM INTERPRETER (AI)
    # -------------------------
    with tab3:
        st.subheader("Item Interpreter")

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
                st.markdown(f"### 🛍️ {item}")
                st.code(format_json_output(interpretation), language="json")
                st.markdown("---")
        else:
            st.info("Click 'Interpret Items' to generate item insights.")

    # -------------------------
    # 4. SUBSTITUTION ENGINE (AI)
    # -------------------------
    with tab4:
        st.subheader("Substitution Engine")

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
                st.markdown(f"### 🔄 {item}")
                st.code(format_json_output(result), language="json")
                st.markdown("---")
        else:
            st.info("Click 'Generate Substitutions' to generate alternatives.")

    # -------------------------
    # 5. STOCK RISK PREDICTOR (AI)
    # -------------------------
    with tab5:
        st.subheader("Stock Risk Predictor")

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
                st.markdown(f"### 📉 {item}")
                st.code(format_json_output(result), language="json")
                st.markdown("---")
        else:
            st.info("Click 'Predict Stock Risk' to generate risk insights.")

    # -------------------------
    # 6. SHOPPER REPORT (AI SUMMARY)
    # -------------------------
    with tab6:
        st.subheader("Final Shopper Report")

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
            st.markdown("### 📝 Shopper Report")
            st.write(st.session_state["shopper_report"])
        else:
            st.info("Click to generate a final summary for the entire order.")

else:
    st.info("Upload a CSV to begin.")