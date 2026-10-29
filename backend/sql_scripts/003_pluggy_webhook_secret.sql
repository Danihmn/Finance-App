BEGIN;

ALTER TABLE users
    ADD COLUMN pluggy_webhook_secret_hash text UNIQUE;

COMMIT;