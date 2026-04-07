# 🪐 Exoplanet Explorer

A web dashboard that lets you browse, filter, and calculate survival metrics for confirmed exoplanets — with AI-powered comparisons.

> **One-liner:** Browse, filter, and calculate survival metrics for confirmed exoplanets — with AI-powered comparisons and Planet of the Day.

---

## Demo

### Exoplanet List View
The main dashboard shows a filterable catalog of exoplanets with key statistics at the top.

![Exoplanet List View](https://via.placeholder.com/800x400/0b0f19/6366f1?text=Exoplanet+List+View+—+filterable+catalog+with+stats)

### Planet Detail & Survival Calculator
Click any planet to see full details and the "Could You Survive There?" calculator.

![Survival Calculator](https://via.placeholder.com/800x400/0b0f19/06b6d4?text=Survival+Calculator+—+weight,+travel+time,+temperature+verdict)

---

## Product Context

### End Users
- Space enthusiasts, students, educators, and amateur astronomers
- Anyone curious about what it would be like to visit another world

### Problem
Exoplanet discoveries are growing rapidly (5,000+ confirmed), but the data is buried in NASA archives and scientific databases. There is no simple interface for non-scientists to explore these worlds, compare them meaningfully, or understand what visiting one would actually be like.

### Solution
Exoplanet Explorer provides a clean, accessible web interface to:
- **Browse** the catalog of confirmed exoplanets
- **Filter** by radius, mass, habitable zone, constellation, and name
- **Calculate** survival metrics — your weight on the planet, travel time, temperature verdict, and gravity verdict

---

## Architecture

```
[Browser] ──→ [React SPA] ──→ [FastAPI Backend] ──→ [PostgreSQL]
                                      │
                              (seeded from NASA
                               Exoplanet Archive)
```

| Component | Technology |
|---|---|
| **Backend** | Python + FastAPI + SQLModel |
| **Database** | PostgreSQL 18 (Alpine) |
| **Client** | React + Vite + TypeScript |
| **Reverse proxy** | Caddy |
| **Containerization** | Docker Compose |

---

## Features

### Implemented (V1 + V2)
- ✅ **Exoplanet catalog** — seeded from NASA Exoplanet Archive TAP API on first run
- ✅ **Filterable list view** — search by name, filter by radius/mass, habitable zone
- ✅ **Server-side pagination** — efficient loading of large datasets
- ✅ **Planet detail modal** — full stats for any planet with one click
- ✅ **"Could You Survive There?" calculator** — enter your weight, see:
  - Your weight on the planet
  - Surface gravity in m/s²
  - Escape velocity in km/s
  - Travel time at walking, car, plane, Voyager 1, and light speeds
  - Radio signal time to Earth
  - Temperature verdict (freeze / temperate / burn)
  - Gravity verdict (light / manageable / crushing)
- ✅ **Aggregate stats** — total count, habitable zone count, closest planet, average radius
- ✅ **AI-powered planet comparisons** — select two planets, get AI-generated natural-language comparison with side-by-side stats
- ✅ **Planet of the Day** — daily featured planet with AI-generated fun fact
- ✅ **Dark space theme UI** — responsive design with loading skeletons
- ✅ **Docker Compose** — all services orchestrated (PostgreSQL, backend, frontend, Caddy)
- ✅ **Swagger UI** — interactive API docs at `/docs`
- ✅ **Full test suite** — calculator, DB layer, API endpoints, and LLM module tests

---

## Usage

### Prerequisites
- Docker and Docker Compose v2
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/<your-username>/se-toolkit-hackathon.git
cd se-toolkit-hackathon

# Copy environment variables
cp .env.example .env.secret

# Build and start all services
docker compose up --build

# Open your browser
# Frontend: http://localhost:3000
# Backend API docs: http://localhost:8000/docs
# Caddy proxy: http://localhost:8080
```

### Running Tests

```bash
# Backend tests (calculator, DB layer, API endpoints)
cd backend
pip install -e ".[dev]"
pytest -v
```

### Environment Variables

All variables are documented in `.env.example`. The most important ones:

| Variable | Purpose | Default |
|---|---|---|
| `DB_PASSWORD` | PostgreSQL password | `exoplanet_pass` |
| `API_KEY` | Backend API key | `dev-api-key` |
| `LLM_API_KEY` | OpenAI-compatible API key for AI features | _(empty)_ |
| `LLM_API_BASE_URL` | LLM API base URL | `https://api.openai.com/v1` |
| `LLM_MODEL` | LLM model name | `gpt-4o-mini` |
| `BACKEND_PORT_EXTERNAL` | Backend port | `8000` |
| `CLIENT_PORT_EXTERNAL` | Frontend port | `3000` |
| `CADDY_HTTP_PORT` | Caddy proxy port | `8080` |

---

## Deployment

### Target OS
Ubuntu 24.04 LTS (same as university VMs)

### Prerequisites on VM
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in for group change to take effect

# Install Docker Compose v2 (usually bundled with Docker)
docker compose version
```

### Step-by-Step Deployment

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/se-toolkit-hackathon.git
cd se-toolkit-hackathon

# 2. Create secrets file
cp .env.example .env.secret
nano .env.secret  # Change DB_PASSWORD and API_KEY to strong values

# 3. Build and start all services
docker compose up -d --build

# 4. Check service health
docker compose ps
docker compose logs -f seed-data  # Watch seeding progress

# 5. Access the app
# Frontend: http://<VM_IP>:3000
# Backend API: http://<VM_IP>:8000/docs
# Caddy proxy: http://<VM_IP>:8080

# 6. (Optional) Use Caddy as the single entry point
# All services available through http://<VM_IP>:8080
```

### Stopping the App

```bash
docker compose down
# To also remove volumes (database data):
docker compose down -v
```

---

## Project Structure

```
se-toolkit-hackathon/
├── backend/
│   ├── src/exoplanet_explorer/
│   │   ├── main.py              # FastAPI app, lifespan, middleware
│   │   ├── settings.py          # Pydantic settings (+ LLM config)
│   │   ├── database.py          # Async engine + session
│   │   ├── auth.py              # API key verification
│   │   ├── calculator.py        # Survival metrics calculations
│   │   ├── llm.py               # LLM client (compare, fun fact)
│   │   ├── models/exoplanet.py  # SQLModel models + Pydantic schemas
│   │   ├── db/exoplanets.py     # DB operations
│   │   ├── routers/exoplanets.py # API endpoints (+ /compare, /planet-of-the-day)
│   │   └── data/seed.py         # NASA TAP API seed script
│   ├── tests/
│   │   ├── test_calculator.py
│   │   ├── test_db_exoplanets.py
│   │   ├── test_api_exoplanets.py
│   │   └── test_llm.py
│   ├── pyproject.toml
│   └── Dockerfile
├── client-web-react/
│   ├── src/
│   │   ├── App.tsx              # Main app component
│   │   ├── App.css              # Global styles
│   │   ├── api/client.ts        # API client
│   │   ├── components/
│   │   │   ├── ExoplanetList.tsx
│   │   │   ├── ExoplanetDetail.tsx
│   │   │   ├── SurvivalCalculator.tsx
│   │   │   ├── FilterPanel.tsx
│   │   │   ├── StatsCards.tsx
│   │   │   ├── ComparisonModal.tsx    # V2: AI comparison
│   │   │   └── PlanetOfDay.tsx        # V2: Featured planet
│   │   └── types/exoplanet.ts   # TypeScript types
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── nginx.conf
├── caddy/
│   └── Caddyfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## License

[MIT License](LICENSE)

---

## Acknowledgments

- NASA Exoplanet Archive — data source
- FastAPI, SQLModel, React, Vite, PostgreSQL — the stack
