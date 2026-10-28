# Prompt and reference review

Reviewed the complete master engineering prompt and both ENAM challenge PDFs. The challenge's “thin-but-working beats broad-but-broken” principle informed the implementation. This document distinguishes delivered behavior, deliberate corrections and remaining scope; it is not a claim that every master-prompt wish is complete.

| Requirement | Delivery and limits |
|---|---|
| Mobile-first Push/Pull app | Responsive desktop layout and 390×844 mobile view, bottom navigation, light/dark theme, source drawers, installable shell. |
| 18 portfolio + four research names | All 22 have real captured source packs and EOD histories. ZOMATO resolves to ETERNAL; NARAYANA resolves to NH. |
| Universal ticker ingestion | Generic NSE ticker and numeric BSE-code resolver; Screener discovery, Yahoo prices, NSE announcements and document pipeline. Live POLYCAB check passed. Direct BSE filing-feed adapter remains missing. |
| EOD alerts | Prior 20 sessions exclude alert day; absolute percentage move OR RVOL threshold; configurable sliders and categories. |
| Price-to-filing association | Highest-priority material disclosure in preceding 48 hours, ending at 15:30 IST. Clearly labelled temporal association, not causal explanation. |
| 17 categories | Deterministic taxonomy, priorities, routine drawer, optional T1 for ambiguous cases. Unknowns stay visible for review. Category-specific deal/dilution/litigation/order-value calculations are not yet generalized across every filing. |
| Results rich card | Source-reviewed Sona statutory results and KPIT result-day replay, five metrics and calculated QoQ/YoY deltas. Generic labelled presentation parser supports both inline and multiline amount/percentage grids. Arbitrary scanned tables require review. |
| Executive card | HDFC transition with primary filing and official career profile; KPIT appointment replay. Optional Push-only background-search API exists; automatic name extraction and enrichment of every new leadership filing is not fully wired. |
| Windowed digest | 24h, 3d, 7d and custom IST dates; real deduplicated document counts. Historical event replay does not inflate raw counts. |
| Business and financial snapshot | Reviewed KPIT business, reported quarterly financials, net cash, borrowings/equity and price. All requested TTM/market-cap/52-week/pledge metrics are not independently verified for every issuer. |
| Five-year / eight-quarter trajectory | KPIT revenue charts, five-year reported EBITDA-margin and ROE table. Annual revenue is explicitly USD, quarterly INR; CAGR uses four intervals. |
| Balance sheet / working capital | KPIT borrowings, cash, leases, equity and DSO. Complete inventory/payable-day series and automatic cycle-growth alerts remain gaps. |
| Three-year cash quality | Audited FY24–FY26 CFO and capex with primary EBITDA highlights; cumulative comparison, annual bars, FCF and traffic light. Acquisitions are separate from capex. |
| Four-quarter say–do audit | Reviewed KPIT case with four outcome quarters, primary promise/outcome citations and horizon/basis checks. One matured numeric observation is reported as 0/1, not a reliable personality rating. Optional generic model audit recomputes numeric verdicts in Python. |
| Forward guidance | Cited growth and margin commentary; unavailable numeric capex targets stay unknown. Historical FY27 band is not silently treated as current unchanged guidance. |
| Bull / bear | Three primary-backed points each for the reviewed case; optional generic cited synthesis. |
| Governance forensics | Primary-note and appointment review, explicit incomplete-coverage state, optional model-assisted scan. Full automated contingent-liability materiality, RPT leakage, auditor and promoter-divergence evaluation remain incomplete. |
| Audio | Browser Web Speech reads the top three signals with start/stop. Duration depends on content and voice; not falsely guaranteed to be exactly 90 seconds. |
| Thesis / IC memo | Pin findings, annotate, persist on device, export Markdown or browser print/PDF. A strict one-page PDF is not guaranteed for arbitrarily long notes. |
| Cost / latency / cache | Actual model usage ledger; PDF/HTML hashes; inference cache includes model, prompt, schema and evidence. Unknown pricing disclosed. No fabricated benchmark or sub-300ms cold-start claim. |
| Startup / deployment | Python launchers and Docker configuration; private static hosted demo. Live Python backend must run locally or on a suitable server. |
| Recommended frontend stack | Intentionally uses small dependency-free JavaScript/CSS with SVG charts rather than Next/shadcn. Python uses sqlite3 rather than SQLAlchemy. These reduce setup and build failure points; they are deviations from recommendations, not hidden substitutions. |
| Submission | Source archive, documentation, email draft and build summary supplied. Source is uploaded to Prince-svrn/FINN. A hosted saved-data demo is now deployed privately. Evaluator access, actual conversation export and sending the email remain handoff items. |

## Corrections to the prompt

1. Screener is a secondary normalized-data service. Its document links can lead to primary evidence, but its table cells do not become primary merely because a prompt calls them that.
2. Operating profit is not automatically equivalent to the issuer's reported EBITDA. Definitions, exceptional items, FX and PAT attributable to owners versus all shareholders must stay explicit.
3. A price move and a nearby filing do not establish causation. After-close disclosures are excluded from explaining that session's close.
4. Negative or zero comparison bases make ordinary growth percentages misleading; those values remain unavailable. Missing is not zero.
5. Annual guidance cannot be scored as a quarterly miss. Organic/total, constant-currency/reported, standalone/consolidated and period bases must match.
6. The prompt contains two cash thresholds: a <70% forensic screen and 60%/80% traffic-light boundaries. Both are preserved and labelled.
7. FCF uses cash purchases of PPE/intangibles. Total investing cash flow and changes in gross block are not automatically treated as cash capex.
8. A management score based on one commitment is not reliable. Sample size and excluded open/qualitative promises are disclosed.
9. The sample figures and audit matrix in the prompt are illustrative. They were not passed off as real company facts.
10. Source text is untrusted input. Embedded instructions cannot override the model's grounding rules; citations are checked against exact document/page text. Semantic review is still required.
