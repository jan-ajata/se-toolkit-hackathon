# Exoplanet Explorer — Implementation Plan

## Product Definition

| Item | Description |
|---|---|
| **End-user** | Space enthusiasts, students, educators, and amateur astronomers who want to browse, compare, and learn about confirmed exoplanets in accessible language |
| **Problem** | Exoplanet discoveries are growing rapidly (5,000+ confirmed), but the data is buried in NASA archives and scientific databases. There is no simple interface for non-scientists to explore these worlds, compare them meaningfully, or understand what visiting one would actually be like |
| **One-liner** | A web dashboard that lets you browse, filter, and calculate survival metrics for confirmed exoplanets, with AI-powered comparisons in V2 |
| **Core feature** | Filterable catalog of exoplanets with key stats and a "Could You Survive There?" calculator — V2 adds LLM-powered natural-language planet comparisons |

---

## Architecture

Follows the Lab 8 pattern — three required components:

```
[Browser] ──→ [React SPA] ──→ [FastAPI Backend] ──→ [PostgreSQL]
                                      │
                              (seeded with NASA
                               Exoplanet Archive)
```

| Component | Technology | Purpose |
|---|---|---|
| **Backend** | Python + FastAPI + SQLModel | REST API — serve exoplanet data, handle filtering, run calculator |
| **Database** | PostgreSQL 18 (Alpine) | Store exoplanet catalog (seeded once at startup) |
| **Client** | React + Vite + TypeScript | Browse, search, filter, and calculate exoplanet metrics |
| **Reverse proxy** | Caddy | Route `/api/*` → backend, `/` → React SPA |
| **Containerization** | Docker Compose | All services orchestrated together |

---

## Version 1 — Core Feature (shown to TA during lab)

**Goal:** One thing done well — browse and filter exoplanets.

### Backend (`/backend`)

| # | Task | Details |
|---|---|---|
| 1.1 | Project scaffolding | `pyproject.toml`, `src/exoplanet_explorer/` package with `main.py`, `settings.py`, `database.py`, `auth.py` |
| 1.2 | Settings | `Settings` class (pydantic-settings) — app name, debug, DB credentials, CORS origins, API key — matching Lab 8 pattern |
| 1.3 | Database connection | `get_database_url()`, async `engine`, `get_session()` generator — same pattern as Lab 8 |
| 1.4 | SQLModel models | `ExoplanetRecord` — maps to `exoplanets` table with fields: `id`, `name`, `discovery_year`, `mass_jupiter`, `radius_earth`, `orbital_period_days`, `distance_light_years`, `equilibrium_temperature_k`, `habitable_zone`, `constellation`, `detection_method` |
| 1.5 | Pydantic schemas | `ExoplanetResponse` (read), `ExoplanetFilterQuery` (query params for filtering) |
| 1.6 | DB layer | `db/exoplanets.py` — `read_exoplanets(session, filters)`, `read_exoplanet(session, id)`, `read_exoplanet_count(session, filters)` |
| 1.7 | Router | `routers/exoplanets.py` — `GET /exoplanets/` (list with filtering + pagination), `GET /exoplanets/{id}` (detail), `GET /exoplanets/stats` (aggregate stats) |
| 1.8 | Main app | `main.py` — FastAPI app with lifespan, CORS middleware, error handler, include router |
| 1.9 | Seed script | `data/seed.sql` or Python seed script — inserts ~50–100 notable exoplanets from NASA Exoplanet Archive at container startup via `/docker-entrypoint-initdb.d/` |
| 1.10 | Dockerfile | Multi-stage build matching Lab 8 pattern (uv builder → slim runtime) |

### API Endpoints (V1)

| Method | Path | Description |
|---|---|---|
| `GET` | `/exoplanets/` | List exoplanets with optional query params: `min_radius`, `max_radius`, `min_mass`, `max_mass`, `habitable_zone` (bool), `constellation`, `search` (name substring), `page`, `page_size` |
| `GET` | `/exoplanets/{id}` | Get single exoplanet detail |
| `GET` | `/exoplanets/stats` | Aggregate stats: total count, count in habitable zone, average radius, detection method breakdown |
| `POST` | `/exoplanets/calculate` | **Calculator** — send a planet ID + optional user weight (kg), get back survival metrics: your weight on that planet, travel time at various speeds, temperature verdict, gravity verdict |

### Frontend (`/client-web-react`)

