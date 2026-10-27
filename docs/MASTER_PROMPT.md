# Master Engineering Specification & Autonomous Build Prompt: FINN (Financial Investment Agent)

> **Instructions for GPT Astra / Autonomous Coding Agent:**
> You are tasked with architecting, implementing, and verifying **FINN (Financial Investment Agent)**—a production-grade, mobile-first financial intelligence web application built for the **ENAM Holdings AI Engineer Build Challenge**. Every functional requirement, data model, mathematical formula, UI component, LLM routing rule, and system prompt is pre-specified below so you can spend 100% of your compute writing clean, working, bug-free code rather than speculating on features. Follow this specification deterministically.

---

## 1. System Identity, Philosophy & Hard Constraints

1. **Core Problem Statement:** Public-markets investors are drowning in raw information (prices, NSE/BSE corporate filings, quarterly results, concall transcripts). The scarce skill is **filtering, not aggregating**—surfacing the 5% of material disclosures that move stocks and burying the 95% of routine compliance noise.
2. **Product Paradigm ("No AI Slop"):**
   - **Strictly Prohibited:** Conversational fluff ("Sure! Here is an analysis of..."), generic markdown paragraphs, ungrounded claims, or giant chat bubbles.
   - **Required:** High-density, structured financial cards, tabular sparklines, exact QoQ/YoY deltas in basis points (`bps`) and percentages (`%`), explicit primary-source citations (`[Source: Q3FY26 Concall, p. 14]`), and a thumb-friendly mobile viewport (`max-width: 430px` centered on desktop with a sleek mobile bezel toggle, or native responsive mobile layout).
