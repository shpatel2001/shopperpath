import streamlit as st
import pandas as pd

from modules.route_optimizer import generate_route
from modules.ai_item_interpreter import interpret_item
from modules.ai_substitutions import generate_substitution
from modules.ai_stock_risk import predict_stock_risk
from modules.parser import validate_and_clean
from modules.utils import format_json_output

# page config
st.set_page_config(page_title="ShopperPath", layout="wide")

st.markdown(
    """
    <style>
    .app-title {
        font-size: 2.1rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .app-subtitle {
        font-size: 0.95rem;
        color: #6c757d;
        margin-bottom: 1.2rem;
    }
    .card {
        background: #ffffff;
        border-radius: 14px;
        padding: 1.1rem 1.25rem;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.06);
        margin-bottom: 1rem;
    }
    .card-header {
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    .pill {
        display: inline-block;
        padding: 0.15rem 0.55rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 500;
        background: #f3f4f6;
        color: #4b5563;
        margin-right: 0.3rem;
    }
    .pill-primary {
        background: #e0edff;
        color: #1d4ed8;
    }
    .pill-success {
        background: #dcfce7;
        color: #15803d;
    }
    .pill-warning {
        background: #fef3c7;
        color: #92400e;
    }
    .json-box {
        background: #0b1120;
        color: #e5e7eb;
        border-radius: 10px;
        padding: 0.75rem 0.9rem;
        font-family: "JetBrains Mono", "SF Mono", Menlo, monospace;
        font-size: 0.8rem;
        white-space: pre-wrap;
        word-break: break-word;
        margin-top: 0.4rem;
    }
    .section-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #9ca3af;
        margin-bottom: 0.2rem;
    }
    .stat-number {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 0.1rem;
    }
    .stat-label {
        font-size: 0.8rem;
        color: #6b7280;
    }
    .route-summary {
        padding: 0.9rem 1rem;
        background: #f3f4ff;
        border-radius: 12px;
        border: 1px solid #dbe4ff;
        margin-bottom: 1rem;
    }
    .route-summary h3 {
        margin: 0;
        font-size: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def card_header(title: str, icon: str = ""):
    return f"<div class='card-header'>{icon} {title}</div>"


def json_box(content: str):
    return f"<div class='json-box'>{content}</div>"


def aisle_card(section):
    items_html = "".join([f"<li>{item}</li>" for item in section["items"]])
    return f"""
    <div class="card">
        <div class="card-header">🛒 {section['aisle']}</div>
        <div style="margin-bottom: 0.4rem;">
            <span class="pill pill-primary">{section['num_items']} items</span>
            <span class="pill pill-success">{section['time_estimate']} min</span>
        </div>
        <ul style="margin: 0.4rem 0 0.1rem 1.1rem; padding-left: 0;">
            {items_html}
        </ul>
    </div>
    """


# title
st.markdown("<div class='app-title'>🛒 ShopperPath</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='app-subtitle'>Shopper buying assistant for faster, smarter Instacart runs.</div>",
    unsafe_allow_html=True,
)

# gile upload
uploaded_file = st.file_uploader("Upload your order CSV", type=["csv"])

if not uploaded_file:
    st.info("Upload a CSV to begin.")
    st.stop()

# loading and cleaning csv file
df = pd.read_csv(uploaded_file)

try:
    df = validate_and_clean(df)
except Exception as e:
    st.error(f"CSV Error: {e}")
    st.stop()

# order preview
st.markdown("<div class='section-label'>Order</div>", unsafe_allow_html=True)
st.markdown("<div class='card'>📄 Order preview</div>", unsafe_allow_html=True)
st.dataframe(df, use_container_width=True, hide_index=True)

# tabs for different choices
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "Overview",
        "Route",
        "Item Interpreter",
        "Substitutions",
        "Stock Risk",
        "Shopper Report",
    ]
)

# overview
with tab1:
    st.markdown("<div class='section-label'>Snapshot</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    total_items = len(df)
    unique_categories = df["category"].nunique()
    unique_brands = df["brand"].nunique()

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='stat-number'>{}</div>".format(total_items), unsafe_allow_html=True)
        st.markdown("<div class='stat-label'>Total items</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='stat-number'>{}</div>".format(unique_categories), unsafe_allow_html=True)
        st.markdown("<div class='stat-label'>Categories</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='stat-number'>{}</div>".format(unique_brands), unsafe_allow_html=True)
        st.markdown("<div class='stat-label'>Brands</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-label' style='margin-top:0.8rem;'>Breakdown</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>🛍️ Items by category</div>", unsafe_allow_html=True)
    st.dataframe(
        df.groupby("category")["item_name"].count().reset_index(name="count"),
        use_container_width=True,
        hide_index=True,
    )

# route optimizer
with tab2:
    st.markdown("<div class='section-label'>Route</div>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>🧭 Optimized store route</div>", unsafe_allow_html=True)

    if st.button("Generate Route"):
        with st.spinner("Optimizing route..."):
            route, total_time = generate_route(df)
            st.session_state["route_results"] = (route, total_time)

    if "route_results" in st.session_state:
        route, total_time = st.session_state["route_results"]

        st.markdown(
            f"""
            <div class="route-summary">
                <h3>⏱ Estimated total shop time: <strong>{total_time} minutes</strong></h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        cols = st.columns(2)
        for idx, section in enumerate(route):
            with cols[idx % 2]:
                st.markdown(aisle_card(section), unsafe_allow_html=True)
    else:
        st.info("Click **Generate Route** to see the optimized picking order.")

# item interpreter
with tab3:
    st.markdown("<div class='section-label'>AI</div>", unsafe_allow_html=True)
    st.markdown(card_header("🔍 Item interpreter"), unsafe_allow_html=True)

    if st.button("Interpret Items"):
        with st.spinner("Interpreting items..."):
            results = []
            for _, row in df.iterrows():
                result = interpret_item(
                    item_name=row["item_name"],
                    category=row["category"],
                    dietary_tags=row["dietary_tags"],
                    customer_notes=row["customer_notes"],
                )
                results.append((row["item_name"], result))
            st.session_state["interpret_results"] = results

    if "interpret_results" in st.session_state:
        for item, interpretation in st.session_state["interpret_results"]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-header'>🛍️ {item}</div>", unsafe_allow_html=True)
            st.markdown(json_box(format_json_output(interpretation)), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Click **Interpret Items** to generate item insights.")

# substitution engine
with tab4:
    st.markdown("<div class='section-label'>AI</div>", unsafe_allow_html=True)
    st.markdown(card_header("🔄 Substitution engine"), unsafe_allow_html=True)

    if st.button("Generate Substitutions"):
        with st.spinner("Generating substitutions..."):
            subs = []
            for _, row in df.iterrows():
                result = generate_substitution(
                    item_name=row["item_name"],
                    category=row["category"],
                    brand=row["brand"],
                    dietary_tags=row["dietary_tags"],
                    customer_notes=row["customer_notes"],
                )
                subs.append((row["item_name"], result))
            st.session_state["subs_results"] = subs

    if "subs_results" in st.session_state:
        for item, result in st.session_state["subs_results"]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-header'>🔁 {item}</div>", unsafe_allow_html=True)
            st.markdown(json_box(format_json_output(result)), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Click **Generate Substitutions** to generate alternatives.")

# stock risk predictor
with tab5:
    st.markdown("<div class='section-label'>AI</div>", unsafe_allow_html=True)
    st.markdown(card_header("📉 Stock risk predictor"), unsafe_allow_html=True)

    if st.button("Predict Stock Risk"):
        with st.spinner("Predicting stock risk..."):
            risks = []
            for _, row in df.iterrows():
                result = predict_stock_risk(
                    item_name=row["item_name"],
                    historical_stock_risk=row["historical_stock_risk"],
                    historical_sub_rate=row["historical_substitution_rate"],
                )
                risks.append((row["item_name"], result))
            st.session_state["risk_results"] = risks

    if "risk_results" in st.session_state:
        for item, result in st.session_state["risk_results"]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-header'>⚠️ {item}</div>", unsafe_allow_html=True)
            st.markdown(json_box(format_json_output(result)), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Click **Predict Stock Risk** to generate risk insights.")

# shopper report
with tab6:
    st.markdown("<div class='section-label'>Summary</div>", unsafe_allow_html=True)
    st.markdown(card_header("📝 Final shopper report"), unsafe_allow_html=True)

    if st.button("Generate Shopper Report"):
        with st.spinner("Compiling report..."):
            sample_items = df["item_name"].tolist()[:10]

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
                customer_notes=report_prompt,
            )

            st.session_state["shopper_report"] = report

    if "shopper_report" in st.session_state:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-header'>🧾 Shopper report</div>", unsafe_allow_html=True)
        st.write(st.session_state["shopper_report"])
        st.markdown("</div>", unsafe_allow_html=True)
    else:

        st.info("Click to generate a final summary for the entire order.")
