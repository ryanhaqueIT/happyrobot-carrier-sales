# Inbound Carrier Sales — HappyRobot FDE Technical Challenge

A working proof-of-concept for **Acme Logistics**: an AI voice agent on the [HappyRobot](https://happyrobot.ai) platform that automates inbound carrier sales. Carriers call in looking for loads, the AI verifies them with the FMCSA, matches them to available freight, negotiates the rate, and books the load — all without a human on the line.

---

## Live Links

| Resource | URL |
|---|---|
| **Dashboard** | https://happyrobot-carrier-sales-production-95a3.up.railway.app/dashboard |
| **API base** | https://happyrobot-carrier-sales-production-95a3.up.railway.app |
| **API docs (Swagger)** | https://happyrobot-carrier-sales-production-95a3.up.railway.app/docs |
| **HappyRobot workflow** | https://platform.happyrobot.ai/fderyanhaque/workflows/t2b82xfysmjd |
| **Code repo** | https://github.com/ryanhaqueIT/happyrobot-carrier-sales |
| **Walkthrough video** | https://youtu.be/kpDW6EkYlXc |

**API Key for dashboard / endpoints:** `acme-carrier-sales-2026`

---

## Screenshots

### Dashboard — Overview

<img width="2842" height="1530" alt="image" src="https://github.com/user-attachments/assets/a95550f6-6b42-4d9a-afea-4526a87439d3" />


### Dashboard — Loads

<img width="2840" height="1429" alt="image" src="https://github.com/user-attachments/assets/a9020f6a-2507-49d1-89a6-516e39e5ef46" />


### Dashboard — Call detail drawer
  <img width="2861" height="1528" alt="image" src="https://github.com/user-attachments/assets/9c6e7c1f-cfac-4774-9818-fe50b45a2769" />


### HappyRobot Workflow
<img width="2866" height="1484" alt="image" src="https://github.com/user-attachments/assets/dfe544b6-d6ed-4ce4-90b0-d553ab6fea7b" />

<img width="2871" height="1536" alt="image" src="https://github.com/user-attachments/assets/0125ed40-7dc3-44a1-a451-ed1eb876670f" />

---

## Architecture

```
                        Carrier dials in
                              │
                              ▼
                    ┌───────────────────┐
                    │  HappyRobot       │
                    │  Voice Agent      │
                    │  (web call)       │
                    └─┬───────────────┬─┘
                      │               │
            tool: verify_carrier  tool: find_available_loads
                      │               │
                      ▼               ▼
            ┌─────────────────────────────────┐
            │   FastAPI backend (Railway)     │
            │                                 │
            │   GET  /verify-mc?mc_number=…   │──▶ FMCSA QCMobile API
            │   GET  /loads?origin=…&…        │──▶ SQLite (15 seed loads)
            │   POST /call-record             │──▶ SQLite (calls table)
            │   GET  /metrics                 │──▶ aggregate for dashboard
            │   GET  /dashboard               │──▶ HTML + Chart.js
            └─────────────────────────────────┘
                      ▲                ▲
                      │                │
                After call:    User views:
                AI Classify    https://…/dashboard
                AI Extract
                POST /call-record
```

The system has two halves connected by HTTPS:

1. **HappyRobot platform** — handles voice (STT, LLM, TTS), workflow orchestration, post-call AI Classify and AI Extract.
2. **Our FastAPI backend** — provides loads database, FMCSA-backed eligibility verification, and stores every call's outcome for the dashboard.

---

## What the agent does on every call

1. **Greets** the caller as "Acme Logistics"
2. **Asks for the MC number**
3. **Calls `/verify-mc`** which hits the federal FMCSA API and runs eligibility logic:
   - `allowedToOperate == "Y"` (active authority)
   - `safetyRating != "Unsatisfactory"`
   - If insurance is required by FMCSA, it must be on file
   - Returns `verified: true/false` with a `rejection_reason` if applicable
4. **If verified false** → politely rejects the carrier using the rejection reason and ends the call
5. **If verified** → confirms the carrier company name with the caller
6. **Calls `/loads`** to find matching freight (filterable by origin, destination, equipment_type)
7. **Pitches** a load with all 13 fields from the spec (origin, destination, pickup/delivery datetimes, equipment, weight, commodity, miles, dimensions, etc.)
8. **Negotiates** up to 3 rounds — each round a higher counter (4% → 7% → 10% above loadboard rate as ceiling). Never decreases between rounds.
9. **If rate agreed** → mocks transfer with "Transfer was successful and now you can wrap up the conversation"
10. **After the call ends:**
    - **AI Classify** tags the outcome: `booked`, `declined`, `not_qualified`, `no_match`, `transferred`, `dropped`
    - **AI Extract** pulls structured data: mc_number, carrier_name, equipment_type, load_id, offered_rate, agreed_rate, sentiment, negotiation_rounds
    - **Webhook** posts everything to our `/call-record` endpoint → stored in SQLite → visible on dashboard

---

## API endpoints

All endpoints (except `/health` and `/dashboard`) require the `X-API-Key` header.

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/loads` | List/search loads (filters: `origin`, `destination`, `equipment_type`, `min_rate`, `max_rate`) |
| GET | `/loads/{load_id}` | Get a single load |
| GET | `/verify-mc?mc_number=…` | Verify carrier eligibility via FMCSA |
| POST | `/log-negotiation` | Log a single negotiation round |
| POST | `/webhook/happyrobot` | Receive `session.status_changed` events from HappyRobot |
| POST | `/call-record` | Store post-call data (called by HappyRobot's post-call webhook) |
| GET | `/metrics` | Aggregated metrics for the dashboard (auth required) |
| GET | `/dashboard` | Renders the HTML dashboard (no auth — fetches `/metrics` with the public key) |
| GET | `/docs` | FastAPI auto-generated Swagger UI |

### Example calls

**List loads from Dallas:**
```bash
curl -H "X-API-Key: acme-carrier-sales-2026" \
  "https://happyrobot-carrier-sales-production-95a3.up.railway.app/loads?origin=Dallas&equipment_type=Dry+Van"
```

**Verify a carrier (try MC 728261 vs 728262 to see pass/fail):**
```bash
curl -H "X-API-Key: acme-carrier-sales-2026" \
  "https://happyrobot-carrier-sales-production-95a3.up.railway.app/verify-mc?mc_number=728261"
```

**Fetch dashboard metrics:**
```bash
curl -H "X-API-Key: acme-carrier-sales-2026" \
  "https://happyrobot-carrier-sales-production-95a3.up.railway.app/metrics"
```

---

## Tech stack

- **Backend:** Python 3.12 / FastAPI / SQLite / httpx
- **Dashboard:** Single HTML file with Tailwind CSS + Chart.js (CDN), no build step
- **Hosting:** [Railway](https://railway.com) (auto-deploy on `git push` to `master`)
- **Container:** Docker (multi-arch, persists data via Railway volume mount at `/data`)
- **External API:** [FMCSA QCMobile](https://mobile.fmcsa.dot.gov/) (free federal carrier database)
- **Voice platform:** HappyRobot (workflow + AI Classify/Extract + voice agent)

---

## Run it locally

### Prerequisites
- Python 3.10+
- An [FMCSA WebKey](https://mobile.fmcsa.dot.gov/) (free, takes 2 minutes via Login.gov)

### Setup
```bash
# Clone
git clone https://github.com/ryanhaqueIT/happyrobot-carrier-sales.git
cd happyrobot-carrier-sales

# Install dependencies
pip install -r requirements.txt

# Copy env template and fill in your FMCSA key
cp .env.example .env
# Edit .env and set FMCSA_WEB_KEY=<your-webkey>

# Run the server
uvicorn app.main:app --reload --port 8000
```

Then visit:
- Dashboard: http://localhost:8000/dashboard
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Run tests
```bash
pytest tests/ -v
```

16 tests covering loads search, FMCSA verification, negotiation logging, webhook receiver, metrics aggregation, and auth.

---

## Run with Docker

```bash
docker build -t carrier-sales-api .
docker run -p 8000:8000 --env-file .env carrier-sales-api
```

Or with docker-compose:
```bash
docker-compose up
```

---

## Deploy your own

The fastest path is **Railway** — what this project uses.

### 1. Push to GitHub
Fork or clone this repo to your own GitHub account.

### 2. Create a Railway project
1. Sign up at https://railway.com
2. Click **New Project** → **Deploy from GitHub repo** → select the fork
3. Railway detects the Dockerfile and builds automatically

### 3. Add environment variables
In Railway → your service → **Variables**:

| Variable | Value |
|---|---|
| `API_KEY` | A secret string for protecting your API (e.g., `acme-carrier-sales-2026`) |
| `FMCSA_WEB_KEY` | Your FMCSA WebKey from https://mobile.fmcsa.dot.gov/ |
| `DATABASE_PATH` | `/data/carrier_sales.db` (if using a volume — recommended) |

### 4. Add a volume (for data persistence)
- Service → **Settings** → **Volumes** → **+ New Volume**
- Mount path: `/data`
- Size: 500 MB is plenty

Without a volume, the SQLite database resets on every redeploy.

### 5. Generate a public domain
Service → **Settings → Networking → Generate Domain** → you get an HTTPS URL like `https://your-app-production.up.railway.app`.

### 6. Wire up HappyRobot
In your HappyRobot workflow, point the tool webhooks at your public URL:
- `verify_carrier` tool → `GET https://<your-domain>/verify-mc?mc_number=@mc_number`
- `find_available_loads` tool → `GET https://<your-domain>/loads`
- Post-call webhook → `POST https://<your-domain>/call-record`

All requests must include the header `X-API-Key: <your API_KEY>`.

---

## Security

- **HTTPS** — Railway auto-provisions Let's Encrypt certificates on the generated domain. All traffic is TLS.
- **API key auth** — All sensitive endpoints (`/loads`, `/verify-mc`, `/log-negotiation`, `/metrics`) require an `X-API-Key` header. The `/call-record` and `/webhook/happyrobot` endpoints accept HappyRobot's webhook posts (since they originate from a known IP range and we verify by their CloudEvents payload structure).
- **Secrets** — All secrets (FMCSA WebKey, API key) live in environment variables, never committed to git. The `.env` file is gitignored.

---

## Project layout

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              FastAPI entry point + CORS + lifespan
│   ├── config.py            Loads env vars
│   ├── auth.py              X-API-Key dependency
│   ├── database.py          SQLite init + seed loader + connection helper
│   ├── models.py            Pydantic request/response models
│   ├── routes/
│   │   ├── loads.py         GET /loads, GET /loads/{id}
│   │   ├── carrier.py       GET /verify-mc
│   │   ├── negotiation.py   POST /log-negotiation
│   │   ├── webhook.py       POST /webhook/happyrobot, POST /call-record
│   │   └── metrics.py       GET /metrics, GET /dashboard
│   └── services/
│       ├── fmcsa.py         FMCSA QCMobile client + eligibility logic
│       └── loads.py         SQLite query helpers for load search
├── data/
│   └── seed_loads.json      15 realistic freight loads (all 13 spec fields)
├── templates/
│   └── dashboard.html       Single-file dashboard (Tailwind + Chart.js)
├── tests/
│   ├── conftest.py          TestClient fixture + ephemeral test DB
│   ├── test_loads.py
│   ├── test_carrier.py
│   ├── test_negotiation.py
│   ├── test_webhook.py
│   └── test_metrics.py
├── docs/
│   └── screenshots/         (screenshots referenced in this README)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
├── .dockerignore
└── README.md
```

---

## Test MC numbers (for demos)

| MC | Carrier | Result | Why |
|---|---|---|---|
| `728261` | KING SIZED TRUCKING & TRANSPORT LLC | ✅ verified — proceeds to load search | Authority active, no insurance flag |
| `75000` | WGH LOGISTICS LLC | ✅ verified — proceeds to load search | All checks pass |
| `728262` | DIANE BARBER | ❌ rejected — "no liability insurance on file" | Real carrier, but FMCSA flags missing insurance |
| `7861` | MACON IT TRANSPORTATION LLC | ❌ rejected — "no liability insurance on file" | Same as above |

For the booking demo: use **728261**, ask for Dallas dry van loads, counter the rate to trigger negotiation.
For the rejection demo: use **728262** — the agent rejects politely and ends the call.

---

## Acknowledgements

Built for the HappyRobot Forward Deployed Engineer technical challenge by Ryan Haque.

Powered by:
- [HappyRobot](https://happyrobot.ai) — voice AI orchestration
- [FMCSA QCMobile API](https://mobile.fmcsa.dot.gov/) — federal carrier eligibility data
- [Railway](https://railway.com) — hosting + persistence
