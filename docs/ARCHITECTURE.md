# Architecture and evidence flow

The static frontend renders a saved JSON snapshot immediately. When served by FastAPI, it detects `/api/health` and enables live operations. A separately hosted HTTPS backend can be configured in the settings drawer. A same-origin local app avoids mixed-content and CORS problems.

The backend resolves a symbol without a seed-universe lookup, retrieves normalized discovery data, fetches completed EOD bars, and warms an NSE session for filings. A 17-category rule engine ranks disclosures. Known routine categories are collapsed; unknown announcements remain material-review candidates. The snapshot has approximately 1,000 distinct filings across the captured window, not fabricated demonstration counters.

Research discovers primary presentations, results, transcripts and annual reports. At most three documents download concurrently. Bounded HTTPS fetches validate redirects and reject local-network targets. Known official domains can use the environment proxy's remote DNS; this is not a general private-network exception. PDF bytes are hashed and parsed once into page text. Sparse pages are flagged for OCR; short annual-report covering letters are classified as notices, not full reports.

A conservative financial parser requires labelled revenue, reported EBITDA, PBT and PAT rows, explicit units, and a current/prior/year-ago quarter sequence. Percentage columns are skipped rather than accidentally read as currency. Arithmetic is computed in Python. Unsupported layouts are unavailable.

Optional T2 synthesis receives primary page text, never Screener aggregates or Push biography snippets. Output is validated with Pydantic. Claims with missing documents, pages or exact quote spans are discarded. Numeric guidance verdicts are recomputed with basis and period gates. Exact-span validation checks traceability, not whether a model interpretation follows logically from its quote.

SQLite stores provider caches, content-addressed document text, settings, filings, pins and telemetry. Inference keys include prompt version, model, request, schema and evidence. The shipped seed omits complete PDF text. Raw capture intermediates and credentials are excluded from Git and the source archive.

The reviewed case is deliberately separate from the reusable engine: `scripts/build_snapshot.py` and `enhance_snapshot.py` curate primary sources, while `backend/services/` contains no ticker-specific financial outputs. Saved KPIT/Sona/HDFC findings are human-readable reviewed fixtures, not represented as unattended model results.

API reference is available at `/docs` when running locally. The backend is single-process/single-user. Polling requires the process to remain running. No external notification queue, multi-user authorization, comprehensive rate limiting, cloud job scheduler, production monitoring or provider SLA is claimed.
