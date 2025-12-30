from sqlalchemy import (
    Table,
    Column,
    BigInteger,
    String,
    Text,
    MetaData,
    DateTime,
    func,
)

metadata = MetaData()

links = Table(
    "links",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("short_code", String(16), unique=True, nullable=False),
    Column("long_url", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)
