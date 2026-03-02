import streamlit as st
import pandas as pd

from modules.route_optimizer import generate_route
from modules.ai_item_interpreter import interpret_item
from modules.ai_substitutions import generate_substitution
from modules.ai_stock_risk import predict_stock_risk
from modules.parser import validate_and_clean
from modules.utils import format_json_output

st.set_page_config(page_title="ShopperPath", layout="wide")

# UI styling
st.markdown("""
<style>

    * {
        font-family: 'Inter', sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    body {
        margin: 0;
        padding: 0;
    }

    .section-header {
        font-size: 1.35rem;
        font-weight: 600;
        margin-top: 1.4rem;
        margin-bottom: 0.4rem;
        letter-spacing: -0.3px;
    }

    .card {
        background-color: var(--card-bg);
        border: 1px solid var(--card-border);
        padding: 16px 18px;
        border-radius: 14px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        margin-bottom: 0.9rem;
        transition: box-shadow 0.15s ease, transform 0.15s ease;
    }

    .card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transform: translateY(-1px);
    }

    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }

    .bottom-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: var(--bottom-bg);
        color: var(--bottom-text);
        padding: 12px;
        text-align: center;
        border-top: 1px solid var(--bottom-border);
        box-shadow: 0 -2px 6px rgba(0,0,0,0.08);
        z-index: 999;
    }

    /* Switch styling */
    .switch-container {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
    }

    .switch-label {
        font-size: 0.9rem;
        font-weight: 500;
    }

    .switch {
        position: relative;
        display: inline-block;
        width: 46px;
        height: 24px;
    }

    .switch input { display: none; }

    .slider {
        position: absolute;
        cursor: pointer;
        top: 0; left: 0;
        right: 0; bottom: 0;
        background-color: #ccc;
        transition: .3s;
        border-radius: 24px;
    }

    .slider:before {
        position: absolute;
        content: "";
        height: 18px;
        width: 18px;
        left: 3px;
        bottom: 3px;
        background-color: white;
        transition: .3s;
        border-radius: 50%;
    }

    input:checked + .slider {
        background-color: #4ade80;
    }

    input:checked + .slider:before {
        transform: translateX(22px);
    }

</style>
""", unsafe_allow_html=True)

# theme switcher in sidebar
st.sidebar.markdown("<div class='switch-container'><span class='switch-label'>Dark Mode</span>", unsafe_allow_html=True)
dark_mode = st.sidebar.checkbox("", key="dark_mode_switch")
st.sidebar.markdown("</div>", unsafe_allow_html=True)

theme_choice = st.sidebar.selectbox("Accent Theme", ["Light", "Green"])

if dark_mode:
    theme = "Dark"
else:
    theme = theme_choice

if theme == "Light":
    st.markdown("""
    <style>
        :root {
            --card-bg: #ffffff;
            --card-border: #e5e7eb;
            --bottom-bg: #ffffff;
            --bottom-text: #111827;
            --bottom-border: #e5e7eb;
        }
    </style>
    """, unsafe_allow_html=True)

elif theme == "Dark":
    st.markdown("""
    <style>
        :root {
            --card-bg: #1f2937;
            --card-border: #374151;
            --bottom-bg: #1f2937;
            --bottom-text: #f3f4f6;
            --bottom-border: #374151;
        }
    </style>
    """, unsafe_allow_html=True)

else:  # Green theme
    st.markdown("""
    <style>
        :root {
            --card-bg: #ffffff;
            --card-border: #c7e8ca;
            --bottom-bg: #0b6e4f;
            --bottom-text: #ffffff;
            --bottom-border: #0b6e4f;
        }
    </style>
    """, unsafe_allow_html=True)


st.title("ShopperPath – Shopping Buying Assistant")