| # | Task | Details |
|---|---|---|
| 1.11 | Project scaffolding | Vite + React + TypeScript — `package.json`, `vite.config.ts`, `tsconfig.json`, `index.html` |
| 1.12 | API client | Simple `fetch` wrapper module for calling backend endpoints |
| 1.13 | Exoplanet list view | Table/grid showing name, discovery year, radius, mass, distance, habitable zone badge |
| 1.14 | Filter panel | Sidebar/top bar with sliders for radius/mass, checkbox for habitable zone, text search by name |
| 1.15 | Detail view | Click a planet → modal or dedicated page with full stats |
| 1.16 | Stats summary | Small cards at top: "Total discovered", "In habitable zone", "Closest to Earth" |
| 1.17 | **Calculator UI** | "Could You Survive There?" panel on the detail view — enter your weight → see results: weight on planet, travel time, temperature verdict, gravity verdict |
| 1.18 | Dockerfile | Multi-stage build (Node builder → Alpine with build output) — matching Lab 8 pattern |

### Infrastructure

| # | Task | Details |
|---|---|---|
| 1.19 | `docker-compose.yml` | Services: `backend`, `postgres`, `client-web-react`, `caddy` — adapted from Lab 8, removing LMS-specific services (otel-collector, victoria-logs/traces, nanobot, qwen-code-api, pgadmin) |
| 1.20 | `.env.docker.example` | All required env vars documented |
| 1.21 | `caddy/Caddyfile` | Route `/exoplanets*`, `/docs*`, `/openapi.json` → backend, everything else → React SPA |
| 1.22 | `.env.secret` | API key, DB password (gitignored) |

### Tests (V1)

| # | Task | Details |
|---|---|---|
| 1.23 | Unit tests | Test DB layer functions (`read_exoplanets`, `read_exoplanet`) with SQLite in-memory |
| 1.24 | API tests | Test endpoint responses (status codes, schema validation) with `httpx.AsyncClient` |
| 1.25 | **Calculator tests** | Test gravity, travel time, and temperature calculations with known values |

### V1 Acceptance Criteria (for TA demo)

- [ ] `docker compose up` starts all services
- [ ] React UI loads in browser at `http://localhost:<port>`
- [ ] Exoplanet list displays with data from the database
- [ ] Filtering by habitable zone works
- [ ] Search by name works
- [ ] Clicking a planet shows its detail view
- [ ] Stats summary shows correct aggregate numbers
- [ ] **Calculator works** — enter weight, see survival metrics for a selected planet
- [ ] Swagger UI at `/docs` is functional
- [ ] TA can try it and give feedback

---

## Version 2 — Polish + Deploy (by Thursday 23:59)

**Goal:** Improve V1 based on TA feedback + add LLM-powered features + deploy.

### New / Improved Features

| # | Task | Details |
|---|---|---|
| 2.1 | TA feedback implementation | Address whatever the TA suggested during V1 demo |
| 2.2 | **LLM settings** | Add `LLM_API_KEY`, `LLM_API_BASE_URL`, `LLM_MODEL` to `settings.py` and `.env` files |
| 2.3 | **LLM module** | `llm.py` — `compare_planets(planet_a, planet_b)` and `generate_fun_fact(planet)` using `httpx` to call OpenAI-compatible API |
| 2.4 | **LLM comparison endpoint** | `POST /exoplanets/compare` — send two planet IDs, get back AI-generated natural-language comparison paragraph |
| 2.5 | **Comparison UI** | Select two planets → "Compare" button → modal shows LLM-generated text with loading skeleton while waiting |
| 2.6 | Enhanced comparison view | Show both the LLM-generated text AND a side-by-side stat table with Earth-relative values (e.g., "2.3× Earth radius", "0.8× Earth mass") for cross-validation |
| 2.7 | "Planet of the Day" with LLM | Highlight one notable exoplanet on the homepage — LLM generates a fun, accessible fact about it each day |
| 2.8 | Pagination | Server-side pagination for the exoplanet list (if not in V1) |
| 2.9 | Loading states + error handling | Skeleton loaders for LLM responses, graceful error messages, retry logic |
| 2.10 | Responsive design | Mobile-friendly layout |
| 2.11 | Expanded dataset | Seed 200+ exoplanets instead of ~50 |
| 2.12 | Calculator polish | Add more metrics: surface gravity in m/s², escape velocity, how long a radio signal would take to reach Earth |

### Deployment

| # | Task | Details |
|---|---|---|
| 2.8 | Dockerize all services | Every service has a working `Dockerfile`, `docker-compose.yml` runs with `--build` |
| 2.9 | Deploy to VM | `docker compose up -d` on university VM, accessible via public IP/port |
| 2.10 | Caddy TLS | If domain available, Caddy handles HTTPS automatically |

