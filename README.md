# Devil's Advocate

Devil's Advocate is a real-time AI debate app for stress-testing startup ideas. A founder states a pitch, the agent attacks weak assumptions, and the app produces a transcript, live judge updates, and a structured post-debate report.

This public portfolio version is adapted from a Spring 2026 UIUC MCS CS 568 group prototype. It keeps the product and engineering work visible while removing private course materials, teammate identifiers, participant data, old deployment IDs, and credential-dependent demo paths.

## Live Demo

Try the public mock demo: https://devils-advocate.web.app

The hosted demo runs in deterministic mock mode. It is safe to leave online because it does not call live Gemini/OpenAI services or write Firebase user data.

## What It Demonstrates

- Full-stack product engineering with a React/Vite frontend and FastAPI + Socket.IO backend.
- Real-time interaction design for debate turns, transcripts, interruption states, and post-session reporting.
- AI service integration patterns across Gemini Live/text, OpenAI structured outputs, and local deterministic mock services.
- Retrieval-augmented context using Chroma-backed startup/VC reference material and optional uploaded documents.
- Privacy-aware portfolio hardening: mock public mode, credential-free demo behavior, env-driven URLs, no committed keys, and no Firebase writes in demo mode.
- Deployment readiness with Firebase Hosting, Cloud Run, GitHub Actions CI, and Workload Identity Federation for keyless deploys.

## Product Experience

In live mode, the app supports spoken debate through Gemini Live. In public portfolio mode, it defaults to a typed mock demo so interviewers can try the product without API spend, microphone permissions, Firebase credentials, or stored user data.

Public demo behavior:

- `VITE_DEMO_MODE=1` creates a local demo user and hides Firebase auth/upload/feedback friction.
- `MOCK_SERVICES=1` returns deterministic Gemini, OpenAI, and Firebase behavior on the backend.
- Typed turns use the `text_turn` Socket.IO event so the debate remains accessible and reliable.
- Firebase logging and uploads are skipped in mock mode.

## Architecture

```text
React/Vite frontend
  |  Socket.IO events: start_session, text_turn, audio_chunk, end_session
  v
FastAPI + Socket.IO backend
  |  session lifecycle, validation, rate limiting, transcript state
  |  optional RAG over uploaded docs + bundled knowledge base
  |  Gemini Live/text debate client
  |  OpenAI structured judge/report clients
  v
Firebase Auth/Firestore/Storage in live mode
```

Repository layout:

- `frontend/`: React app for the pitch flow, transcript, judge timeline, report, share text, PDF export, and optional feedback.
- `backend/`: FastAPI + Socket.IO service for auth validation, session lifecycle, Gemini/OpenAI calls, RAG, report generation, and Firebase logging.
- `backend/knowledge_base/`: local startup and VC reference material for retrieval.
- `tests/backend/`: backend unit and integration coverage.
- `.github/workflows/`: CI and mock-demo deployment workflows.

## Environment Templates

The project is intentionally split into two configurations:

- Public portfolio demo: no model keys, no Firebase writes, safe for interviewers.
- Live credentialed mode: full voice/model/Firebase behavior for controlled demos.

### Local/Public Mock Demo

`backend/.env`:

```env
MOCK_SERVICES=1
APP_ENV=local
PUBLIC_APP_URL=http://localhost:5173
ALLOWED_ORIGINS=http://localhost:5173,http://localhost

GEMINI_API_KEY=
GEMINI_LIVE_MODEL=gemini-2.5-flash-native-audio-preview-12-2025
GEMINI_TEXT_MODEL=gemini-2.5-flash-lite

OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.4-mini

FIREBASE_KEY_PATH=./firebase_key.json
FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
RAG_BACKEND=chroma
```

`frontend/.env.local`:

```env
VITE_DEMO_MODE=1
VITE_BACKEND_URL=http://localhost:8000
VITE_PUBLIC_APP_URL=http://localhost:5173

VITE_FIREBASE_API_KEY=
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=
VITE_FIREBASE_APP_ID=
VITE_FIREBASE_MEASUREMENT_ID=
```

### Hosted Mock Demo

Use this for the public portfolio deploy.

Backend Cloud Run env:

```env
MOCK_SERVICES=1
APP_ENV=production
PUBLIC_APP_URL=https://your-firebase-site.web.app
ALLOWED_ORIGINS=https://your-firebase-site.web.app
RAG_BACKEND=chroma
```

Frontend build env:

```env
VITE_DEMO_MODE=1
VITE_BACKEND_URL=https://your-cloud-run-service-xxxxx-uc.a.run.app
VITE_PUBLIC_APP_URL=https://your-firebase-site.web.app
```

GitHub Actions variables:

