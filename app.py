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

    body {
        font-family: 'Inter', sans-serif;
    }

    .section-header {
        font-size: 1.4rem;
        font-weight: 600;
        margin-top: 1.8rem;
        margin-bottom: 0.6rem;
    }

    .card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
    }

    .risk-high {
        border-left: 6px solid #EF4444;
    }
    .risk-medium {
        border-left: 6px solid #F59E0B;
    }
    .risk-low {
        border-left: 6px solid #10B981;
    }

    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-green { background: #D1FAE5; color: #065F46; }
    .badge-yellow { background: #FEF3C7; color: #92400E; }
    .badge-red { background: #FEE2E2; color: #991B1B; }

</style>
""", unsafe_allow_html=True)

st.title("ShopperPath – Shopper Buying Assistant")

# file uploader   
uploaded_file = st.file_uploader("Upload your order CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Clean and validate CSV
    try:
        df = validate_and_clean(df)
    except Exception as e:
        st.error(f"CSV Error: {e}")
        st.stop()

    st.markdown("<div class='section-header'>Order Preview</div>", unsafe_allow_html=True)
    st.dataframe(df)

    # tabs for different functionalities
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Overview",
        "Route",
        "Item Interpreter",
        "Substitutions",
        "Stock Risk",
        "Shopper Report"
    ])

    # overview tab
    with tab1:
        st.markdown("<div class='section-header'>🛒 Batch Overview</div>", unsafe_allow_html=True)

        total_items = len(df)
        unique_categories = df["category"].nunique()
        unique_brands = df["brand"].nunique()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Items", total_items)
        col2.metric("Categories", unique_categories)
        col3.metric("Brands", unique_brands)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("<div class='card'><b>Items by Category</b></div>", unsafe_allow_html=True)
        st.dataframe(df.groupby("category")["item_name"].count().reset_index())

    # route optimization tab
    with tab2:
        st.markdown("<div class='section-header'>🧭 Optimized Route</div>", unsafe_allow_html=True)

        if st.button("Generate Route"):
            with st.spinner("Optimizing route..."):
                route, total_time = generate_route(df)
                st.session_state["route_results"] = (route, total_time)

        if "route_results" in st.session_state:
            route, total_time = st.session_state["route_results"]

            st.markdown(
                f"<div class='card'><b>Estimated Total Shop Time:</b> {total_time} minutes</div>",
                unsafe_allow_html=True
            )

            for section in route:
                st.markdown(f"""
                <div class='card'>
                    <b>{section['aisle']}</b><br>
                    {section['num_items']} item(s)<br>
                    <span class='badge badge-green'>{section['time_estimate']} min</span>
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

    # substitution engine tab
    with tab4:
        st.markdown("<div class='section-header'>🔄 Substitution Engine</div>", unsafe_allow_html=True)

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
                badge_color = "badge-green" if confidence == "High" else "badge-yellow"

                st.markdown(f"""
                <div class='card'>
                    <b>{item}</b><br><br>
                    <span class='badge {badge_color}'>{confidence} Confidence</span>
                </div>
                """, unsafe_allow_html=True)

                st.code(format_json_output(result), language="json")
        else:
            st.info("Click 'Generate Substitutions' to generate alternatives.")

    # stock risk predictor tab
    with tab5:
        st.markdown("<div class='section-header'>⚠️ Stock Risk Predictor</div>", unsafe_allow_html=True)

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
                risk_class = (
                    "risk-high" if risk_level == "High" else
                    "risk-medium" if risk_level == "Medium" else
                    "risk-low"
                )

                st.markdown(f"""
                <div class='card {risk_class}'>
                    <b>{item}</b><br><br>
                    Risk Level: {risk_level}<br><br>
                </div>
                """, unsafe_allow_html=True)

                st.code(format_json_output(result), language="json")
        else:
            st.info("Click 'Predict Stock Risk' to generate risk insights.")

    # shopper report tab
    with tab6:
        st.markdown("<div class='section-header'>📄 Final Shopper Report</div>", unsafe_allow_html=True)

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
            st.markdown("<div class='card'><b>Shopper Report</b></div>", unsafe_allow_html=True)
            st.write(st.session_state["shopper_report"])
        else:
            st.info("Click to generate a final summary for the entire order.")

else:
    st.info("Upload a CSV to begin.")