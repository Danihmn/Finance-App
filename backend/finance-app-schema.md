# Schema: Finance App Schema
Database: pgsql
Tables: 8
Columns are NOT NULL unless marked nullable.

## users
id: uuid PK
first_name: varchar
email: varchar unique
client_id: uuid
client_secret_crypto: text
created_at: timestamptz

## pluggy_applications
id: uuid PK
user_id: uuid FK
pluggy_item_id: uuid
connector_name: varchar
consent_expires_at: timestamptz
last_synced_at: timestamptz
created_at: timestamptz
updated_at: timestamptz nullable

## bank_accounts
id: uuid PK
type: text
subtype: text
item_id: uuid
pluggy_application_id: uuid FK unique
created_at: timestamptz
updated_at: timestamptz nullable
currency_code: varchar
tax_number: text
name: text
marketing_name: text
number: varchar
owner: text

## credit_datas
id: uuid PK
bank_account_id: uuid FK
level: text
brand: varchar
balance_close_date: timestamptz
balance_due_date: timestamptz
available_credit_limit: double precision
balance_foreign_currency: double precision
minimum_payment: double precision
credit_limit: double precision
status: varchar
holder_type: varchar

## bank_datas
id: uuid PK
bank_account_id: uuid FK
closing_balance: double precision
transfer_number: text
automatically_invested_balance: double precision
overdraft_contracted_limit: double precision
overdraft_used_limit: double precision
unarranged_overdraft_amount: double precision

## identity_datas
id: bigint PK
bank_account_id: uuid FK
item_id: uuid
document: text
birth_date: timestamptz
document_type: varchar
job_title: varchar
full_name: varchar
address_id: uuid FK

## addresses
id: uuid PK
full_address: text
state: varchar nullable
primary_address: text
country: varchar
type: text nullable
postal_code: varchar
city: varchar
additional_info: text nullable
district: varchar nullable

## transactions
id: uuid PK
bank_account_id: uuid FK
created_at: timestamptz
updated_at: timestamptz nullable
date: timestamptz
description: text nullable
currency_code: varchar
amount: double precision
balance: double precision nullable
category: varchar nullable
provider_code: varchar nullable
status: varchar
type: varchar

## Relationships
pluggy_applications.user_id → users.id (many-to-one)
bank_accounts.pluggy_application_id → pluggy_applications.id (many-to-one)
credit_datas.bank_account_id → bank_accounts.id (one-to-one)
bank_datas.bank_account_id → bank_accounts.id (one-to-one)
identity_datas.bank_account_id → bank_accounts.id (one-to-one)
identity_datas.address_id → addresses.id (one-to-one)
transactions.bank_account_id → bank_accounts.id (many-to-one)

---
If you suggest changes to this schema, ALSO return them as a DrawSQL patch: one fenced ```json code block, so I can apply them to my diagram. If you are only answering a question, skip the patch.

Patch rules:
- One JSON object with "strategy": "merge"; combine every change into that single patch.
- Reference tables and columns by name. Only include what changes — omit unchanged columns and unused optional fields.
- Column: {"name","type","length","is_primary_key","is_auto_increment","is_nullable","is_unique_key","is_index","is_unsigned","default","enum_values"} — use exact type names for pgsql as shown in the schema above.
- Relationship: {"type":"one-to-many","source_table":"users","source_column":"id","target_table":"posts","target_column":"user_id"} — for "one-to-many" the source is the "one" side; for "many-to-one" the source is the "many" (foreign-key) side. Prefer "one-to-many".
- Add "default_type" ("string" | "function" | "number" | "boolean") when a default could be misread — a literal string "CURRENT_TIMESTAMP" or "0" needs "default_type":"string".
- SET columns (MySQL) list their members in "set_values", not "enum_values".
- Index: {"indexes":[{"name":"idx_posts_user_created","type":"index","columns":["user_id","created_at"]}]} on its table — "type" is "index" or "unique"; delete via "deletions".
- Group: {"name":"Billing"}. A group never lists its members — put "parent_name":"Billing" on each table that belongs to it.
- Sticky note: {"sticky_notes":[{"content":"..."}]}.
- Delete via "deletions"; rename via "old_name". Do not include left/top coordinates.

Examples:
Add table: `{"strategy":"merge","tables":[{"name":"posts","comment":"Blog posts","columns":[{"name":"id","type":"bigint","is_primary_key":true,"is_auto_increment":true},{"name":"user_id","type":"bigint","is_index":true},{"name":"title","type":"varchar","length":255},{"name":"body","type":"text","is_nullable":true},{"name":"created_at","type":"timestamp","is_nullable":true},{"name":"updated_at","type":"timestamp","is_nullable":true}]}]}`
Rename table and column (use old_name only when renaming): `{"strategy":"merge","tables":[{"name":"articles","old_name":"posts","columns":[{"name":"content","old_name":"body"}]}]}`
Delete: `{"strategy":"merge","deletions":{"tables":["tmp"],"columns":[{"table":"users","columns":["legacy"]}],"relationships":[{"source_table":"users","source_column":"id","target_table":"posts","target_column":"user_id"}]}}`
Multiple groups with nested tables (every table sets parent_name): `{"strategy":"merge","groups":[{"name":"Auth"},{"name":"Content"}],"tables":[{"name":"users","parent_name":"Auth","columns":[{"name":"id","type":"bigint","is_primary_key":true,"is_auto_increment":true}]},{"name":"roles","parent_name":"Auth","columns":[{"name":"id","type":"bigint","is_primary_key":true,"is_auto_increment":true}]},{"name":"posts","parent_name":"Content","columns":[{"name":"id","type":"bigint","is_primary_key":true,"is_auto_increment":true}]}]}`