# file uploader
uploaded_file = st.file_uploader("Upload your order CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    try:
        df = validate_and_clean(df)
    except Exception as e:
        st.error(f"CSV Error: {e}")
        st.stop()

    st.markdown("<div class='section-header'>Order Preview</div>", unsafe_allow_html=True)
    st.dataframe(df)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Overview", "Route", "Item Interpreter", "Substitutions", "Stock Risk", "Report"
    ])

    # overview tab
    with tab1:
        st.markdown("<div class='section-header'>🛒 Overview</div>", unsafe_allow_html=True)

        total_items = len(df)
        unique_categories = df["category"].nunique()
        unique_brands = df["brand"].nunique()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Items", total_items)
        col2.metric("Categories", unique_categories)
        col3.metric("Brands", unique_brands)

        st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='card'><b>Items by Category</b></div>", unsafe_allow_html=True)
        st.dataframe(df.groupby("category")["item_name"].count().reset_index())

    # route optimization tab
    with tab2:
        st.markdown("<div class='section-header'>🧭 Route</div>", unsafe_allow_html=True)

        if st.button("Generate Route"):
            with st.spinner("Optimizing route..."):
                route, total_time = generate_route(df)
                st.session_state["route_results"] = (route, total_time)

        if "route_results" in st.session_state:
            route, total_time = st.session_state["route_results"]

            st.markdown(
                f"<div class='card'><b>Estimated Time:</b> {total_time} minutes</div>",
                unsafe_allow_html=True
            )

            for section in route:
                st.markdown(f"""
                <div class='card'>
                    <b>{section['aisle']}</b><br>
                    {section['num_items']} item(s)<br>
                    <span class='badge' style="background:#D1FAE5;color:#065F46;">
                        {section['time_estimate']} min
                    </span>
                    <br><br>
                    {', '.join(section['items'])}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Click 'Generate Route' to see the optimized picking order.")

    # item interpretation tab
    with tab3:
        st.markdown("<div class='section-header'>🔍 Item Interpretation</div>", unsafe_allow_html=True)

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
                st.markdown(f"<div class='card'><b>{item}</b></div>", unsafe_allow_html=True)
                st.code(format_json_output(interpretation), language="json")
        else:
            st.info("Click 'Interpret Items' to generate item insights.")

    # substitutions tab
    with tab4:
        st.markdown("<div class='section-header'>🔄 Substitutions</div>", unsafe_allow_html=True)

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
                confidence = result.get("confidence", "Medium")

                if confidence == "High":
                    bg = "#D1FAE5"
                    color = "#065F46"
                else:
                    bg = "#FEF3C7"
                    color = "#92400E"

                st.markdown(f"""
                <div class='card'>
                    <b>{item}</b><br><br>
                    <span style="
                        background:{bg};
                        color:{color};
                        padding:4px 10px;
                        border-radius:8px;
                        font-size:0.75rem;
                        font-weight:600;
                    ">
                        {confidence} Confidence
                    </span>
                </div>
                """, unsafe_allow_html=True)

                st.code(format_json_output(result), language="json")
        else:
            st.info("Click 'Generate Substitutions' to generate alternatives.")

    # stock risk tab
    with tab5:
        st.markdown("<div class='section-header'>⚠️ Stock Risk</div>", unsafe_allow_html=True)

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
                risk_level = result.get("risk_level", "Medium")

                if risk_level == "High":
                    style = "border-left: 6px solid #EF4444;"
                elif risk_level == "Medium":
                    style = "border-left: 6px solid #F59E0B;"
                else:
                    style = "border-left: 6px solid #10B981;"

                st.markdown(f"""
                <div class='card' style="{style}">
                    <b>{item}</b><br><br>
                    Risk Level: {risk_level}<br><br>
                </div>
                """, unsafe_allow_html=True)

                st.code(format_json_output(result), language="json")
        else:
            st.info("Click 'Predict Stock Risk' to generate risk insights.")

    # report tab
    with tab6:
        st.markdown("<div class='section-header'>📄 Report</div>", unsafe_allow_html=True)

        if st.button("Generate Report"):
            with st.spinner("Compiling report..."):
                sample_items = df['item_name'].tolist()[:10]

                report_prompt = f"""
                Create a concise summary of this order.
                Include:
                - Order type
                - Key categories
                - Items needing attention
                - Suggested shopping strategy

                Items: {sample_items}
                """

                report = interpret_item(
                    item_name="Order Report",
                    category="N/A",
                    dietary_tags="N/A",
                    customer_notes=report_prompt
                )

                st.session_state["report"] = report

        if "report" in st.session_state:
            st.markdown("<div class='card'><b>Order Report</b></div>", unsafe_allow_html=True)
            st.write(st.session_state["report"])
        else:
            st.info("Click to generate a summary.")

    # flaoting bottom bar for mobile users
    st.markdown("""
    <div class='bottom-bar'>
        ShopperPath is optimized for mobile — scroll up to continue.
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("Upload a CSV to begin.")