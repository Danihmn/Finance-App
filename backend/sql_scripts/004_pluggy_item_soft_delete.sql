BEGIN;
ALTER TABLE pluggy_items
    ADD COLUMN deleted_at timestamptz;
COMMIT;