### Documentation

| # | Task | Details |
|---|---|---|
| 2.11 | `README.md` | Product name, one-line description, screenshots, end users, problem, solution, features (implemented + planned), usage instructions, deployment instructions (OS, prerequisites, step-by-step) |
| 2.12 | `LICENSE` | MIT License |
| 2.13 | `.gitignore` | Python, Node, Docker, env files |
| 2.14 | `.dockerignore` | For each service Dockerfile |

### Presentation (Task 5)

| Slide | Content |
|---|---|
| 1 — Title | "Exoplanet Explorer", name, email, group |
| 2 — Context | End users, problem, one-liner |
| 3 — Implementation | How built (FastAPI + React + Postgres + **LLM for AI comparisons**), V1 vs V2 scope, TA feedback addressed |
| 4 — Demo | **Pre-recorded 2-min video with voice-over** showing V2 in action |
| 5 — Links | GitHub repo URL + QR, deployed product URL + QR |

---

## Repository Structure

```
se-toolkit-hackathon/
├── .gitignore
├── LICENSE                          # MIT
├── README.md                        # Product documentation
├── PLAN.md                          # This file
├── .env.example                     # Template for environment variables
├── .env.secret                      # Actual secrets (gitignored)
├── docker-compose.yml               # Orchestration
│
├── backend/
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── pyproject.toml               # + httpx dependency (V2) for LLM calls
│   └── src/
│       └── exoplanet_explorer/
│           ├── __init__.py
│           ├── main.py              # FastAPI app, lifespan, middleware, routers
│           ├── settings.py          # + LLM_API_KEY, LLM_API_BASE_URL, LLM_MODEL (V2)
│           ├── database.py          # Engine, session
│           ├── auth.py              # API key verification
│           ├── llm.py               # **V2** — LLM client: compare_planets(), generate_fun_fact()
│           ├── calculator.py        # **V1** — gravity, travel time, temperature calculations
│           ├── models/
│           │   ├── __init__.py
│           │   └── exoplanet.py     # SQLModel models (ExoplanetRecord, schemas)
│           ├── db/
│           │   ├── __init__.py
│           │   └── exoplanets.py    # DB operations
│           ├── routers/
│           │   ├── __init__.py
│           │   └── exoplanets.py    # + /calculate (POST) in V1, + /compare (POST) in V2
│           └── data/
│               └── seed.sql          # Initial exoplanet data
│
├── client-web-react/
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/
│       │   └── client.ts            # Fetch wrapper + calculate (V1) + compare (V2)
│       ├── components/
│       │   ├── ExoplanetList.tsx
│       │   ├── ExoplanetDetail.tsx
│       │   ├── ComparisonModal.tsx       # **V2** — LLM comparison display
│       │   ├── SurvivalCalculator.tsx    # **V1** — "Could You Survive There?"
│       │   ├── FilterPanel.tsx
│       │   ├── StatsCards.tsx
│       │   └── PlanetOfDay.tsx           # **V2** — LLM-generated fun fact
│       └── types/
│           └── exoplanet.ts
│
├── caddy/
│   └── Caddyfile
│
└── tests/
    ├── test_db_exoplanets.py        # Unit tests for DB layer
    ├── test_api_exoplanets.py       # API endpoint tests
    ├── test_llm.py                  # **V2** — LLM module tests (mocked)
    └── test_calculator.py           # **V1** — calculator tests
```

---

## Compliance Checklist (from README.md requirements)

| Requirement | How We Meet It |
|---|---|
| Simple to build | Single domain (exoplanets), one table, CRUD + filtering + calculator math (V1); LLM call added in V2 |
| Clearly useful | Makes NASA exoplanet data accessible to non-scientists with AI-powered insights |
| Easy to explain | "Browse, calculate survival metrics, and compare with AI for exoplanets" |
| **LLM usage (mandatory)** | **V2: LLM generates natural-language comparisons between any two planets + fun facts for "Planet of the Day"** |
| Backend | FastAPI with SQLModel + PostgreSQL |
| Database | PostgreSQL with seeded exoplanet catalog |
| End-user client | React SPA with Vite + TypeScript |
| Version 1 — one core feature | Browse + filter catalog + survival calculator |
| Version 2 — builds on V1 | **LLM comparison endpoint + UI**, Planet of the Day with LLM, TA feedback |
| Dockerized | All services have Dockerfiles, orchestrated via docker-compose |
| Deployed | Runs on university VM, accessible via Caddy |
| MIT License | Included |
| README.md structure | Name, description, screenshots, context, features, usage, deployment |
| GitHub repo named `se-toolkit-hackathon` | Will be created/pushed |
| No Telegram bot | Not used (blocked on university VMs anyway) |