```text
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=us-central1
CLOUD_RUN_SERVICE=devils-advocate-api
FIREBASE_PROJECT_ID=your-firebase-project-id
VITE_BACKEND_URL=https://your-cloud-run-service-xxxxx-uc.a.run.app
VITE_PUBLIC_APP_URL=https://your-firebase-site.web.app
```

GitHub Actions secrets:

```text
GCP_WORKLOAD_IDENTITY_PROVIDER=projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID
GCP_DEPLOY_SERVICE_ACCOUNT=github-deploy@your-gcp-project-id.iam.gserviceaccount.com
```

### Live Credentialed Mode

Use live mode only for controlled demos where quotas, monitoring, deletion policies, and abuse controls are configured.

Backend additions:

```env
MOCK_SERVICES=0
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key
FIREBASE_KEY_PATH=./firebase_key.json
FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
```

Frontend additions:

```env
VITE_DEMO_MODE=0
VITE_FIREBASE_API_KEY=your-firebase-web-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
VITE_FIREBASE_MEASUREMENT_ID=your-measurement-id
```

Do not commit `.env`, `.env.local`, Firebase Admin SDK JSON, downloaded user materials, transcripts, generated reports, `.venv`, `node_modules`, `.firebase`, or build output.

## Local Development

Backend:

```bash
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -r backend/requirements.txt -r requirements-dev.txt
cp backend/.env.example backend/.env
cd backend
python -m uvicorn main:socket_app --host 0.0.0.0 --port 8000 --reload
```

Frontend:

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open `http://localhost:5173`.

## Testing

Use Python 3.11 for backend tests. The current Chroma/Pydantic stack is not compatible with Python 3.14.

```bash
uv run --python 3.11 --with-requirements backend/requirements.txt --with-requirements requirements-dev.txt pytest -q

cd frontend
npm run lint
npm test
npm run build
```

Root shortcuts:

```bash
make test-backend
make test-frontend
make test
make clean
```

CI runs the same backend and frontend checks in `.github/workflows/ci.yml`.

## Deployment

The recommended portfolio deployment is:

- Firebase Hosting for the static Vite frontend.
- Cloud Run for the FastAPI/Socket.IO backend.
- Public mock mode enabled by default.
- GitHub Actions deploy with Google Workload Identity Federation, not service-account JSON secrets.

Included workflows:

- `.github/workflows/ci.yml`: backend tests plus frontend lint/test/build.
- `.github/workflows/deploy.yml`: deploys the mock backend to Cloud Run and the demo frontend to Firebase Hosting.

Manual deployment order:

1. Create or choose a Firebase/GCP project.
2. Create a Firebase Hosting site and fill `.firebaserc` from `.firebaserc.example`.
3. Create a Cloud Run deploy service account with permissions for Cloud Run, Artifact Registry/Cloud Build source deploys, and Firebase Hosting deployment.
4. Configure GitHub Workload Identity Federation and add the two GitHub secrets.
5. Add the GitHub variables listed in `Environment Templates`.
6. Run CI on `main`.
7. Run the `Deploy Demo` workflow.
8. Smoke test the hosted app with no Gemini, OpenAI, or Firebase runtime keys.

## Manual Portfolio QA

Before treating the project as portfolio-ready, manually verify:

- Local mock demo loads at `http://localhost:5173` with no Firebase keys.
- Starting a typed demo creates a transcript, agent responses, judge updates, and a final report.
- Refreshing or ending a mock session does not create Firebase records or require uploads.
- Share text and PDF export use `VITE_PUBLIC_APP_URL`, not localhost or an old deployment URL.
- Backend `/health` returns `mock_services: true` in public demo deploys.
- CORS allows only the intended frontend origin in hosted mode.
- Firebase Hosting URL loads the app directly and after route refreshes.
- Cloud Run WebSocket connection stays open long enough for a complete debate.
- Browser console has no uncaught errors during start, turn submission, report generation, share, or PDF export.
- Mobile viewport remains usable for the pitch input, transcript, typed turn composer, and report.
- README, env examples, and source scans contain no teammate names, private course materials, participant data, secrets, or old deployment IDs.

## Portfolio Framing

This project is strongest as a playable public mock demo plus a clear code walkthrough. The public demo shows the interaction design and architecture without live model cost or privacy risk. Live voice mode is still valuable for controlled demos, but it should stay behind explicit credentials, monitoring, and quota controls.

Good interview discussion topics:

- Why the public version defaults to deterministic mock services.
- How Socket.IO session state coordinates transcripts, typed turns, audio turns, judge updates, and report generation.
- How structured-output model clients make report and judge data predictable for the UI.
- How env-driven URLs, CORS, and GitHub Actions make the project portable across deployments.
- What tradeoffs remain before a production launch: persistence model, abuse controls, observability, model latency, and stronger end-to-end browser coverage.
