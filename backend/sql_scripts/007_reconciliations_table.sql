BEGIN;

CREATE TABLE reconciliations
(
    id                 uuid PRIMARY KEY        DEFAULT gen_random_uuid(),
    financial_entry_id uuid           NOT NULL REFERENCES financial_entries (id) ON DELETE RESTRICT,
    transaction_id     uuid           NOT NULL REFERENCES transactions (id) ON DELETE RESTRICT,
    source             text           NOT NULL DEFAULT 'MANUAL' CHECK (source IN ('MANUAL', 'AUTO')),
    notes              text,
    created_at         timestamptz    NOT NULL DEFAULT now(),
    updated_at         timestamptz,
    deleted_at         timestamptz
);

CREATE UNIQUE INDEX uq_reconciliations_entry_transaction
    ON reconciliations (financial_entry_id, transaction_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_reconciliations_transaction_id
    ON reconciliations (transaction_id) WHERE deleted_at IS NULL;

COMMIT;