3. **Strict Primary-Source Discipline (Pull Mode):**
   - All on-demand ("Pull") company research **must** be grounded strictly in primary company disclosures (Annual Reports, Quarterly Results Filings, Investor Presentations, and Earnings Call Transcripts fetched from `screener.in` or NSE/BSE).
   - **Zero Secondary Contamination:** Never use broker reports, news opinion articles, or pre-trained LLM memory to fabricate financial metrics. Every analytical assertion in Pull Mode must carry an inline citation badge linking to the exact primary document and section/page.
   - *Exception:* Secondary web enrichment (e.g., LinkedIn/web search for an incoming CEO/CFO's prior career history) is **explicitly permitted and required** on the **Push** side for `management_change` alerts.
4. **Generalisation Engine Requirement:**
   - Pre-configure the app with a 18-stock diversified NSE Mock Portfolio and 4 Ad-Hoc Research stocks.
   - **Crucial Grading Constraint:** The ingestion and research engine **must not be hard-coded** to these 22 tickers. It must dynamically accept **any valid NSE/BSE ticker symbol** (e.g., entered via the Pull command bar), resolve its Yahoo Finance ticker (`{SYMBOL}.NS` / `{SYMBOL}.BO`) and `screener.in/company/{SYMBOL}/consolidated/` URL on the fly, scrape/ingest the live primary data, and run the full pipeline.

---

## 2. Recommended Tech Stack & Monorepo Architecture

Build a clean, modular application that runs reliably with a single startup script (`docker-compose up` or `./start.sh`):

- **Frontend (Mobile-First PWA):** Next.js 14+ (App Router, TypeScript), Tailwind CSS, `shadcn/ui` primitives, `lucide-react` icons, `framer-motion` (for swipeable triage cards and bottom-sheet drawers), and `lightweight-charts` or `recharts` for sparklines and multi-year trajectory plots.
- **Backend API & Scraping Engine:** Python 3.11+ with **FastAPI**, `yfinance` (EOD price/volume), `httpx` + `BeautifulSoup4` / `playwright` (for NSE/BSE corporate announcements and `screener.in` fundamentals/concall links), `pypdf` / `pdfplumber` (for fast PDF text & table extraction from filings/transcripts).
- **Database & Caching Layer (Bonus Points for Cost/Speed Efficiency):**
  - **SQLite** (via SQLAlchemy/SQLModel) for structured relational storage of portfolios, EOD price series, classified filings, user alert thresholds, and cached LLM outputs.
  - **Content-Addressable SHA-256 Cache:** Hash every downloaded PDF/HTML fragment (`sha256(raw_bytes)`). Never re-parse or re-run LLM extraction on a document that has already been processed.
- **Smart Tiered Model Router (`llm_router.py`):**
  - **Tier 0 (Deterministic Regex & Rule Engine — $0 cost, <5ms):** Classify obvious `unclassified` noise (e.g., "Closure of Trading Window", "Loss of Share Certificate", "Regulation 74(5)") and parse tabular HTML numbers from Screener without calling an LLM.
  - **Tier 1 (Fast/Cheap Extraction Model — e.g., `gemini-2.5-flash` or `gpt-4o-mini`):** Classify ambiguous NSE announcements into the 17 canonical categories, extract headline QoQ/YoY tables from quarterly result PDFs, and summarize executive bios.
  - **Tier 2 (Frontier Reasoning Model — e.g., `gemini-2.5-pro`, `claude-3-5-sonnet`, or `gpt-4o`):** Reserved strictly for complex Pull-mode synthesis: **4-Quarter Narrative vs. Numbers Audit**, **Forensic Red-Flag Scanner**, and **Evidence-Backed Bull vs. Bear Debate**.
  - **Cost & Token Telemetry Tracker:** Log input tokens, output tokens, cache hits, and estimated USD cost for every request and expose it in the UI header (`⚡ Cost Telemetry Badge`) to directly earn the brief's efficiency bonus points.

---

## 3. Pre-Configured Universe (Plus Dynamic Ticker Support)

Seed `config/universe.json` with the following **18 NSE Portfolio Stocks** (spanning Large, Mid, and Small Cap across 8 sectors) and **4 Ad-Hoc Demo Stocks**, while allowing any arbitrary NSE symbol (`[A-Z0-9&-]+`) to be queried dynamically:

| Group | Sector | NSE Symbol | Yahoo Ticker | Company Name | Market Cap Tier |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Portfolio (18)** | Banking & Finance | `HDFCBANK` | `HDFCBANK.NS` | HDFC Bank Ltd. | Large Cap |
| **Portfolio** | Banking & Finance | `BAJFINANCE` | `BAJFINANCE.NS` | Bajaj Finance Ltd. | Large Cap |
| **Portfolio** | Banking & Finance | `CDSL` | `CDSL.NS` | Central Depository Services | Mid Cap |
| **Portfolio** | IT & SaaS | `TCS` | `TCS.NS` | Tata Consultancy Services | Large Cap |
| **Portfolio** | IT & SaaS | `KPITTECH` | `KPITTECH.NS` | KPIT Technologies Ltd. | Mid Cap |
| **Portfolio** | IT & SaaS | `RATEGAIN` | `RATEGAIN.NS` | RateGain Travel Technologies | Small Cap |
| **Portfolio** | Industrials & Defense | `LT` | `LT.NS` | Larsen & Toubro Ltd. | Large Cap |
| **Portfolio** | Industrials & Defense | `HAL` | `HAL.NS` | Hindustan Aeronautics Ltd. | Large Cap |
| **Portfolio** | Industrials & Defense | `KAYNES` | `KAYNES.NS` | Kaynes Technology India Ltd. | Mid Cap |
| **Portfolio** | Auto & EV | `M&M` | `M&M.NS` | Mahindra & Mahindra Ltd. | Large Cap |
| **Portfolio** | Auto & EV | `SONACOMS` | `SONACOMS.NS` | Sona BLW Precision Forgings | Mid Cap |
| **Portfolio** | Pharma & Healthcare | `SUNPHARMA` | `SUNPHARMA.NS` | Sun Pharmaceutical Industries | Large Cap |
| **Portfolio** | Pharma & Healthcare | `MAXHEALTH` | `MAXHEALTH.NS` | Max Healthcare Institute | Large Cap |
| **Portfolio** | Consumer & Retail | `TRENT` | `TRENT.NS` | Trent Ltd. | Large Cap |
| **Portfolio** | Consumer & Retail | `TITAN` | `TITAN.NS` | Titan Company Ltd. | Large Cap |
| **Portfolio** | Energy & Conglomerate | `RELIANCE` | `RELIANCE.NS` | Reliance Industries Ltd. | Large Cap |
| **Portfolio** | Chemicals & Specialty | `DEEPAKNTR` | `DEEPAKNTR.NS` | Deepak Nitrite Ltd. | Mid Cap |
| **Portfolio** | EMS & Manufacturing | `DIXON` | `DIXON.NS` | Dixon Technologies (India) | Mid Cap |
| **Ad-Hoc (4)** | New-Age Tech | `ZOMATO` | `ZOMATO.NS` | Eternal / Zomato Ltd. | Large Cap |
| **Ad-Hoc** | Hospitality | `INDHOTEL` | `INDHOTEL.NS` | The Indian Hotels Company | Large Cap |
| **Ad-Hoc** | Capital Goods | `ABB` | `ABB.NS` | ABB India Ltd. | Large Cap |
| **Ad-Hoc** | Healthcare | `NARAYANA` | `NARAYANA.NS` | Narayana Hrudayalaya Ltd. | Mid Cap |

---

## 4. Backend Data Pipelines & Mathematical Formulas

### 4.1 Pipeline A: End-of-Day (EOD) Price, Volume & Anomaly Engine (`services/eod_service.py`)
Fetch the last 30 trading days of OHLCV data using `yfinance` (`Ticker(f"{symbol}.NS").history(period="2mo", interval="1d")`). Compute and store:

1. **Daily Price Change (%):**
   $$\Delta P_{\%} = \left( \frac{\text{Close}_t - \text{Close}_{t-1}}{\text{Close}_{t-1}} \right) \times 100$$
2. **20-Day Moving Average Volume ($\text{ADV}_{20}$):**
   $$\text{ADV}_{20} = \frac{1}{20} \sum_{i=1}^{20} \text{Volume}_{t-i}$$
3. **Relative Volume Multiplier ($\text{RVOL}$):**
   $$\text{RVOL}_t = \frac{\text{Volume}_t}{\text{ADV}_{20}}$$
4. **Configurable Anomaly Trigger:**
   - Default thresholds (stored in `user_settings` table and editable via mobile slider): `price_threshold_pct = 3.0%` ($\pm X\%$), `volume_multiplier_threshold = 2.0x` ($2\times$).
   - Trigger an alert whenever $|\Delta P_{\%}| \ge \text{price\_threshold\_pct}$ **OR** $\text{RVOL}_t \ge \text{volume\_multiplier\_threshold}$.
   - **Auto-Correlated Price-to-Filing Attribution (Differentiating Feature):** When an EOD price/volume alert triggers on day $t$, automatically query the `announcements` table for that ticker within $[t - 48\text{ hours}, t]$ and attach the highest-priority material filing directly to the EOD anomaly card so the investor immediately sees *why* the stock moved.

### 4.2 Pipeline B: NSE/BSE Corporate Announcements & 17-Category Classifier (`services/filings_service.py`)
1. **Ingestion:** Fetch live corporate announcements from NSE (`https://www.nseindia.com/api/corporate-announcements?index=equities&symbol={SYMBOL}` using a session-cookie-warmed `httpx.AsyncClient` with realistic User-Agent headers) and/or BSE corporate filing feeds, plus a deterministic local seed fallback (`data/sample_nse_filings.json`) so the demo never breaks if exchange rate-limits occur during grading.
2. **The 17 Canonical Categories & Materiality Priority Scoring:**
   Map every announcement into one of the 17 reference categories, assign a **Materiality Tier (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW_NOISE`)**, and compute a **Priority Score (0–100)**:

| Category ID | Materiality Tier | Base Score | Trigger / Routing Rule & Required Push Presentation |
| :--- | :--- | :--- | :--- |
| `results` | `CRITICAL` | 95 | **Rich Card Required:** Parse PDF/filing and render a structured table of **Revenue, EBITDA, PBT, PAT** + **EBITDA Margin (%)** with exact **QoQ (%)** and **YoY (%)** deltas and a 1-line beat/miss takeaway. |
| `M&A` | `CRITICAL` | 92 | Acquisitions, mergers, demergers, JVs, subsidiary stake sales. Extract deal value (₹ Cr), valuation multiple, and strategic rationale. |
| `management_change` | `CRITICAL` | 90 | **Rich Card Required:** CEO, CFO, MD, or Director appointment/resignation. Identify outgoing vs. incoming executive and run automated web/LinkedIn enrichment to attach a 2–3 sentence career pedigree bio of the incoming leader. |
| `litigation` | `HIGH` | 85 | Tax demands, regulatory orders (SEBI/RBI), penalties, insolvency. Calculate **Materiality % of PAT** ($\text{Claim Amount} \div \text{Trailing 12M PAT}$). |
| `fund_raise` | `HIGH` | 82 | QIPs, rights issues, preferential allotments, commercial paper, buybacks. State dilution % or buyback size. |
| `capex` | `HIGH` | 80 | New plant, capacity expansion. Extract ₹ Cr spend, capacity addition, and target commissioning date. |
| `pledging` | `HIGH` | 78 | Promoter pledging or releasing shares. Highlight change in encumbered promoter holding (%). |
| `credit_rating` | `MEDIUM` | 72 | Rating upgrade, downgrade, or reaffirmation by CRISIL/ICRA/CARE. Show old vs. new rating and outlook. |
| `insider_trading` | `MEDIUM` | 70 | Promoter/KMP open-market buy/sell. Show transaction value (₹ Cr) and mode (Market Purchase vs. ESOP). |
| `earnings_call` | `MEDIUM` | 68 | Concall notice, audio link, or **Concall Transcript**. If transcript PDF is attached, auto-extract top 3 analyst Q&A pushbacks. |
| `press_release` | `MEDIUM` | 65 | Order wins (calculate Order Value $\div$ Annual Revenue %), product launches, partnerships, rumour clarifications. |
| `dividend` | `MEDIUM` | 60 | Cash dividend per share (₹), implied dividend yield (%), and **Record Date**. |
| `bonus_split` | `MEDIUM` | 58 | Bonus ratio or stock split ratio and Record Date. |
| `investor_meetings` | `LOW_NOISE` | 35 | Intimation of institutional investor/fund conference schedule. One-line summary; collapsed by default. |
| `postal_ballot` | `LOW_NOISE` | 25 | Postal ballot notice or voting results. Collapsed unless resolution fails or institutional dissent >20%. |
| `agm_egm` | `LOW_NOISE` | 25 | AGM/EGM notice or outcome. Collapsed by default. |
| `unclassified` | `LOW_NOISE` | 10 | Newspaper advertisements, Reg 74(5) demat certificates, trading window closures, duplicate share certificates, routine ESOP allotments. **Buried inside "Routine Compliance Drawer (Collapsed)".** |

### 4.3 Pipeline C: Primary-Source Fundamental Scraper (`services/screener_service.py`)
Given any NSE symbol `{SYMBOL}`:
1. Fetch `https://www.screener.in/company/{SYMBOL}/consolidated/` (falling back to standalone `https://www.screener.in/company/{SYMBOL}/` if consolidated is empty).
2. Deterministically parse HTML tables into structured JSON:
   - **Quarterly Results Table** (last 8–12 quarters): Sales/Revenue, Expenses, Operating Profit (EBITDA), OPM %, Other Income, Interest, Depreciation, PBT, Tax %, Net Profit (PAT), EPS.
   - **Annual Profit & Loss Table** (last 5–10 years): Revenue, EBITDA, PAT, Dividend Payout %.
   - **Balance Sheet Table**: Equity Share Capital, Reserves, Total Borrowings (Debt), Other Liabilities, Fixed Assets, CWIP, Investments, Trade Receivables, Inventory, Cash & Equivalents.
   - **Cash Flow Table**: Cash from Operating Activities (CFO), Cash from Investing Activities (CFI), Cash from Financing Activities (CFF).
   - **Ratios Table**: Debtor Days, Inventory Days, Days Payable, Cash Conversion Cycle (Working Capital Days), Working Capital to Sales %, ROCE %, ROE %.
   - **Shareholding Pattern Table**: Promoter %, FII %, DII %, Public %, and **Pledged Percentage** (if available).
   - **Documents Section**: Extract direct PDF URLs for the latest **Annual Reports** (last 3 years), **Concall Transcripts** (last 4 quarters), and **Investor Presentations**.
3. **Derived Fundamental Ratios (computed in Python, never guessed by LLM):**
   - $\text{Debt-to-Equity (D/E)} = \frac{\text{Total Borrowings}}{\text{Share Capital} + \text{Reserves}}$
   - $\text{EBITDA Margin (\%)} = \left(\frac{\text{Operating Profit}}{\text{Revenue}}\right) \times 100$
   - $\text{PAT Margin (\%)} = \left(\frac{\text{Net Profit}}{\text{Revenue}}\right) \times 100$
   - $\text{Cash Conversion Ratio} = \frac{\text{Operating Cash Flow (CFO)}}{\text{EBITDA}}$ (Flag `< 0.70` over 3-year cumulative period as a **Cash Conversion Red Flag**).
   - $\text{Free Cash Flow (FCF)} = \text{CFO} - \text{Capex}$ (where Capex is extracted from cash flow investing line or $\Delta \text{Gross Block} + \Delta \text{CWIP}$).

---

## 5. Mode 1: "Push" Specification (Proactive Intelligence)

Design the Push tab (`/` default mobile view) with two sub-views and a custom interactive workflow:

### 5.1 Sub-View A: The Windowed Digest (`24h` | `3d` | `7d` | `Custom Date Range`)
- **Top Signal Summary Bar:** Displays: `"142 raw filings ingested → 134 routine buried (94% noise reduction) → 8 Material Signals requiring attention"`.
- **Priority Stream (Material Signals First):** Renders cards sorted by `Priority Score` descending.
- **Special Card 1 — `results` (Quarterly Results First-Cut Card):**
  - Renders a compact, scannable financial grid directly inside the push card:
  
  | Metric (₹ Cr) | Current Q | Prev Q | YoY Q | QoQ % | YoY % |
  | :--- | ---: | ---: | ---: | ---: | ---: |
  | **Revenue** | 6,420 | 5,980 | 5,410 | +7.4% | +18.7% |
  | **EBITDA** | 1,284 | 1,136 | 1,028 | +13.0% | +24.9% |
  | **EBITDA Margin** | 20.0% | 19.0% | 19.0% | +100 bps | +100 bps |
  | **PBT** | 1,110 | 980 | 890 | +13.3% | +24.7% |
  | **PAT** | 832 | 735 | 668 | +13.2% | +24.6% |

  - Includes a 1-sentence primary-source takeaway and a `[View Official NSE PDF]` link.
- **Special Card 2 — `management_change` (Executive Pedigree Card):**
  - Displays a clean transition badge: `Role: Chief Financial Officer | Outgoing: [Name] → Incoming: [Name] (Effective: [Date])`.
  - **Enriched Bio Box:** Automatically queries web/LinkedIn data for the incoming person and displays a structured 3-bullet background (`Prior Role & Company`, `Core Domain Expertise / Track Record`, `Education / Credentials`).
- **Collapsed Noise Drawer (Bottom of Feed):**
  - A single collapsible accordion labeled `"94 Routine Filings Hidden (ESOPs, Reg 74(5), Trading Window, Notices)"`. Tapping expands a compact 1-line table for auditability without cluttering the main feed.

### 5.2 Sub-View B: Configurable Triggered Alerts & Anomaly Watch
- **Interactive Threshold Drawer:**
  - **Price Move Slider:** $\pm 1.0\%$ to $\pm 10.0\%$ (default $\pm 3.0\%$).
  - **Relative Volume Slider:** $1.5\times$ to $5.0\times$ 20-day average volume (default $2.0\times$).
  - **Category Toggles:** Checkboxes for which announcement categories trigger instant push alerts (`results`, `M&A`, `management_change`, `litigation`, `capex`, `pledging`, `fund_raise` enabled by default).
- **Correlated EOD Anomaly Cards:** Shows ticker, EOD close price, $\Delta P_{\%}$ badge, $\text{RVOL}$ bar (e.g., `3.4x 20d Avg Vol`), and the **Auto-Matched Exchange Filing** (or `"Unexplained Volume Spike — Zero NSE/BSE filings in last 48h"` if no filing exists, which is itself a crucial institutional signal).

---

## 6. Mode 2: "Pull" Specification (On-Demand Primary-Source Research)

When the user taps a portfolio ticker or types **any NSE ticker** (e.g., `ZOMATO`, `TRENT`, `POLYCAB`) into the Pull Command Bar, render a unified, mobile-first **8-Module Fundamental Dossier** grounded 100% in primary data (`screener.in` tables + downloaded Annual Reports + Concall Transcripts):

1. **Module 1 — Business Snapshot:**
   - Core business model, revenue mix by segment and geography (extracted from the latest Annual Report / Investor Presentation), and key operating KPIs.
2. **Module 2 — Financial Snapshot (At-a-Glance Grid):**
   - Market Cap, Current Price, 52W High/Low, TTM Revenue, TTM EBITDA Margin, TTM PAT, ROCE %, ROE %, D/E Ratio, Pledged %.
3. **Module 3 — Multi-Year Trajectory (5-Year Sparkline Table):**
   - Interactive toggle between **Annual (5Y)** and **Quarterly (8Q)** trends showing Revenue CAGR, EBITDA Margin expansion/compression (in `bps`), and ROE trajectory, flagging explicitly what is accelerating vs. compressing.
4. **Module 4 — Balance Sheet & Working Capital Cycle:**
   - Total Debt trend, Debt-to-Equity (D/E), funding structure, and the **Working Capital Cycle breakdown** (`Debtor Days + Inventory Days - Payable Days = Net Working Capital Days`). Automatically warn if the working capital cycle is lengthening faster than revenue growth.
5. **Module 5 — Cash Quality & Conversion Forensics:**
   - Plots **Cumulative 3Y CFO vs. Cumulative 3Y EBITDA** and **Free Cash Flow (FCF = CFO − Capex)**. Displays a clear traffic-light badge (`GREEN: CFO/EBITDA > 80%`, `AMBER: 60–80%`, `RED: < 60% — Accounting profits not converting to cash`).
6. **Module 6 — Narrative vs. Numbers (The 4-Quarter Say-Do Audit Matrix — Flagship Module):**
   - Implements the exact worked example valued most in the brief. Extracts management's explicit headline guidance and growth/margin commentary from the **last 4 quarterly concall transcripts** and compares it side-by-side against **actual delivered quarterly numbers**:

   | Quarter | Management Guidance / Promise (Primary Source Quote) | Actual Delivered Metric (Primary Filing) | Verdict & Credibility Delta |
   | :--- | :--- | :--- | :--- |
   | **Q4 FY25** | *"Expect 18–20% YoY revenue growth and EBITDA margin above 19%."* `[Q3FY25 Concall, p.6]` | Rev: **+19.4% YoY**, EBITDA Margin: **19.6%** `[Q4FY25 Results]` | **BEAT (+60 bps)** |
   | **Q1 FY26** | *"Working capital days will normalize below 65 days by Q1."* `[Q4FY25 Concall, p.11]` | WC Cycle rose to **78 days** `[AR FY25 / Q1 Filing]` | **MISSED (+13 days slip)** |

   - Computes an overall **Management Credibility Score (0–100%)** based on historical guidance accuracy.
7. **Module 7 — Forward Guidance Tracker:**
   - Bulleted table of active management guidance for the upcoming 1–2 fiscal years across **Revenue Growth**, **Margin Band**, **Capex Outlay (₹ Cr)**, and **New Capacity / Store Additions**, each with an exact transcript page citation.
8. **Module 8 — Evidence-Backed Bull vs. Bear Case:**
   - Side-by-side (or swipeable mobile toggle) **3-Point Bull Case** vs. **3-Point Bear Case**. Every bullet must cite a specific primary metric or transcript admission—zero generic macro filler.

---

## 7. High-Signal Differentiating Features (To Stand Out in Grading)

Include these four investor-workflow innovations to demonstrate strong product instinct:

1. **Forensic Red-Flag & Governance Scanner (Pull Mode Bonus Tab):**
   - Scans Annual Report notes and shareholding tables for the exact red flags highlighted in the Reference Glossary:
     - **Contingent Liabilities % of Net Worth** (flags if disputed tax/legal claims exceed 10% of equity).
     - **Related-Party Transactions (RPT) Leakage Check** (flags royalty/rent/loans to promoter entities).
     - **Auditor Qualifications / Emphasis of Matter** (checks auditor report text for non-clean sign-offs).
     - **Promoter Pledging & Insider Selling Divergence** (flags when promoters pledge or sell shares while giving bullish concall guidance).
2. **90-Second "Morning Commute" Audio Podcast Brief (Mobile Voice UX):**
   - A sticky floating play button on the Push Digest that synthesizes the top 3 material portfolio alerts into a crisp, 90-second Bloomberg-style audio briefing using the browser's Web Speech API (`window.speechSynthesis`) or TTS endpoint, built for an investor commuting to work.
3. **One-Tap Thesis Pinboard & IC Memo Export:**
   - Every Push alert and Pull module has a `[+ Pin to Thesis]` action. Investors can pin key findings across tickers into a personal conviction log and export a 1-page structured Markdown/PDF Investment Committee (IC) note.
4. **Live Cost, Latency & Model-Routing Inspector Drawer:**
   - A tap-to-open developer telemetry pill in the top bar showing how FINN routes tasks across Tier 0 (Regex/Python), Tier 1 (Flash/Mini), and Tier 2 (Pro/Sonnet), proving the system runs on pennies while maintaining institutional accuracy.

---

## 8. System Prompts for LLM Modules

Embed these exact system prompts in `backend/prompts.py`:

### 8.1 Prompt 1: Tier-1 Filing Classifier & Results Extractor
```text
You are an institutional Indian public-markets filing analyst. Given a corporate announcement from NSE/BSE and extracted PDF text:
1. Classify the filing into EXACTLY ONE of the 17 categories: [results, M&A, fund_raise, management_change, litigation, insider_trading, earnings_call, investor_meetings, credit_rating, dividend, bonus_split, capex, press_release, postal_ballot, agm_egm, pledging, unclassified].
2. Assign a materiality_score (0-100) based on whether this disclosure could materially move the stock price or alter fundamental conviction.
3. If category == "results", extract exact numerical values (in ₹ Crore) for Revenue, EBITDA, PBT, and PAT for Current Quarter, Previous Quarter (QoQ), and Same Quarter Last Year (YoY), and compute QoQ % and YoY % changes.
4. Write a maximum 22-word high-density institutional headline (zero filler words like "The company announced that...").
Return strictly valid JSON matching the FilingAnalysisSchema.
```

### 8.2 Prompt 2: Tier-2 "Narrative vs. Numbers" 4-Quarter Audit Engine
```text
You are a forensic buy-side equity analyst. You are provided ONLY with primary company disclosures:
(A) Standardised quarterly & annual financial tables from Screener.in / NSE filings.
(B) Verbatim excerpts from the company's last 4 earnings call (concall) transcripts and Annual Report MD&A.

STRICT GROUNDING RULE: You must rely 100% on the provided primary text and numbers. Do NOT use outside memory, broker commentary, or secondary news. Every claim MUST include an inline citation badge [Source: <DocName>, <Quarter/Page>].

Task:
Compare management's explicit forward guidance and narrative commentary across the last 4 quarters against the actual reported financial numbers in subsequent quarters.
Output a structured JSON array containing:
- quarter_label
- promised_guidance_quote (verbatim or tight paraphrase with exact citation)
- delivered_actual_metric (exact reported Revenue growth %, EBITDA margin %, working capital days, or capex with citation)
- status ("BEAT" | "INLINE" | "MISSED" | "MOVED_GOALPOSTS")
- analytical_insight (1 concise sentence explaining whether management is conservative, promotional, or facing structural headwinds).
```

---

## 9. Mobile-First UI/UX & Visual Design System

- **Aesthetic Direction:** "Institutional Dark Obsidian & Warm Paper" (toggleable dark/light mode; default `#0B0F17` obsidian slate background, `#111827` card surfaces, `#1F2937` 1px crisp borders, `#10B981` emerald for beats/positive deltas, `#F43F5E` rose for misses/red flags, `#F59E0B` amber for warnings/material alerts).
- **Typography:** `Inter` or `Plus Jakarta Sans` for UI copy; `JetBrains Mono` (`tabular-nums`) for all financial tables, prices, percentages, and basis-point deltas so digits align vertically to the pixel.
- **Mobile Navigation Architecture (Bottom Sticky Bar):**
  1. `📡 Push Digest` (Windowed Digest + Routine Noise Drawer + Audio Brief)
  2. `⚡ Alert Watch` (Configurable Price/Volume Sliders + Correlated EOD Moves)
  3. `🔍 Pull Research` (Universal NSE Ticker Search + 8-Module Primary Dossier)
  4. `📌 Portfolio & Cost` (18-Stock Watchlist + Thesis Pinboard + LLM Cost Telemetry)

---

## 10. Step-by-Step Build & Verification Plan for Astra

Execute the build in this exact order to adhere to the **"Thin-but-working beats broad-but-broken"** grading rule:

1. **Step 1 (Data & Caching Core):** Build SQLite models, `yfinance` EOD fetcher, `screener.in` HTML parser, and NSE filing scraper with a pre-populated realistic offline cache (`data/seed_cache.db`) for the 22 demo stocks so the app loads instantaneously (<300ms) out of the box while supporting live fetching for any new NSE ticker.
2. **Step 2 (Tiered LLM Router):** Implement `llm_router.py` with SHA-256 caching, Tier 0 regex rules, Tier 1 extraction, Tier 2 narrative-vs-numbers synthesis, and token cost logging.
3. **Step 3 (Mobile-First Frontend — Push Mode):** Build the Windowed Digest (`24h/3d/7d`), `results` QoQ/YoY table card, `management_change` LinkedIn/web bio card, collapsible routine drawer, and configurable EOD threshold sliders.
4. **Step 4 (Mobile-First Frontend — Pull Mode):** Build the universal NSE ticker bar and the 8-Module Research View, prioritizing the **Narrative vs. Numbers 4-Quarter Audit Matrix** and **Cash Quality / Forensic Scanner**.
5. **Step 5 (Self-Test & Smoke Verification):** Verify that searching an unseeded NSE ticker (e.g., `PIDILITIND` or `POLYCAB`) dynamically fetches live EOD prices from Yahoo Finance and live fundamentals from `screener.in`, renders all charts/tables without runtime errors, and stays responsive on a `390x844` (iPhone 14/15) viewport.
