# ShopperPath: Product Case Study
### AI powered item intelligence, substitution logic, and route optimization for Instacart shoppers

---

## Problem
Instacart shoppers operate under tight time pressure while navigating incomplete item descriptions, unpredictable stock levels, and customer expectations for accurate replacements. A single batch can contain dozens of items with vague names, missing details, or unclear preferences. 

**Common Shopper Pain Points:**
* **Data Gaps:** Items that lack brand, size, or type information.
* **Inventory Volatility:** Frequent out-of-stock situations requiring quick judgment.
* **Inefficiency:** In-store navigation that increases batch time.
* **Communication Friction:** Customer dissatisfaction when substitutions do not match intent.

> These challenges lead to slower batch completion, lower customer ratings, and reduced earnings. Shoppers need a tool that helps them interpret items quickly, make confident substitution decisions, and move through the store efficiently.

---

## The User
The primary user is an Instacart shopper who wants to complete batches faster and with fewer errors. They are typically:

* **Time-Constrained:** Multitasking while shopping under strict deadlines.
* **Adaptable:** Often working in unfamiliar stores or changing layouts.
* **Customer-Facing:** Managing active communication while picking items.
* **Goal-Oriented:** Motivated by speed, accuracy, and high customer satisfaction ratings.

---

## Solution
**ShopperPath** is an AI-powered assistant that transforms a shopper’s CSV batch export into structured, actionable insights. 

### Key Features
* **Item Interpretation:** Extracts brand, size, type, category, and dietary tags from messy item names.
* **Substitution Engine:** AI-generated replacements with reasoning based on customer intent.
* **Stock-Risk Prediction:** Low, medium, or high risk scoring with recommended shopper actions.
* **Route Optimization:** A store-friendly picking order to reduce backtracking.
* **Mobile-Friendly UI:** Designed specifically for shoppers on the move.

---

## 🛠 Approach & Implementation
The product was scoped around a simple, repeatable workflow: **Upload → Analyze → Shop.**

* **LLM Engine:** Groq’s Llama-3.1 was selected for its speed and cost-efficiency.
* **Interface:** Streamlit provided a lightweight, mobile-responsive frontend.
* **Modularity:** Each module (Interpreter, Substitutions, Stock Risk, Route Optimizer) was built as a standalone component for rapid iteration.

---

## Constraints & Tradeoffs
* **Cost:** Groq’s free tier influenced model selection to ensure fast, predictable responses.
* **Usability:** The UI remained focused on readability on mobile devices, limiting complex data visualizations.
* **Scope:** Real-time store maps and customer chat automation were deferred to keep the MVP focused on core logic.

---

## Impact & Future
ShopperPath demonstrates how AI can meaningfully improve the gig-economy workflow by:
1. **Speed:** Completing batches significantly faster.
2. **Accuracy:** Reducing errors and customer complaints.
3. **Earnings:** Improving ratings and overall shopper efficiency.

**Next Steps:**
* Integration with real-time store inventory APIs.
* Visual interactive route maps.
* Barcode and image recognition for pick validation.
