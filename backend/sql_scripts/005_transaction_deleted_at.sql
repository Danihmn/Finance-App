BEGIN;
ALTER TABLE transactions
    ADD COLUMN deleted_at timestamptz;
COMMIT;