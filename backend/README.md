# Finance App — Backend

FastAPI backend of the personal finance app (bank reconciliation + AI). The project goal, stack and rules are in the root [`CLAUDE.md`](../CLAUDE.md).

## Prerequisites

- Python 3.14 (see `.python-version`)
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL (13+, because of `gen_random_uuid()`)
- [ngrok](https://ngrok.com/) with an account and a static domain (needed to receive Pluggy's webhooks)

## Installation

```bash
cd backend
uv sync
```

## PostgreSQL

The project is **database first**: the source of truth is the scripts in `sql_scripts/`, numbered and applied in order.

Create the database:

```bash
createdb finance_app
```

Apply the scripts, in order:

```bash
for f in sql_scripts/*.sql; do psql -d finance_app -v ON_ERROR_STOP=1 -f "$f"; done
```

Rules:

- A schema change = a **new script** (`004_...sql`). Never edit a script that was already applied.
- The SQLAlchemy models (`infra/database/models.py`) are **generated** with `sqlacodegen`, never written by hand.

## Configuration (`.env`)

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `DATABASE_URL` | Postgres connection, e.g. `postgresql+psycopg2://user:pass@localhost:5432/finance_app` |
| `JWT_SECRET_KEY` | JWT secret. Generate a new one, do not use the example's |
| `JWT_ALGORITHM` | E.g. `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime |
| `ENCRYPTION_KEY` | Fernet key that encrypts the Pluggy client secret |
| `PUBLIC_BASE_URL` | Public HTTPS URL Pluggy reaches the backend at (the ngrok one) |

Generate the `ENCRYPTION_KEY`:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

If `PUBLIC_BASE_URL` is not set, the automatic webhook registration is skipped (a warning is logged).

## Running the API

From `backend/`:

```bash
uv run fastapi dev presentation/app.py
```

The API starts at `http://127.0.0.1:8000` and the interactive docs are at `http://127.0.0.1:8000/docs`.

## Pluggy webhooks with ngrok

Pluggy tells us when an item is created, updated or deleted by calling a webhook. Since the API runs on your machine, ngrok exposes it publicly.

1. In the `.env`, set ngrok's static domain:

   ```
   PUBLIC_BASE_URL=https://gatherer-darkened-swifter.ngrok-free.dev
   ```

2. Start the API (previous section). It must be running before the tunnel.

3. In another terminal, open the tunnel:

   ```bash
   ngrok http http://127.0.0.1:8000 --url https://gatherer-darkened-swifter.ngrok-free.dev
   ```

How it works:

- At startup (and when a user is created), the backend registers (or fixes) three webhooks of every user in Pluggy, pointing to `PUBLIC_BASE_URL` + the route of each event (`infra/jobs/webhook_registration.py`):

  | Event | Route | What the backend does |
  |---|---|---|
  | `item/created` | `/webhooks/pluggy/items/created` | Saves the item in `pluggy_items` for the user that owns the webhook, then syncs. |
  | `item/updated` | `/webhooks/pluggy/items/updated` | Syncs the user. An unknown item is saved first (covers a lost `item/created`). |
  | `item/deleted` | `/webhooks/pluggy/items/deleted` | Sets `pluggy_items.deleted_at`. Accounts and transactions stay, but the item leaves the sync. |

- Pluggy sends the `X-Webhook-Token` header with a per-user secret, shared by the three webhooks. Only its hash is stored in the database.
- To add a bank you do not touch the database: connect it in Pluggy (Dashboard, application's Demo page, Connect Account, MeuPluggy). Each bank connected in Meu Pluggy is authorized separately, so a bank added later also needs this step.
- The ngrok domain is static, so the URL does not change between runs. If you change the domain, update `PUBLIC_BASE_URL` and restart the API to register the webhook again.
- The tunnel must be open when Pluggy updates the data. With it closed, ngrok answers `404 ERR_NGROK_3200` and Pluggy gives up after a few attempts.
- ngrok's inspector, with the received requests, is at `http://127.0.0.1:4040`.

## Testing flow

1. Postgres running, with the scripts applied.
2. `.env` configured.
3. API up.
4. ngrok up.
5. Create a user and log in (`/docs`).
6. Connect a bank in Pluggy. The `item/created` webhook registers the item (`POST /pluggy-items` is only needed for items created while the API was down).
7. Wait for the `item/updated` webhook. Meu Pluggy refreshes every 24 hours and does not allow a manual refresh.

## Structure

| Folder | Content |
|---|---|
| `domain/` | Entities |
| `infra/` | Database (session, generated models), repositories, jobs |
| `integrations/pluggy/` | Pluggy's HTTP clients, schemas and config |
| `presentation/` | FastAPI app, routers, schemas, webhooks |
| `services/` | Business rules |
| `sql_scripts/` | Schema (source of truth) |
