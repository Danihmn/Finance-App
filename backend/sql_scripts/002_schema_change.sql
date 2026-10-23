BEGIN;

ALTER TABLE bank_accounts
    ADD COLUMN balance numeric(18, 2);

ALTER TABLE transactions
    ADD COLUMN description_raw                text,
    ADD COLUMN category_id                    text,
    ADD COLUMN operation_type                 text,
    ADD COLUMN operation_type_additional_info text,
    ADD COLUMN provider_id                    text,
    ADD COLUMN amount_in_account_currency     numeric(18, 2),
    ADD COLUMN payment_data                   jsonb,
    ADD COLUMN credit_card_metadata           jsonb,
    ADD COLUMN merchant                       jsonb;

CREATE INDEX idx_transactions_provider_id
    ON transactions (bank_account_id, provider_id) WHERE provider_id IS NOT NULL;

ALTER TABLE identity_datas
    ADD COLUMN pluggy_item_id uuid REFERENCES pluggy_items (id) ON DELETE CASCADE;
ALTER TABLE addresses
    ADD COLUMN identity_data_id uuid REFERENCES identity_datas (id) ON DELETE CASCADE;

ALTER TABLE identity_datas
    ALTER COLUMN pluggy_item_id SET NOT NULL,
    ADD CONSTRAINT identity_datas_pluggy_item_id_key UNIQUE (pluggy_item_id),
    DROP COLUMN bank_account_id,
    DROP COLUMN address_id;

ALTER TABLE addresses
    ALTER COLUMN identity_data_id SET NOT NULL;

CREATE INDEX idx_addresses_identity_data_id ON addresses (identity_data_id);

COMMIT;