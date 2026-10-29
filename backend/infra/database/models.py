import datetime
import decimal
import uuid

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="users_pkey"),
        UniqueConstraint("email", name="users_email_key"),
        UniqueConstraint(
            "pluggy_webhook_secret_hash", name="users_pluggy_webhook_secret_hash_key"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    pluggy_client_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    pluggy_client_secret_crypto: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False, server_default=text("now()")
    )
    pluggy_webhook_secret_hash: Mapped[str | None] = mapped_column(Text)

    pluggy_items: Mapped[list[PluggyItems]] = relationship(
        "PluggyItems", back_populates="user"
    )


class PluggyItems(Base):
    __tablename__ = "pluggy_items"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="RESTRICT",
            name="pluggy_items_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="pluggy_items_pkey"),
        UniqueConstraint("pluggy_item_id", name="pluggy_items_pluggy_item_id_key"),
        Index("idx_pluggy_items_user_id", "user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    pluggy_item_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False, server_default=text("now()")
    )
    consent_expires_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(True))
    last_synced_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(True))
    updated_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(True))

    user: Mapped[Users] = relationship("Users", back_populates="pluggy_items")
    bank_accounts: Mapped[list[BankAccounts]] = relationship(
        "BankAccounts", back_populates="pluggy_item"
    )
    identity_datas: Mapped[IdentityDatas] = relationship(
        "IdentityDatas", uselist=False, back_populates="pluggy_item"
    )


