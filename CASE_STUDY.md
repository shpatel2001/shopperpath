ShopperPath — Product Case Study
AI‑powered item intelligence, substitution logic, and route optimization for Instacart shoppers

Problem
Instacart shoppers operate under tight time pressure while navigating incomplete item descriptions, unpredictable stock levels, and customer expectations for accurate replacements. A single batch can contain dozens of items with vague names, missing details, or unclear preferences. Shoppers often face:
- Items that lack brand, size, or type information
- Frequent out‑of‑stock situations requiring quick judgment
- Inefficient in‑store navigation that increases batch time
- Customer dissatisfaction when substitutions don’t match intent
These challenges lead to slower batch completion, lower customer ratings, and reduced earnings. Shoppers need a tool that helps them interpret items quickly, make confident substitution decisions, and move through the store efficiently.

User
The primary user is an Instacart shopper who wants to complete batches faster and with fewer errors. They are typically:
- Time‑constrained and multitasking while shopping
- Working in unfamiliar stores or layouts
- Managing customer communication while picking items
- Motivated by speed, accuracy, and customer satisfaction
Their needs are straightforward: clear item details, smart substitution guidance, and a route that minimizes walking time.

Solution
ShopperPath is an AI‑powered assistant that transforms a shopper’s CSV batch export into structured, actionable insights. The tool provides:
- Item Interpretation: Brand, size, type, category, and dietary tags extracted from messy item names
- Substitution Engine: AI‑generated replacements with reasoning based on customer intent
- Stock‑Risk Prediction: Low/medium/high risk scoring with recommended shopper actions
- Route Optimization: A store‑friendly picking order to reduce backtracking
- Clean, mobile‑friendly UI: Designed for shoppers who are on the move
The goal is to reduce cognitive load and help shoppers complete batches faster and more accurately.

Approach
The product was scoped around a simple, repeatable workflow: upload → analyze → shop. This ensured the experience stayed fast and focused.
- Groq’s Llama‑3.1 model was selected for its speed and cost‑efficiency, enabling real‑time item interpretation and substitution logic.
- Streamlit provided a lightweight, mobile‑friendly interface that could be deployed quickly.
- A realistic dataset of Instacart‑style items was created to test parsing, substitution quality, and stock‑risk predictions.
- Each module (Interpreter, Substitutions, Stock Risk, Route Optimizer) was built as a standalone component to keep the system modular and maintainable.
This modular approach allowed rapid iteration while ensuring each feature delivered clear value on its own.

Constraints and Tradeoffs
- Cost: Groq’s free tier influenced model selection and prompt design to ensure fast, predictable responses.
- Mobile usability: The UI had to remain simple and readable on a phone, limiting complex visualizations.
- Data realism: Without access to Instacart’s internal APIs, realistic mock data and heuristics were used to simulate stock risk and route patterns.
- Scope: Advanced features like real‑time store maps, customer chat automation, and multi‑batch optimization were intentionally deferred to keep the MVP focused.
- Consistency: Strict JSON prompting was required to ensure reliable parsing across all AI modules.

Impact
ShopperPath demonstrates how AI can meaningfully improve the Instacart shopping workflow. By reducing the time spent interpreting items, choosing substitutions, and navigating the store, the tool helps shoppers:
- Complete batches faster
- Reduce errors and customer complaints
- Improve ratings and earnings
- Make more confident decisions under pressure
The project also showcases how AI can augment gig‑economy workflows by simplifying complex, high‑frequency tasks.

Future Improvements
Real‑time store integrations
Connecting to store inventory APIs or crowdsourced stock data would improve stock‑risk accuracy.
Visual route maps
Replacing list‑based routes with interactive store maps would reduce navigation time even further.
Customer preference modeling
Learning from past orders could improve substitution recommendations and personalize shopper actions.
Multi‑batch optimization
Shoppers handling multiple batches could receive combined routes and item grouping suggestions.
Barcode and image recognition
Scanning items or shelf labels could validate picks and reduce errors.
Exportable shopper reports
A one‑click summary could help shoppers track performance or share insights with customers.
Enhanced prompt engineering
More structured prompts and model‑specific tuning would improve consistency as LLMs evolve.
