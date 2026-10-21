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

## 3. Pluggy documentation access (MCP): use it first

This project uses the **Pluggy Docs MCP server** (`pluggy-docs`). It gives live access to the official Pluggy docs: guides, API reference (OpenAPI), changelog, recipes, and support Q&A. No API key is needed.

**Rules for the agent:**
1. Before answering any question about Pluggy, or writing any code that calls the Pluggy API, **search the MCP first**. Do not rely on memory. The API and the dashboard can change.
2. Useful tools: `search_docs`, `get_guide`, `list_guides`, `search_endpoints`, `get_api_endpoint`, `search_changelog`, `search_qa`, `search_recipes`.
3. Key guides: `guides/meu-pluggy-personal-use` and `guides/dashboard-connectors`.
4. If the MCP is not available, read the public docs at https://docs.pluggy.ai (a full index is at `/llms.txt`) and tell me that the MCP was not used.
5. If the official docs disagree with this file, **the docs win**. Tell me, and suggest an update to this file.
6. Always say which guide or endpoint the answer came from.

## 4. Bank integration: what we learned

### 4.1 Direct integration with the banks is not an option
- Using Open Finance directly requires being an institution authorized by the Central Bank. Not possible for a personal project.
- The banks' developer APIs (statement, Pix, billing) are for business (PJ) accounts, with contracts and certificates. Too much work for personal accounts.

### 4.2 Use an aggregator: Pluggy
- Pluggy covers through Open Finance (accounts, transactions, credit cards), for personal and business.
- One integration model for all banks. The user authorizes in the bank's own app or site (Open Finance consent).
- The consent has an expiration date. As far as I know, it is up to 12 months. The app must warn when a connection is about to expire. (Not confirmed in the docs. Check it.)