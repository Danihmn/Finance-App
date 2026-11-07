BEGIN;

CREATE TABLE recurrences
(
    id            uuid PRIMARY KEY        DEFAULT gen_random_uuid(),
    user_id       uuid REFERENCES users (id),
    category      text,
    type          text           NOT NULL CHECK (type IN ('DEBIT', 'CREDIT')),
    amount        numeric(18, 2) NOT NULL CHECK ( amount > 0 ),
    currency_code varchar(3)     NOT NULL DEFAULT 'BRL',
    created_at    timestamptz    NOT NULL DEFAULT now(),
    updated_at    timestamptz,
    deleted_at    timestamptz
);

COMMIT;