# FINN — Financial Investment Intelligence

A mobile-first research prototype for the ENAM AI Engineer Build Challenge. FINN ranks corporate disclosures, compares price/volume anomalies with contemporaneous filings, and builds research around traceable company evidence.

**This is a working prototype, not production-certified investment software.** The static demo serves a genuine saved dataset captured on 27 October 2026. Live provider access and optional model inference run through the included FastAPI backend. The saved snapshot does not contain an unattended Python market feed.

## Open without installation

Double-click `dist/FINN_Demo.html` in Chrome or Edge. It contains the saved data and complete interface in one file. Live refresh and arbitrary-ticker retrieval require the backend below.

**Hosted demo:** [https://finn-investment-agent-prince.safegrape512.chatgpt.site](https://finn-investment-agent-prince.safegrape512.chatgpt.site) — deployed on 28 October 2026, currently owner-private. Enable evaluator access before submitting this link. It serves the saved-data prototype; live retrieval still requires the Python backend. The source repository is [Prince-svrn/FINN](https://github.com/Prince-svrn/FINN). The source package and standalone demo are usable locally.

## Start on Windows

Install Python 3.11 or newer, extract this project, and double-click `start.cmd`. Python 3.13.15 was confirmed to start the app on the user's Windows laptop. Keep the terminal open while using FINN.

Alternatively, open PowerShell in the project folder and run:

```powershell
.\start.ps1
```

If your system blocks the script, run the commands it contains individually rather than changing machine-wide security policy. Open **http://127.0.0.1:8000**. The first launch downloads dependencies; subsequent launches reuse the virtual environment. Internet is required for installation and live data, but the saved briefing is included.

## Start on macOS / Linux

```bash
chmod +x start.sh
./start.sh
```

Alternative, with Docker Compose v2.24+:

```bash
docker compose up --build
```

Both serve the UI and API on port 8000. Stop with Ctrl+C. Docker binds the host port to localhost and retains SQLite data in a named volume. The equivalent manual startup commands were confirmed working on Windows with Python 3.13.15. The convenience launchers and Docker configuration have not been executed on their target platforms.

## Try the product

1. Open Push digest. Compare the Sona results card with its official PDF; inspect the HDFC leadership transition. Change the time window and expand routine disclosures.
2. Open Alert watch. Move the price and relative-volume sliders. Related filings stop at the market close; a later announcement cannot explain an earlier close.
3. Open Pull research → KPITTECH. Review all eight modules, especially the four-quarter audit and three-year cash conversion. Switch the trajectory to Annual for five years of dollar revenue, margin and ROE.
4. Pin evidence, add your own thesis note under Portfolio, and export Markdown or print to PDF.
5. In the local app, search **POLYCAB**, then select **Run primary research → Ingest & extract**. POLYCAB is outside the 22-stock seed. Its source tables, quotes, filings, four transcripts and primary financial grid were checked during the build.

## Optional model configuration

Copy `.env.example` to `.env`. Add a provider API key, compatible Chat Completions base URL, and T1/T2 model IDs. The adapter requires JSON-object responses and the `max_tokens` parameter; not every provider/model supports that interface. Enter current per-million-token prices for the chosen models. Missing prices are recorded as unknown, not free. Do not commit `.env`.

- T0: regex classification, parsing and arithmetic; no model charge.
- T1: ambiguous filing classification when configured.
- T2: explicitly requested primary-document synthesis, guidance audit, bull/bear and governance findings.
- Optional `BRAVE_SEARCH_API_KEY`: Push-only executive background search through `/api/executive`; it is not part of Pull research.
- `FINN_POLL_INTERVAL_SECONDS`: enable portfolio polling while the backend is running (minimum 300 seconds). Default is off.

No paid model calls or Brave calls were made during this build. Those provider integrations are implemented but not end-to-end validated with credentials. Headline classification may invoke T1 on refresh when configured. Keep polling off until you have checked usage and provider quotas.

## Contents

- `backend/`: FastAPI, financial functions, data adapters, PDF cache, model router.
- `frontend/`: editable HTML, CSS and JavaScript; no frontend package installation needed.
- `dist/`: deployable static interface and saved evidence snapshot.
- `config/universe.json`: 18 portfolio stocks and four research names.
- `config/reviewed_sources.json`: source URLs and exact hashes for the reviewed case.
- `data/seed_cache.db`: portable provider cache, excluding complete PDF text and credentials.
- `tests/`: financial, provenance, parser and API regression checks.
- `docs/`: requirement review, architecture, validation, demo, submission checklist and email draft.
- `scripts/capture_sources.py`: recreate local build inputs from public sources, subject to provider availability.
- `scripts/build_snapshot.py`: rebuild the curated case using those captured documents; run from project root. Curation is explicitly separate from the generic live engine.

To edit the UI, change `frontend/` and run `python scripts/sync_frontend.py`. The committed `dist/` is ready to serve. Run frontend request checks with `node tests/frontend_requests.cjs` (Node is needed only for this check). Run Python tests with `.venv/bin/python -m pytest tests -q` (Windows: `.\.venv\Scripts\python.exe -m pytest tests -q`).

## Source and operational limits

NSE, Yahoo and Screener can change their pages or reject requests. Stale fallback is labelled. Screener's normalized tables are retained for discovery and inspection; they are not presented as primary-company evidence in Pull conclusions. The generic parser accepts known labelled layouts and rejects unknown ones; it does not guarantee complete financial extraction for every issuer. Scanned pages are flagged for OCR/manual review. BSE numeric codes support price and document discovery, but a direct BSE announcements adapter is not implemented.

The full reviewed eight-module dossier is KPIT. Other tickers receive live discovery, supported financial extraction and optional cited model analysis, not a promise of a complete automatically audited dossier. Model citations are checked for exact text/page/hash membership; this does not prove semantic correctness. Governance coverage is partial. DSO is not misrepresented as the full cash-conversion cycle. See `docs/PROMPT_REVIEW.md` for the complete scope map.

This is a single-user app. Browser notes stay on the device; optional API storage is single-user. Before internet-hosting the backend, set `FINN_API_TOKEN`, restrict `FINN_CORS_ORIGINS`, use HTTPS and add appropriate operational controls. No brokerage connection or trade execution exists.

## Final validation pass

47 Python checks and 5 frontend request checks pass. Model-adapter tests use a mock provider and verify schema rejection, cache reuse, invalidation when evidence changes, and usage-based cost accounting; these are not a claim of a real provider test. A fresh empty-cache PIDILITIND run retrieved 64 price bars, six table sections and 12 primary documents including four transcripts in 122.7 seconds. Seven source downloads failed; no complete annual report or supported primary financial grid was retrieved for that run. See `docs/PIDILITIND_LIVE_CHECK.json`. The UI waits longer for cold company discovery, recovers after timeouts, and prevents overlapping requests from leaving controls stuck.
