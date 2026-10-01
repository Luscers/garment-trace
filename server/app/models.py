from datetime import datetime, date

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Factory(Base):
    __tablename__ = "factories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    brand: Mapped[str] = mapped_column(String(128))
    address: Mapped[str] = mapped_column(String(255))
    license_no: Mapped[str] = mapped_column(String(64), default="")
    contact: Mapped[str] = mapped_column(String(128), default="")
    phone: Mapped[str] = mapped_column(String(64), default="")
    intro: Mapped[str] = mapped_column(Text, default="")

    products: Mapped[list["Product"]] = relationship(back_populates="factory")


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("factory_id", "style_no", name="uq_factory_style"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id"))
    style_no: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(128))
    category: Mapped[str] = mapped_column(String(64), default="")
    composition: Mapped[str] = mapped_column(String(255), default="")
    standard_no: Mapped[str] = mapped_column(String(64), default="")
    color: Mapped[str] = mapped_column(String(64), default="")
    size_range: Mapped[str] = mapped_column(String(64), default="")
    care: Mapped[str] = mapped_column(String(255), default="")
    image_url: Mapped[str] = mapped_column(String(255), default="")

    factory: Mapped[Factory] = relationship(back_populates="products")
    batches: Mapped[list["Batch"]] = relationship(back_populates="product")


class Batch(Base):
    __tablename__ = "batches"
    __table_args__ = (UniqueConstraint("product_id", "batch_no", name="uq_product_batch"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    factory_id: Mapped[int] = mapped_column(Integer, default=1)
    batch_no: Mapped[str] = mapped_column(String(64))
    production_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    inspector: Mapped[str] = mapped_column(String(64), default="")
    workshop: Mapped[str] = mapped_column(String(64), default="")
    grade: Mapped[str] = mapped_column(String(32), default="合格")
    extra_json: Mapped[str] = mapped_column(Text, default="{}")

    product: Mapped[Product] = relationship(back_populates="batches")
    codes: Mapped[list["TraceCode"]] = relationship(back_populates="batch")


class TraceCode(Base):
    __tablename__ = "trace_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"))
    factory_id: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(16), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    batch: Mapped[Batch] = relationship(back_populates="codes")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="admin")