---

## Development Order (suggested)

1. Scaffold repo structure + `.gitignore` + `LICENSE`
2. Backend V1: settings → database → models → DB layer → **calculator module** → router (incl. `/calculate`) → main app
3. Backend V1: seed script + Dockerfile
4. Frontend V1: scaffold → API client → list view → filter panel → detail view → **survival calculator** → Dockerfile
5. Infrastructure: `docker-compose.yml` → `Caddyfile` → `.env` files
6. Test V1 end-to-end → demo to TA → collect feedback
7. Backend V2: add LLM settings → **LLM module** → `/compare` endpoint + wire into router
8. Frontend V2: **comparison modal** → Planet of the Day with LLM → TA feedback → polish
9. Deploy → document → record demo → prepare slides

---

## LLM Integration — Design Details (V2 reference)

> **Note:** This section is for V2 planning. Do not implement during V1.

### How it works

The backend has a single `llm.py` module that wraps all LLM calls. It uses `httpx` to make OpenAI-compatible HTTP requests.

```
User selects 2 planets in React UI
        ↓
React sends POST /exoplanets/compare { "planet_a_id": 5, "planet_b_id": 12 }
        ↓
Backend fetches both planets from DB
        ↓
Backend builds prompt:
  "You are a science communicator. Compare these two exoplanets
   for a general audience. Mention size, temperature, distance,
   and habitability. Keep it under 150 words.

   Planet A: Kepler-442b — radius 1.34× Earth, temp 260K,
   distance 1206 ly, in habitable zone.
   Planet B: Proxima Centauri b — radius 1.03× Earth, temp 234K,
   distance 4.24 ly, in habitable zone."
        ↓
LLM API returns:
  "Kepler-442b and Proxima Centauri b are both promising
   candidates in the search for habitable worlds..."
        ↓
Backend returns { "comparison": "..." } to React
        ↓
React displays the text with a nice card layout
```

### `llm.py` — two functions

| Function | Purpose |
|---|---|
| `compare_planets(planet_a, planet_b, client)` | Takes two `ExoplanetRecord` dicts, builds prompt, calls LLM, returns comparison string |
| `generate_fun_fact(planet, client)` | Takes one `ExoplanetRecord`, builds prompt, returns a fun fact string (used for Planet of the Day in V2) |

### Prompt template (comparison)

```
You are an enthusiastic science communicator writing for a general audience.
Compare these two confirmed exoplanets in an engaging, accessible way.
Mention their size, temperature, distance from Earth, and whether they could
potentially support life. Keep it under 150 words. Be specific with numbers.

Planet A: {name} — radius {radius_earth}× Earth, mass {mass_jupiter}× Jupiter,
  temperature {equilibrium_temperature_k}K, distance {distance_light_years} ly,
  {'in the habitable zone' if habitable_zone else 'outside the habitable zone'},
  discovered {discovery_year}.

Planet B: {name} — radius {radius_earth}× Earth, mass {mass_jupiter}× Jupiter,
  temperature {equilibrium_temperature_k}K, distance {distance_light_years} ly,
  {'in the habitable zone' if habitable_zone else 'outside the habitable zone'},
  discovered {discovery_year}.
```

### Calculator — "Could You Survive There?"

Pure math, no LLM needed. Takes planet data + user's Earth weight.

| Metric | Formula |
|---|---|
| **Your weight on planet** | `weight_earth × (planet_mass / earth_mass) / (planet_radius / earth_radius)²` |
| **Surface gravity** | `G × planet_mass / planet_radius²` |
| **Travel time (walking)** | `distance_km / 5 km/h` |
| **Travel time (car)** | `distance_km / 100 km/h` |
| **Travel time (plane)** | `distance_km / 900 km/h` |
| **Travel time (Voyager 1)** | `distance_km / 61,000 km/h` |
| **Travel time (light)** | `distance_light_years` (by definition) |
| **Temperature verdict** | `< 200K → "You'd freeze instantly", 200–320K → "Temperate!", > 320K → "You'd burn up"` |
| **Gravity verdict** | `< 0.5g → "You'd feel light as a feather", 0.5–2g → "Manageable", > 2g → "Crushing weight"` |

Results displayed as colorful cards with verdict emojis.
