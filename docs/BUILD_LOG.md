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
