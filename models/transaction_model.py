from __future__ import annotations
from typing import List

from db import db
from .user_model import *
from .customer_model import *
from datetime import datetime
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.types import TypeDecorator


class TsVector(TypeDecorator):
    impl = TSVECTOR
    cache_ok = True


class TransactionModel(db.Model):
    __tablename__ = "transactions"

    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    receipt_num = db.Column(db.String(50), nullable=False)
    date_entered = db.Column(
        db.Date, default=datetime.today().strftime("%Y-%m-%d"), nullable=False
    )
    account_id = db.Column(
        db.Integer, db.ForeignKey("customers.account_id"), nullable=False
    )
    customer_name = db.Column(db.String(130), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    payment_type = db.Column(db.String(15), nullable=False)
    utility = db.Column(db.String(15), nullable=False)
    service_charge = db.Column(db.Integer, nullable=False)
    balance_due = db.Column(db.Integer, nullable=False)
    processor = db.Column(db.String(65), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    __ts_vector__ = db.Column(
        TsVector(),
        db.Computed(
            "to_tsvector('english', receipt_num || ' ' || customer_name || ' ' || description || ' ' || utility || ' ' || processor )",
            persisted=True,
        ),
    )

    customers = db.relationship("CustomerModel", back_populates="transaction")
    users = db.relationship("UserModel", back_populates="transaction")

    __table_args__ = (
        db.Index("trans_vector_idx", __ts_vector__, postgresql_using="gin"),
    )

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, transaction_id: int) -> TransactionModel:
        return cls.query.filter_by(transaction_id=transaction_id).first()

    @classmethod
    def get_all(cls) -> List[TransactionModel]:
        return cls.query.order_by(db.desc(cls.date_entered)).all()

    @classmethod
    def text_search(cls, term: str) -> List[TransactionModel]:
        return (
            cls.query.filter(cls.__ts_vector__.match(f"{term}:*"))
            .order_by(db.desc(cls.date_entered))
            .all()
        )
