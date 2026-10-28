# Run FINN without buying API credits

The ENAM brief, page 3, explicitly says the challenge is doable on free tiers and permits local, open-source and commercial models. Spending money is not a requirement.

## Windows setup

1. Download the latest source from [Prince-svrn/FINN](https://github.com/Prince-svrn/FINN) using **Code → Download ZIP**, and extract it into a new folder. Repository updates do not update an older laptop copy automatically. Keep the older folder if you want its cached downloads.
2. Open [Google AI Studio API keys](https://aistudio.google.com/apikey), sign in, and create a Gemini key in a project labelled **Free Tier**. Do not link billing, add a payment method, or select a paid project. If the account is ineligible for free access, stop rather than upgrade; the saved-data demo still works.
3. Double-click **setup-free-ai.cmd** in the extracted project folder. Paste the Gemini key into that terminal and press Enter. Hidden input will not display characters. Never paste the key into GitHub, chat, screenshots or the website.
4. Wait for **PASS: Gemini returned valid JSON**. This is one small uncached model call. Failure prints a safe explanation without exposing the key. Free quota availability is controlled by Google.
5. Stop the old FINN server with Ctrl+C in its server window. Double-click **start.cmd** in the new folder and open http://127.0.0.1:8000. Refresh the browser so it loads the updated interface.
6. Select SONACOMS or another company → **Run primary research → Include model synthesis**. Wait for document retrieval and the model call. The result should show cited findings beneath the research view. A connection check alone is not an end-to-end research validation: inspect the findings and primary citations too.

The helper preserves unrelated `.env` settings, replaces the old provider configuration, disables bulk classification and background polling, and makes no automatic retries or fallback calls to paid providers. It uses `gemini-3.5-flash-lite` through Google's OpenAI-compatible endpoint. It does not change billing settings. The key is stored only in the local `.env`, excluded from Git and the packaged source.

To rerun only the connection check from PowerShell in the new project folder:

```powershell
.\.venv\Scripts\python.exe scripts\setup_free_ai.py --check
```

For macOS/Linux, install the normal project requirements and run `python scripts/setup_free_ai.py` in your virtual environment. The same helper is used.

## Limits and honest status

- Only a Free Tier project makes these requests free. FINN cannot infer billing status from a key. The helper leaves dollar pricing unknown in telemetry; that is not a bill. Do not upgrade the project to keep this setup zero-cost.
- Google may limit free access by account, project, model, requests or tokens. A quota error does not require purchasing credits: wait for the indicated reset or use another genuinely free/local option after checking compatibility.
- The adapter caches valid results using the provider, model, prompt, schema and evidence. Changed evidence invalidates the cache. Truncated or invalid output is rejected. Quota and authentication failures now appear in the research screen.
- Free-tier inputs/outputs may be used by Google to improve its products. This workflow sends public company disclosures; do not add private documents to it.
- The public hosted site is a saved-data demo. The local Python backend performs live retrieval and model calls. A key entered on your laptop does not enable a model on the hosted site.
- Automated tests use mock HTTP responses. The owner has verified a successful real JSON connection using gemini-3.5-flash-lite. Full SONACOMS synthesis then failed with HTTP 400 INVALID_ARGUMENT. The router now uses JSON mode with local schema validation. Subsequent owner screenshots show populated SONACOMS Business, Guidance, Bull, Bear and Governance findings. No comparable audit commitments were extracted. Independent claim-to-source review remains incomplete.

Official references checked 28 October 2026: [pricing](https://ai.google.dev/gemini-api/docs/pricing), [billing and Free Tier](https://ai.google.dev/gemini-api/docs/billing), [API keys](https://ai.google.dev/gemini-api/docs/api-key), [OpenAI compatibility](https://ai.google.dev/gemini-api/docs/openai), [free-tier eligibility troubleshooting](https://ai.google.dev/gemini-api/docs/troubleshooting).

## Research format check

The simple connection check does not exercise the full research structure. After updating the source, run this additional check in PowerShell:

```powershell
.\.venv\Scripts\python.exe scripts\setup_free_ai.py --research-check
```

This makes one uncached call with the real Synthesis structure and a small synthetic source fixture, then verifies a returned citation. It does not change your key or settings and does not establish real-company research quality. FINN requests JSON objects with the schema in the prompt because Google's endpoint rejected the nested provider-side schema. Pydantic validation, exact source citations and deterministic arithmetic remain enforced locally. No automatic retry or paid fallback is used.
