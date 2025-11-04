## Quick Start (Docker Compose)

```bash
cp .env.sample .env
docker compose up --build
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Adminer (DB UI): http://localhost:8080

## Design Choices
- JWT for Authentication: Secure stateless user sessions.
- SQLAlchemy ORM: Clean database access and migrations.
- Scheduler: Automated tasks for resets and reward distribution.
- Modular Structure: Separate files for models, schemas, database config, and utilities.

### Auth
- Email/password with **bcrypt** hashing (passlib).
- JWT (signed with HS256) containing `sub = user_id`. Expiry configurable via env.
- Protected endpoints require `Authorization: Bearer <token>`.

### Database
- **MySQL 8** via SQLAlchemy models:
  - `users(id, email, password_hash, coins)`
  - `scores(user_id, score, created_at, game_mode, period_type, period_start, period_end)`
  - `rewards(user_id, game_mode, period_type, period_start, period_end, place, amount)`
- **No destructive resets**: the active leaderboard is the subset of `scores` whose `(period_type, game_mode, period_start, period_end)` matches the **current** period. A new period implicitly “clears” the leaderboard because new submissions are placed under the new period keys.

### Reset & Rewards Strategy
- APScheduler cron jobs (UTC) run at boundaries and compute **previous** period winners by highest *best score per user*.
- Top 3 rewarded with 300/250/200 coins. Rewards are added to `users.coins`.

### Leaderboard Semantics
- **Best score per user** defines rank within a period.
- Ties are handled with **dense ranking** behavior on the `/top` endpoint.

### Assumptions & Trade-offs
- Since the prompt did not specify any game “modes,” I defined only the `run` and `campaign` modes.
- Each user will be ranked and awarded based on their highest score, even if their other scores are higher than those of other players.

## Notes
- Timezone is **UTC** for all period calculations.
- Adminer can connect with `db`, system `MySQL`, user `cr_card_app`, password `cr_card_app`, database `cr_card_app`.