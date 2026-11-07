BEGIN;

ALTER TABLE recurrences
    DROP COLUMN user_id;
ALTER TABLE recurrences
    ADD COLUMN user_id uuid REFERENCES users (id) ON DELETE set null;

COMMIT;