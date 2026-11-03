DRAFT — do not send until repository access is enabled and the actual AI build-history link below is filled. The replacement demo is public. The repository remains private; enable reviewer access before sending.

To: assessment@enam.com
Subject: ENAM - IIT screening - 2027

Hello ENAM team,

Please find my submission for the AI Engineer Build Challenge: FINN, a mobile-first tool for filtering portfolio disclosures and reviewing company fundamentals against primary evidence.

Demo: https://finn-investment-agent.jazzyibex1024.chatgpt.site
GitHub: https://github.com/Prince-svrn/FINN
AI build conversation: https://chatgpt.com/share/6ae274da-ad54-83ec-8cae-b58a55c1906a?ogimg=plain
Continuation build history: [attach this conversation export or insert its share link]

The prototype includes a windowed disclosure digest, configurable price/volume alerts, sourced results and leadership cards, a four-quarter KPIT say–do audit, three-year cash conversion, and a thesis pinboard with export. The backend also accepts tickers outside the sample portfolio; I checked the ingestion and primary financial extraction with POLYCAB.

The public demo uses saved evidence and does not call Gemini. A Render deployment configuration is included for hosting the full Python app; hosted inference has not yet been verified. The README distinguishes the saved hosted demonstration from the live backend and documents the current coverage limits. Optional model synthesis supports a Gemini Free Tier project with no billing; I tested a live SONACOMS research run that produced cited business, guidance, bull/bear and governance findings. Its automated audit found no comparable commitments, so it reports that limitation rather than inventing a verdict. The reviewed demonstration does not pretend to be generated live by an LLM.

I chose a small JavaScript frontend and FastAPI backend, with deterministic calculations and document caching to limit cost. The deepest reviewed case is KPIT; other companies receive source discovery, supported extraction and optional model synthesis. Full automated governance coverage and executive enrichment remain outside the completed scope. Next I would expand extraction coverage and validate model synthesis across more issuers.

Regards,
Prince Kumar
IIT Kanpur
