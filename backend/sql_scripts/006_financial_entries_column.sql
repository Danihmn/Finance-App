BEGIN;

CREATE TABLE financial_entries
(
    id                  uuid PRIMARY KEY        DEFAULT gen_random_uuid(),
    user_id             uuid           NOT NULL REFERENCES users (id) ON DELETE RESTRICT,
    bank_account_id     uuid REFERENCES bank_accounts (id) ON DELETE RESTRICT,
    description         text           NOT NULL,
    category            text,
    type                text           NOT NULL CHECK (type IN ('DEBIT', 'CREDIT')),
    amount              numeric(18, 2) NOT NULL CHECK (amount > 0),
    currency_code       varchar(3)     NOT NULL DEFAULT 'BRL',
    reference_month     date           NOT NULL CHECK (reference_month = date_trunc('month', reference_month)::date),
    due_date            date,
    status              text           NOT NULL DEFAULT 'PLANNED' CHECK (status IN ('PLANNED', 'RECONCILED', 'CANCELLED')),
    installment_number  smallint CHECK (installment_number > 0),
    installment_total   smallint CHECK (installment_total >= installment_number),
    notes               text,
    created_at          timestamptz    NOT NULL DEFAULT now(),
    updated_at          timestamptz,
    deleted_at          timestamptz
);

CREATE INDEX idx_financial_entries_user_month
    ON financial_entries (user_id, reference_month) WHERE deleted_at IS NULL;
CREATE INDEX idx_financial_entries_bank_account_id
    ON financial_entries (bank_account_id) WHERE bank_account_id IS NOT NULL;

COMMIT;
