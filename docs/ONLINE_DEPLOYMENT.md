# Live Gemini research on a phone

The ChatGPT Site is a public saved-data demo. It does not run Python. The complete FastAPI app can be hosted on Render using the repository's render.yaml Blueprint. The same hosted app serves its frontend and API; the laptop can be switched off.

1. Connect Render and grant it access to Prince-svrn/FINN. Create a Blueprint from the main branch and render.yaml. Review the Free plan; do not enable paid services unintentionally.
2. Supply FINN_LLM_API_KEY in Render's secret environment settings. Use the Gemini key that worked locally. Never put it in GitHub or the browser connection form.
3. Render generates FINN_API_TOKEN. Copy this separately as the reviewer access token. It protects the research API and its Gemini quota. Share it privately with reviewers, not in the public source or demo.
4. Wait for successful deployment and /healthz to return status ok. Open the Render-returned service URL on the phone.
5. Open Source and backend settings, leave the backend origin blank, and enter FINN_API_TOKEN. Tap Connect & verify. Choose SONACOMS, Run primary research, Include model synthesis.
6. Verify populated findings, source links and model errors. A deployment or healthy server alone is not evidence that Gemini inference worked. Try an unseeded ticker too.
7. Update the covering email with this verified live URL and reviewer token. Keep the static demo as a quick fallback.

The original public demo can also connect to the Render URL through its settings; its origin is allowed by FINN_CORS_ORIGINS. Each phone/browser needs its reviewer token once per session. Notes remain browser-local.

Free instances can sleep and have ephemeral storage. Source and model caches may reset after restarts; do not use this deployment as durable personal storage. Model availability and free quota depend on the Google project. Keep bulk T1 classification and polling disabled. No automated provider fallback is configured.

Current status: configuration prepared, but Render deployment and real hosted inference require the owner's connected account and Gemini secret. No successful hosted synthesis is claimed.
