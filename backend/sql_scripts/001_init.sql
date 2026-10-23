-- 001_init.sql
-- Initial schema. Source of truth for the database (see CLAUDE.md, section 3).
-- Do not edit after it has been applied anywhere with data you care about:
-- new changes go in a new numbered script.

-- ---------------------------------------------------------------- users
CREATE TABLE users
(
    id                          uuid PRIMARY KEY     DEFAULT gen_random_uuid(),
    first_name                  text        NOT NULL,
    email                       text        NOT NULL UNIQUE,
    hashed_password             text        NOT NULL,
    pluggy_client_id            uuid        NOT NULL,
    pluggy_client_secret_crypto text        NOT NULL,
    created_at                  timestamptz NOT NULL DEFAULT now()
);

-- -------------------------------------------------------- pluggy_items
CREATE TABLE pluggy_items
(
    id                 uuid PRIMARY KEY     DEFAULT gen_random_uuid(),
    user_id            uuid        NOT NULL REFERENCES users (id) ON DELETE RESTRICT,
    pluggy_item_id     uuid        NOT NULL UNIQUE,
    consent_expires_at timestamptz,
    last_synced_at     timestamptz,
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
    created_at            timestamptz    NOT NULL DEFAULT now(),
    updated_at            timestamptz
);

CREATE INDEX idx_transactions_account_date ON transactions (bank_account_id, date DESC);
