# Personal Finance App (Bank Reconciliation + AI)

## 1. Project goal

A personal finance app. It connects to our bank accounts, imports transactions, and uses AI to:

- Create the entries (lançamentos) automatically.
- Reconcile the bank transactions with the entries.
- Answer questions like "who spent how much?" (per person and per household).

Use case: private use by two people (two different CPFs). Not a public product for now.

## 2. Tech stack (decided)

| Layer | Choice |
|---|---|
| Backend | Python + FastAPI |
| AI | LangChain (LangGraph if agents are needed) |
| Database | PostgreSQL |
| Mobile app | Flutter |
| Bank data | Pluggy, free "Meu Pluggy" plan (Open Finance) |

Pluggy code lives in `backend/integrations/pluggy/` (`http_clients/`, `schemas/`, `exceptions/`, `config.py`).

## 3. Database schema

The project is **database first**. The source of truth is the versioned SQL scripts in `backend/sql_scripts/`, numbered in order (`001_init.sql`, `002_...sql`). The SQLAlchemy models are generated from the database (with `sqlacodegen`), never written by hand.

- `backend/sql_scripts/`: **source of truth.** Read the scripts, in order, before writing queries or code that touches tables, or answering questions about tables and columns. A change to the schema is a new script. Do not edit a script that was already applied.
- Generated models: do not edit them by hand, they are overwritten on each generation. Extra logic goes in separate modules.
- `backend/finance-app-schema.md` and `backend/finance-app-schema.webp`: export of the DrawSQL diagram. **Only a sketch for humans.** It can be outdated or differ from the scripts. Do not use them as the reference for the real schema.

Rules:
1. If the code, the DrawSQL export and the scripts disagree, the scripts win. Tell me about the difference, and do not silently pick one.
2. When you suggest schema changes, write them as a new SQL script in `backend/sql_scripts/`. Do not produce a DrawSQL patch unless I ask for one.
3. Money columns use `numeric`, never `float`/`double precision`. In Python, use `Decimal`.

## 4. Pluggy documentation access (MCP): use it first

This project uses the **Pluggy Docs MCP server**. It gives live access to the official Pluggy docs: guides, API reference (OpenAPI), changelog, recipes, and support Q&A. No API key is needed.

Rules for the agent:
1. Before answering any question about Pluggy, or writing any code that calls the Pluggy API, **search the MCP first**. Do not rely on memory. The API and the dashboard can change.
2. Useful tools: `search_docs`, `get_guide`, `list_guides`, `search_endpoints`, `get_api_endpoint`, `search_changelog`, `search_qa`, `search_recipes`.
3. Key guides: `guides/meu-pluggy-personal-use`, `guides/dashboard-connectors`, `connections/consents`.
4. If the MCP is not available, read the public docs at https://docs.pluggy.ai (a full index is at `/llms.txt`) and tell me that the MCP was not used.
5. If the official docs disagree with this file, **the docs win**. Tell me, and suggest an update to this file.
6. Always say which guide or endpoint the answer came from.
7. For response shapes, trust the OpenAPI spec (`get_api_endpoint`), not the JSON `example` on the docs pages. Examples are often outdated and much smaller than the real response.

## 5. Bank integration

### 5.1 Why Pluggy
- Using Open Finance directly requires being an institution authorized by the Central Bank. Not possible for a personal project.
- The banks' developer APIs (statement, Pix, billing) are for business (PJ) accounts, with contracts and certificates.
- Pluggy is an aggregator: one integration model for all banks, for personal accounts.

### 5.2 How Meu Pluggy works (confirmed in the docs)
- Each person has their own Meu Pluggy account and their own Pluggy application (Client ID + Client Secret). Authenticate **per user** (`POST /auth` returns an `apiKey`).
- Banks are connected in the Meu Pluggy site. Connecting through the **MeuPluggy** connector in the Dashboard is one authorization, and each connected bank becomes one **item** (`itemId`).
- `GET /v2/items` is not available for Meu Pluggy accounts, so we store each `itemId` ourselves. Accounts and transactions are read per item (`/accounts?itemId=`, `/transactions?accountId=`).
- Personal use only, up to 5 connections. Meu Pluggy refreshes every 24 hours, and items cannot be refreshed manually.

### 5.3 Consent expiration
- The MeuPluggy authorization lasts **1 year**. The date is `consentExpiresAt` on `GET /items/{id}`. It applies to all of that user's items.
- After it expires, accounts and transactions return **empty**, and the next refresh fails with `LOGIN_ERROR` / `USER_AUTHORIZATION_EXPIRED` (webhook `item/error`). The item may still show `UPDATED` until then, so an empty read with a past `consentExpiresAt` means "expired", not "no data".
- Renewing means doing the MeuPluggy login again in the Dashboard. A refresh by API cannot renew it.
- The app must warn before the date.

### 5.4 Data we keep
- Re-authorizing can change the `itemId`. Our tables use our own UUID primary keys, and Pluggy ids are separate unique columns. Transactions are reconciled by our own ids, not by assuming the item id is stable.
- We store transactions locally: after the consent expires, the API returns nothing, and the AI features need the history.
