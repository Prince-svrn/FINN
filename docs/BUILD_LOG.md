# AI-assisted build record — summary

This is an honest summary of work performed in this conversation on 27 October 2026. It is **not a raw conversation export** and must not be represented as the full AI chat history requested by the challenge. Attach the actual exported/shared conversation separately before submitting.

- Read the master prompt and both challenge PDFs, including the 17 disclosure categories and finance glossary.
- Corrected stale ticker symbols and identified conflicts between primary-only research and secondary normalized tables.
- Built deterministic financial functions, SQLite caches, generic source adapters, PDF extraction, model schemas and routing, and FastAPI endpoints.
- Retrieved real source packs and EOD histories for the 22-stock universe; captured and deduplicated exchange filings.
- Reviewed KPIT presentations, transcripts and two annual reports. Matched four quarters of narrative to outcomes without fabricating comparable guidance.
- Identified annual-versus-quarter and organic-versus-total growth mismatches, preserving them in audit verdicts rather than forcing a score.
- Rendered and manually inspected Sona's scanned statutory financial table after OCR. Reconciled EBITDA and distinguished operating revenue, FX-inclusive presentation revenue and PAT ownership bases.
- Reviewed the HDFC appointment filing and official career profile for the current leadership card.
- Implemented responsive digest, alert settings, research modules, source ledger, pinboard, exports, speech briefing, themes and routing inspector.
- Tested the 390×844 viewport, threshold changes, annual charts, evidence drawer, pin workflow and missing-backend states in the browser.
- Tested an unseeded ticker, POLYCAB: six normalized table sections, 63 price bars, 1,109 exchange filings and 16 downloaded documents, including four transcripts. Adapted the generic financial parser for multiline amount/percentage columns; extracted its three-period primary P&L from PDF page 15. Identified two short annual-report notices as notices rather than full reports.
- Added automated checks for arithmetic, timestamps, source validation, unsupported layouts, settings, authentication, pin APIs and snapshot integrity.

No paid LLM inference was used. Model-generated analysis and paid web-enrichment integrations remain unverified with real credentials. Setup instructions and submission materials explain those limits.

## Final readiness pass, 27–28 October 2026

Confirmed user Windows startup on Python 3.13.15. Added `start.cmd`, longer cold-source request budgets, readable timeout recovery, overlapping-request protection, visibility of model results alongside the reviewed KPIT dossier, and restored bottom navigation in desktop phone preview. Standalone HTML is now regenerated from the editable frontend.

47 Python tests and 5 frontend request checks pass; model tests use an HTTP mock and do not validate a real paid provider. Empty-cache PIDILITIND retrieval returned 64 price bars, six table sections and 12 documents including four transcripts; seven sources failed, no complete annual report was fetched, and no supported primary financial table was extracted. These limits are retained in the live-check JSON.

The saved-data site was deployed privately on 28 October 2026. The Python backend remains local. No evaluator invitations or submission email were sent. The covering-email subject was corrected to the exact required text.

## Zero-cost setup, 28 October 2026

The owner subsequently authorized public access to the saved-data site; that change was verified. The repository remains private. The owner's local OpenAI diagnostic returned HTTP 429 / credit_balance_exhausted / insufficient_quota. Rechecked the challenge's explicit free-tier allowance and confirmed that buying API credits is not required.

Added a Gemini Free Tier setup helper, the provider-specific JSON-schema request format, an uncached connection check, safe actionable errors in the research screen, and provider-aware inference cache keys. The helper keeps T1 and polling disabled and makes no paid fallback calls. Free-tier eligibility must be checked in AI Studio; FINN cannot verify billing status from a key. Updated the download and submission notes to reflect public demo access and zero-cost setup.

60 Python tests and 6 frontend checks passed. Tests cover provider failures, no automatic retries, key-safe error handling, Gemini requests, uncached connection checks, truncated output rejection, cache separation and local configuration preservation. Tests use mock provider responses. A successful real Gemini connection and full cited synthesis remain pending the owner's eligible key. The Windows setup launcher has not been executed on Windows by the build agent.


## Gemini research-format compatibility, 28 October 2026

The owner's Free Tier project and HTTP 200 model-list request were visible in screenshots. gemini-3.8-flash timed out on a connection test; the owner switched to gemini-3.5-flash-lite and the simple JSON connection test passed. SONACOMS retrieved 18 documents including four transcripts, but full synthesis returned HTTP 400. An isolated full-schema request reproduced a list-shaped error with status INVALID_ARGUMENT and message "Request contains an invalid argument." The first diagnostic incorrectly assumed a dictionary; corrected it to reveal the provider response.

Changed Gemini requests to JSON-object mode with the schema in the prompt. Local Pydantic validation and exact-citation checks remain active. Added a full research-format fixture check, list-shaped error handling and regression tests. Default setup now uses the model that passed the owner's connection test. 64 Python checks pass. Full real-company synthesis with this change is still pending; the saved-data hosted demo is unaffected.


## Owner-observed live synthesis result

After replacing backend/llm_router.py and restarting, the owner supplied SONACOMS screenshots showing three Business findings, one Guidance finding, two Bull findings, one Bear finding and one Governance finding, each with a source badge. All visible badges refer to the transcript dated 2026-07-30. The model-assisted audit reports no comparable commitments. This demonstrates the live model-to-interface path on the owner's laptop; it does not establish cross-quarter completeness or independent semantic correctness.

Review observations: the order-book claim says "240 billion" without a currency; confirm and retain the source currency before relying on that number. The Governance finding is explicitly management's account of its own disclosure practice, not independent evidence of sound governance. The multi-quarter audit remains demonstrated by the separately reviewed KPIT case. No full raw model response or cited PDF pages from this particular run were supplied for independent claim verification.


## 29 October 2026 — account handover and snapshot recovery

Reviewed the supplied conversation, master prompt, challenge PDFs and source archive.
The separate uploaded llm_router.py contains a newer Gemini JSON-mode fix than the archive; merged it and updated the adapter contract test.

Static startup now renders the snapshot before optional local/configured backend discovery. Static hosts do not probe nonexistent API routes. Empty hosted connection origins produce an inline explanation. Connection errors now display inside the modal instead of behind it. Snapshot recovery restores the original dataset, clears live research, closes the dialog and returns to the digest. Session storage failures no longer abort startup; older browsers receive a timeout-signal fallback. Hosted and standalone builds use the same startup code. Shell cache version advanced to v2.

Validation in this session: 60 Python tests passed; six existing frontend checks passed; added static startup, blocked-storage, empty-origin, snapshot-reset and timeout-fallback regression checks passed. Browser checked the edited compact layout: connection explanation, saved-mode recovery, bottom navigation, and KPIT audit. This is desktop compact-layout verification, not a physical-phone test.

The old public page loaded and its compact Research navigation worked in this browser. The precise cause of the reported phone failure is not proven. The old hosting project is not accessible from this account. GitHub installation was confirmed but repository tools were not exposed in the active session; no repository push or public deployment was performed. Live Gemini success is reported in the supplied prior conversation; no fresh live inference was performed here.


## Repository reconciliation and replacement hosting
GitHub access is now verified. Main ac4067677ab0173659b8491dfe162970679b70bb contains one newer commit than the original ZIP. Preserved all remote changes, including the working model default and research-format tests. Reran 64 Python tests and both frontend suites successfully. Prepared a replacement owner-private Site under the current account because the old Site is not editable here. Public access requires a separate audience decision.
