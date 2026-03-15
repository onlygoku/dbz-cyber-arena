# 🐉 Dragon Ball Z Cyber Arena — CTF Platform

A full-featured, production-ready Capture The Flag competition platform themed around Dragon Ball Z and Chinese cyberpunk aesthetics.

---

## Feature Overview

| Feature | Details |
|---|---|
| **Theme** | Dragon Ball Z + Cyberpunk hacker aesthetic |
| **Scoring** | Static points, 6000 total across all challenges |
| **Teams** | Up to 3 members, invite-code joining |
| **Flag format** | `PREFIX{inner_value}` — prefix configurable from admin panel |
| **Attempts** | 10 per challenge; −10 pts per wrong submission after limit |
| **Rate limit** | 1 submission/second per team |
| **Dynamic flags** | Per-team HMAC-derived flags on selected challenges |
| **Scoreboard** | Real-time leaderboard with 10-second cache; freezes in final hour |
| **Live feed** | Solve events stream in real time |
| **Celebration** | Full-screen popup on correct flag |
| **Boss challenge** | Shenron Ultimate Wish (1000 pts) triggers Shenron canvas animation |
| **First Blood** | Badge for first team to solve each challenge |
| **Dragon Radar** | Team dashboard SVG radar showing category progress |
| **Auto hints** | Hints release by time-elapsed or solve-count thresholds |
| **Challenge import** | ZIP upload or directory scan auto-imports challenges |
| **Security monitor** | Detects excessive submissions, same-IP teams, fast solves |
| **Admin panel** | Full management: users, teams, challenges, submissions, security log |
| **Email verification** | SMTP-based; suppressed in dev mode (auto-verify) |

---

## Quick Start (Local Docker Compose)

### Prerequisites
- Docker ≥ 24
- Docker Compose ≥ 2.x

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/yourorg/ctf-platform.git
cd ctf-platform

# 2. Copy environment file (edit if needed)
cp .env.example .env

# 3. Start all services
docker compose up --build

# 4. Open the platform
open http://localhost:5000

# Admin login (default)
# Email:    admin@ctf.local
# Password: AdminPass123!
```

The platform **automatically**:
- Creates the PostgreSQL schema
- Creates the admin account
- Imports all challenges from the `challenges/` directory

---

## Local Development (no Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env — set DATABASE_URL to your local PostgreSQL instance

# Run
FLASK_ENV=development python run.py
```

---

## Deploying to Render.com

### Option A — Blueprint (Recommended)

