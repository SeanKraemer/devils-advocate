# Devil's Advocate

Devil's Advocate is a voice-first AI debate prototype for stress-testing startup ideas. A founder describes an idea, the agent challenges assumptions, and the app produces a scorecard plus a post-debate report.

This repository is a private portfolio copy prepared from a team research prototype. The first cleanup pass removes deployment-specific cache artifacts, documents external services, and adds a mock-service mode for local backend development without shared Firebase or model credentials.

## What It Does

- Runs a live debate session over a FastAPI + Socket.IO backend.
- Uses Gemini Live for spoken adversarial feedback when configured.
- Uses lightweight judge/report flows to classify claims and generate a final report.
- Supports Firebase Auth, Firestore logging, and Firebase Storage document uploads in the full setup.
- Includes a React/Vite frontend with typed claims, document upload, scorecard, feedback, share, and PDF export flows.

## Tech Stack

- React, Vite, Firebase Web SDK
- FastAPI, python-socketio
- Gemini Live API and Gemini text models
- OpenAI structured outputs for report/judge helpers
- Firebase Auth, Firestore, and Firebase Storage
- Chroma-backed retrieval for local document context

## Repository Layout

```text
frontend/          React + Vite app
backend/           FastAPI + Socket.IO backend
tests/backend/     Backend tests
docs/              Architecture diagrams
```

## Backend Setup

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r backend/requirements.txt -r requirements-dev.txt
cp backend/.env.example backend/.env
```

For a no-credential local backend smoke test, set:

```env
MOCK_SERVICES=1
```

For full behavior, provide:

```env
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
FIREBASE_KEY_PATH=./firebase_key.json
FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
```

Then run:

```bash
cd backend
python -m uvicorn main:socket_app --host 0.0.0.0 --port 8000 --reload
```

## Frontend Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Frontend environment:

```env
VITE_BACKEND_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your_firebase_web_api_key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
VITE_FIREBASE_APP_ID=your_firebase_app_id
VITE_FIREBASE_MEASUREMENT_ID=your_measurement_id
```

## Verification

```bash
source .venv/bin/activate
make test-backend

cd frontend
npm test
npm run build
```

## External Service Notes

- Do not commit Firebase Admin SDK JSON files or `.env` files.
- Use `MOCK_SERVICES=1` for backend unit work that should not touch Firebase.
- Full live debate sessions may use paid model APIs and cloud storage.
- Deployment-specific Firebase project settings should be supplied locally in `.firebaserc`, not committed.

## Portfolio Notes

This is a team-origin project. Public polishing should keep attribution accurate, avoid publishing participant data, and use original summaries rather than copied assignment text. The next deeper pass should add a true end-to-end mock debate session for frontend demos without live model APIs.
