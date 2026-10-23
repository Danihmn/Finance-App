-- 001_init.sql
-- Initial schema. Source of truth for the database (see CLAUDE.md, section 3).
-- Do not edit after it has been applied anywhere with data you care about:
-- new changes go in a new numbered script.
--
-- Pluggy hierarchy: users (Pluggy credentials) -> pluggy_items (one per bank
-- connected through Meu Pluggy) -> bank_accounts -> transactions.
-- Pluggy ids are separate unique columns; our own uuid is always the PK.

-- ---------------------------------------------------------------- users
CREATE TABLE users
(
    id                          uuid PRIMARY KEY     DEFAULT gen_random_uuid(),
    first_name                  text        NOT NULL,
    email                       text        NOT NULL UNIQUE,
    pluggy_client_id            uuid        NOT NULL,
    pluggy_client_secret_crypto text        NOT NULL, -- encrypted by the app, never plain text
    created_at                  timestamptz NOT NULL DEFAULT now()
);

-- -------------------------------------------------------- pluggy_items
CREATE TABLE pluggy_items
(
    id                 uuid PRIMARY KEY     DEFAULT gen_random_uuid(),
    user_id            uuid        NOT NULL REFERENCES users (id) ON DELETE RESTRICT,
    pluggy_item_id     uuid        NOT NULL UNIQUE,
    connector_name     text        NOT NULL, -- likely always 'MeuPluggy'; confirm against GET /items/{id}
    consent_expires_at timestamptz,          -- null until first read of the item
    last_synced_at     timestamptz,          -- null until first successful sync
    created_at         timestamptz NOT NULL DEFAULT now(),
    updated_at         timestamptz
);

CREATE INDEX idx_pluggy_items_user_id ON pluggy_items (user_id);

-- ------------------------------------------------------------ addresses
-- Pluggy marks every address field as optional.
CREATE TABLE addresses
(
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    full_address    text,
    primary_address text,
    district        text,
    city            text,
    state           text,
    postal_code     text,
    country         text,
    type            text,
    additional_info text
);

-- --------------------------------------------------------- bank_accounts
CREATE TABLE bank_accounts
(
    id                uuid PRIMARY KEY     DEFAULT gen_random_uuid(),
    pluggy_item_id    uuid        NOT NULL REFERENCES pluggy_items (id) ON DELETE RESTRICT,
    pluggy_account_id uuid        NOT NULL UNIQUE,
    type              text        NOT NULL CHECK (type IN ('BANK', 'CREDIT')),
    subtype           text        NOT NULL CHECK (subtype IN ('CHECKING_ACCOUNT', 'SAVINGS_ACCOUNT', 'CREDIT_CARD')),
    name              text        NOT NULL,
    marketing_name    text,
    number            text        NOT NULL,
    currency_code     varchar(3)  NOT NULL,
    tax_number        text,
    owner             text,
    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz
);

CREATE INDEX idx_bank_accounts_pluggy_item_id ON bank_accounts (pluggy_item_id);

-- ----------------------------------------------------------- credit_datas
-- One row per CREDIT account. Pluggy may return any of these as null.
CREATE TABLE credit_datas
(
    id                       uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    bank_account_id          uuid NOT NULL UNIQUE REFERENCES bank_accounts (id) ON DELETE CASCADE,
    level                    text,
    brand                    text,
    balance_close_date       timestamptz,
    balance_due_date         timestamptz,
    available_credit_limit   numeric(18, 2),
    balance_foreign_currency numeric(18, 2),
    minimum_payment          numeric(18, 2),
    credit_limit             numeric(18, 2),
    status                   text CHECK (status IN ('ACTIVE', 'BLOCKED', 'CANCELLED')),
    holder_type              text CHECK (holder_type IN ('MAIN', 'ADDITIONAL'))
);

-- ------------------------------------------------------------ bank_datas
-- One row per BANK account. Pluggy may return any of these as null.
CREATE TABLE bank_datas
(
    id                             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    bank_account_id                uuid NOT NULL UNIQUE REFERENCES bank_accounts (id) ON DELETE CASCADE,
    closing_balance                numeric(18, 2),
    transfer_number                text,
    automatically_invested_balance numeric(18, 2),
    overdraft_contracted_limit     numeric(18, 2),
    overdraft_used_limit           numeric(18, 2),
    unarranged_overdraft_amount    numeric(18, 2)
);

-- -------------------------------------------------------- identity_datas
-- Sensitive (CPF, birth date). Plain text for now; revisit for LGPD.
-- Pluggy returns all of these as nullable.
CREATE TABLE identity_datas
(
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    bank_account_id uuid        NOT NULL UNIQUE REFERENCES bank_accounts (id) ON DELETE CASCADE,
    address_id      uuid UNIQUE REFERENCES addresses (id) ON DELETE SET NULL,
    document        text,
    document_type   text,
    full_name       text,
    job_title       text,
    birth_date      timestamptz
);

-- ---------------------------------------------------------- transactions
-- amount is signed, as returned by Pluggy (debits are negative).
CREATE TABLE transactions
(
    id                    uuid PRIMARY KEY        DEFAULT gen_random_uuid(),
    bank_account_id       uuid           NOT NULL REFERENCES bank_accounts (id) ON DELETE RESTRICT,
    pluggy_transaction_id uuid           NOT NULL UNIQUE, -- backs INSERT ... ON CONFLICT DO NOTHING
    date                  timestamptz    NOT NULL,
    description           text,
    currency_code         varchar(3)     NOT NULL,
    amount                numeric(18, 2) NOT NULL,
    balance               numeric(18, 2),
    category              text,
    provider_code         text,
    status                text           NOT NULL CHECK (status IN ('POSTED', 'PENDING')),
    type                  text           NOT NULL CHECK (type IN ('DEBIT', 'CREDIT')),
    sheet_posted_at       timestamptz,                    -- null = not yet posted to the spreadsheet
    created_at            timestamptz    NOT NULL DEFAULT now(),
    updated_at            timestamptz
);

CREATE INDEX idx_transactions_account_date ON transactions (bank_account_id, date DESC);
CREATE INDEX idx_transactions_pending_sheet ON transactions (id) WHERE sheet_posted_at IS NULL;

-- ------------------------------------------------------------ sync_logs
-- One row per scheduled sync run, per Pluggy item. Inserted as 'running' at the
-- start and updated at the end: a row stuck in 'running' means the job died.
CREATE TABLE sync_logs
(
    id                    uuid PRIMARY KEY     DEFAULT gen_random_uuid(),
    pluggy_item_id        uuid        NOT NULL REFERENCES pluggy_items (id) ON DELETE RESTRICT,
    started_at            timestamptz NOT NULL DEFAULT now(),
    finished_at           timestamptz,
    status                text        NOT NULL DEFAULT 'running'
        CHECK (status IN ('running', 'success', 'partial', 'failed')),
    transactions_fetched  integer     NOT NULL DEFAULT 0,
    transactions_inserted integer     NOT NULL DEFAULT 0,
    transactions_skipped  integer     NOT NULL DEFAULT 0,
    failed_step           text CHECK (failed_step IN ('fetch', 'persist', 'sheet')),
    error_code            text,
    error_message         text,
    details               jsonb
);

CREATE INDEX idx_sync_logs_item_started ON sync_logs (pluggy_item_id, started_at DESC);