1. Push your repository to GitHub.
2. In the [Render Dashboard](https://dashboard.render.com), click **New → Blueprint**.
3. Connect your GitHub repository.
4. Render reads `render.yaml` and creates:
   - A **Web Service** running Gunicorn
   - A **PostgreSQL** database
5. Set sensitive environment variables via **Render → Environment → Secret Files**:
   - `ADMIN_PASSWORD` — your secure admin password
   - `MAIL_USERNAME` / `MAIL_PASSWORD` — SMTP credentials
6. Deploy. The first boot auto-initialises the database and admin account.

### Option B — Manual

1. **Create a PostgreSQL database** on Render (Free or Starter tier).
2. **Create a Web Service**:
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60`
3. Add all environment variables from `.env.example` (mark secrets as Secret).
4. Set `DATABASE_URL` to the Internal Database URL from step 1.

### Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Flask session secret (use Render auto-generate) |
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `ADMIN_EMAIL` | ✅ | Admin account email (created on first boot) |
| `ADMIN_PASSWORD` | ✅ | Admin account password |
| `FLAG_PREFIX` | ✅ | Flag prefix, e.g. `THA` → `THA{...}` |
| `CTF_NAME` | — | Event display name |
| `DYNAMIC_FLAG_SECRET` | ✅ | HMAC secret for per-team dynamic flags |
| `MAX_TEAM_SIZE` | — | Default: 3 |
| `MAX_ATTEMPTS` | — | Default: 10 |
| `PENALTY_POINTS` | — | Default: 10 |
| `SCOREBOARD_CACHE_TTL` | — | Seconds between scoreboard refreshes (default: 10) |
| `MAIL_SUPPRESS_SEND` | — | Set `true` to skip emails (dev mode) |
| `MAIL_SERVER` | — | SMTP host |
| `MAIL_USERNAME` | — | SMTP username |
| `MAIL_PASSWORD` | — | SMTP password |

---

## Challenge Format

### Directory Structure

```
challenges/
└── my_challenge/
    ├── challenge.json   # Metadata
    ├── description.md   # Challenge description (HTML supported)
    ├── flag.txt         # Inner flag value only (no PREFIX{})
    └── files/           # Optional downloadable files
```

### challenge.json Schema

```json
{
  "title": "My Challenge",
  "category": "web",
  "difficulty": "easy",
  "points": 150,
  "is_dynamic": false,
  "is_hidden": false,
  "is_boss": false,
  "connection_info": "nc pwn.server.com 1337",
  "hints": [
    {
      "content": "Hint text here",
      "cost": 0,
      "auto_release_minutes": 30,
      "auto_release_solves": null,
      "is_visible": false
    }
  ]
}
```

### Flag Format

Store **only the inner value** in `flag.txt`:
```
my_secret_flag_value
```

The platform prepends the configured prefix automatically:
```
THA{my_secret_flag_value}
```

### Importing via Admin Panel

1. Zip the challenge directory: `zip -r my_challenge.zip my_challenge/`
2. Go to **Admin → Challenges → Import ZIP**
3. Upload the zip file

---

## Dynamic Flags

Enable `"is_dynamic": true` in `challenge.json`.

Each team receives a unique flag derived from:
```
HMAC-SHA256(DYNAMIC_FLAG_SECRET, secret:team_id:challenge_id)[:8]
```

Example result: `THA{a91f3c7e}`

The platform validates submitted flags against the team's specific value.

---

## Admin Panel

Access at `/admin` (admin account required).

| Section | Description |
|---|---|
| **Dashboard** | Stats, event controls, challenge health monitor |
| **Challenges** | Create, edit, hide/show, delete, ZIP import |
| **Users** | Search, ban/unban, verify, promote to admin |
| **Teams** | Ban, pause, reset progress |
| **Submissions** | Paginated log of all flag submissions |
| **Security** | Suspicious activity log (excessive attempts, same-IP, fast solves) |
| **Settings** | Event start/stop, scoreboard freeze, flag prefix, announcements |

---

## Scoreboard Freeze

During the **final hour** of the event:

1. Admin clicks **Freeze Scoreboard** (or it can be triggered manually).
2. The public scoreboard shows the frozen rankings.
3. Admins see the live scoreboard.
4. When the event ends, click **End Event** — the live rankings are revealed.

---

## Shenron Boss Challenge

When the **Shenron Ultimate Wish** challenge is solved:

1. Correct flag submission triggers the celebration modal.
2. A **full-screen canvas animation** renders Shenron — the Eternal Dragon — flying across the screen with particle effects.
3. The first team to solve it receives the 🩸 **First Blood** badge.

---

## Project Structure

```
ctf-platform/
├── app/
│   ├── __init__.py          # App factory, bootstrap
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── team.py
│   │   ├── challenge.py
│   │   ├── submission.py
│   │   ├── event.py
│   │   └── security.py
│   ├── routes/              # Flask blueprints
│   │   ├── auth.py          # Register, login, verify
│   │   ├── team.py          # Create, join, manage
│   │   ├── challenges.py    # List, detail, flag submit
│   │   ├── scoreboard.py    # Leaderboard + feed
│   │   ├── admin.py         # Full admin panel
│   │   └── api.py           # JSON polling endpoints
│   ├── services/            # Business logic
│   │   ├── flag_service.py  # Validation, dynamic flags
│   │   ├── score_service.py # Score calculation
│   │   ├── cache_service.py # In-process TTL cache
│   │   ├── hint_service.py  # Auto-release hints
│   │   ├── security_service.py # Anomaly detection
│   │   ├── email_service.py
│   │   └── challenge_import.py
│   ├── templates/           # Jinja2 templates
│   ├── static/              # CSS, JS, images
│   └── utils/               # Decorators, helpers
├── challenges/              # Bundled example challenges
├── docker/
│   └── postgres/init.sql
├── config.py
├── run.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── render.yaml
├── Procfile
└── .env.example
```

---

## Security Notes

- All passwords are hashed with Werkzeug's `generate_password_hash` (scrypt/pbkdf2).
- Flag comparison uses `hmac.compare_digest` to prevent timing attacks.
- Dynamic flag generation uses HMAC-SHA256 with a server-side secret.
- Admin routes require `is_admin=True` on the user record.
- Rate limiting is enforced at the submission layer (1 submission/second/team).
- Security events are logged for admin review.

---

## License

MIT — free for educational and competition use.

---

*Power up. Hack the planet. Gather the Dragon Balls.*  🐉