class BankAccounts(Base):
    __tablename__ = "bank_accounts"
    __table_args__ = (
        CheckConstraint(
            "subtype = ANY (ARRAY['CHECKING_ACCOUNT'::text, 'SAVINGS_ACCOUNT'::text, 'CREDIT_CARD'::text])",
            name="bank_accounts_subtype_check",
        ),
        CheckConstraint(
            "type = ANY (ARRAY['BANK'::text, 'CREDIT'::text])",
            name="bank_accounts_type_check",
        ),
        ForeignKeyConstraint(
            ["pluggy_item_id"],
            ["pluggy_items.id"],
            ondelete="RESTRICT",
            name="bank_accounts_pluggy_item_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="bank_accounts_pkey"),
        UniqueConstraint(
            "pluggy_account_id", name="bank_accounts_pluggy_account_id_key"
        ),
        Index("idx_bank_accounts_pluggy_item_id", "pluggy_item_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    pluggy_item_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    pluggy_account_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    subtype: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    number: Mapped[str] = mapped_column(Text, nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False, server_default=text("now()")
    )
    marketing_name: Mapped[str | None] = mapped_column(Text)
    tax_number: Mapped[str | None] = mapped_column(Text)
    owner: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(True))
    balance: Mapped[decimal.Decimal | None] = mapped_column(Numeric(18, 2))

    pluggy_item: Mapped[PluggyItems] = relationship(
        "PluggyItems", back_populates="bank_accounts"
    )
    bank_datas: Mapped[BankDatas] = relationship(
        "BankDatas", uselist=False, back_populates="bank_account"
    )
    credit_datas: Mapped[CreditDatas] = relationship(
        "CreditDatas", uselist=False, back_populates="bank_account"
    )
    transactions: Mapped[list[Transactions]] = relationship(
        "Transactions", back_populates="bank_account"
    )


class IdentityDatas(Base):
    __tablename__ = "identity_datas"
    __table_args__ = (
        ForeignKeyConstraint(
            ["pluggy_item_id"],
            ["pluggy_items.id"],
            ondelete="CASCADE",
            name="identity_datas_pluggy_item_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="identity_datas_pkey"),
        UniqueConstraint("pluggy_item_id", name="identity_datas_pluggy_item_id_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    pluggy_item_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    document: Mapped[str | None] = mapped_column(Text)
    document_type: Mapped[str | None] = mapped_column(Text)
    full_name: Mapped[str | None] = mapped_column(Text)
    job_title: Mapped[str | None] = mapped_column(Text)
    birth_date: Mapped[datetime.datetime | None] = mapped_column(DateTime(True))

    pluggy_item: Mapped[PluggyItems] = relationship(
        "PluggyItems", back_populates="identity_datas"
    )
    addresses: Mapped[list[Addresses]] = relationship(
        "Addresses", back_populates="identity_data"
    )


class Addresses(Base):
    __tablename__ = "addresses"
    __table_args__ = (
        ForeignKeyConstraint(
            ["identity_data_id"],
            ["identity_datas.id"],
            ondelete="CASCADE",
            name="addresses_identity_data_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="addresses_pkey"),
        Index("idx_addresses_identity_data_id", "identity_data_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    identity_data_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    full_address: Mapped[str | None] = mapped_column(Text)
    primary_address: Mapped[str | None] = mapped_column(Text)
    district: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(Text)
    state: Mapped[str | None] = mapped_column(Text)
    postal_code: Mapped[str | None] = mapped_column(Text)
    country: Mapped[str | None] = mapped_column(Text)
    type: Mapped[str | None] = mapped_column(Text)
    additional_info: Mapped[str | None] = mapped_column(Text)

    identity_data: Mapped[IdentityDatas] = relationship(
        "IdentityDatas", back_populates="addresses"
    )


class BankDatas(Base):
    __tablename__ = "bank_datas"
    __table_args__ = (
        ForeignKeyConstraint(
            ["bank_account_id"],
            ["bank_accounts.id"],
            ondelete="CASCADE",
            name="bank_datas_bank_account_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="bank_datas_pkey"),
        UniqueConstraint("bank_account_id", name="bank_datas_bank_account_id_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    bank_account_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    closing_balance: Mapped[decimal.Decimal | None] = mapped_column(Numeric(18, 2))
    transfer_number: Mapped[str | None] = mapped_column(Text)
    automatically_invested_balance: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(18, 2)
    )
    overdraft_contracted_limit: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(18, 2)
    )
    overdraft_used_limit: Mapped[decimal.Decimal | None] = mapped_column(Numeric(18, 2))
    unarranged_overdraft_amount: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(18, 2)
    )

    bank_account: Mapped[BankAccounts] = relationship(
        "BankAccounts", back_populates="bank_datas"
    )


class CreditDatas(Base):
    __tablename__ = "credit_datas"
    __table_args__ = (
        CheckConstraint(
            "holder_type = ANY (ARRAY['MAIN'::text, 'ADDITIONAL'::text])",
            name="credit_datas_holder_type_check",
        ),
        CheckConstraint(
            "status = ANY (ARRAY['ACTIVE'::text, 'BLOCKED'::text, 'CANCELLED'::text])",
            name="credit_datas_status_check",
        ),
        ForeignKeyConstraint(
            ["bank_account_id"],
            ["bank_accounts.id"],
            ondelete="CASCADE",
            name="credit_datas_bank_account_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="credit_datas_pkey"),
        UniqueConstraint("bank_account_id", name="credit_datas_bank_account_id_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    bank_account_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    level: Mapped[str | None] = mapped_column(Text)
    brand: Mapped[str | None] = mapped_column(Text)
    balance_close_date: Mapped[datetime.datetime | None] = mapped_column(DateTime(True))
    balance_due_date: Mapped[datetime.datetime | None] = mapped_column(DateTime(True))
    available_credit_limit: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(18, 2)
    )
    balance_foreign_currency: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(18, 2)
    )
    minimum_payment: Mapped[decimal.Decimal | None] = mapped_column(Numeric(18, 2))
    credit_limit: Mapped[decimal.Decimal | None] = mapped_column(Numeric(18, 2))
    status: Mapped[str | None] = mapped_column(Text)
    holder_type: Mapped[str | None] = mapped_column(Text)

    bank_account: Mapped[BankAccounts] = relationship(
        "BankAccounts", back_populates="credit_datas"
    )


class Transactions(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint(
            "status = ANY (ARRAY['POSTED'::text, 'PENDING'::text])",
            name="transactions_status_check",
        ),
        CheckConstraint(
            "type = ANY (ARRAY['DEBIT'::text, 'CREDIT'::text])",
            name="transactions_type_check",
        ),
        ForeignKeyConstraint(
            ["bank_account_id"],
            ["bank_accounts.id"],
            ondelete="RESTRICT",
            name="transactions_bank_account_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="transactions_pkey"),
        UniqueConstraint(
            "pluggy_transaction_id", name="transactions_pluggy_transaction_id_key"
        ),
        Index("idx_transactions_account_date", "bank_account_id", "date"),
        Index(
            "idx_transactions_provider_id",
            "bank_account_id",
            "provider_id",
            postgresql_where="(provider_id IS NOT NULL)",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    bank_account_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    pluggy_transaction_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    date: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False, server_default=text("now()")
    )
    description: Mapped[str | None] = mapped_column(Text)
    balance: Mapped[decimal.Decimal | None] = mapped_column(Numeric(18, 2))
    category: Mapped[str | None] = mapped_column(Text)
    provider_code: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(True))
    description_raw: Mapped[str | None] = mapped_column(Text)
    category_id: Mapped[str | None] = mapped_column(Text)
    operation_type: Mapped[str | None] = mapped_column(Text)
    operation_type_additional_info: Mapped[str | None] = mapped_column(Text)
    provider_id: Mapped[str | None] = mapped_column(Text)
    amount_in_account_currency: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(18, 2)
    )
    payment_data: Mapped[object | None] = mapped_column(JSONB)
    credit_card_metadata: Mapped[object | None] = mapped_column(JSONB)
    merchant: Mapped[object | None] = mapped_column(JSONB)

    bank_account: Mapped[BankAccounts] = relationship(
        "BankAccounts", back_populates="transactions"
    )
