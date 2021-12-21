from __future__ import annotations
from typing import List
from db import db
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.types import TypeDecorator


class TsVector(TypeDecorator):
    impl = TSVECTOR
    cache_ok = True


class CustomerModel(db.Model):
    __tablename__ = "customers"

    account_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(65), nullable=False)
    lname = db.Column(db.String(65), nullable=False)
    address = db.Column(db.String(140), nullable=False)
    email = db.Column(db.String(25), nullable=False)
    tel_num = db.Column(db.String(15), nullable=False)
    mobile_num = db.Column(db.String(15), nullable=False)
    service_type = db.Column(db.String(22), nullable=False)
    comments = db.Column(db.String(255), nullable=False)
    __ts_vector__ = db.Column(
        TsVector(),
        db.Computed(
            "to_tsvector('english', fname || ' ' || lname || ' ' || address || ' ' || email || ' ' || service_type )",
            persisted=True,
        ),
    )

    transaction = db.relationship("TransactionModel")

    __table_args__ = (
        db.Index("customer_vector_idx", __ts_vector__, postgresql_using="gin"),
    )

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, account_id: int) -> CustomerModel:
        return cls.query.filter_by(account_id=account_id).first()

    @classmethod
    def find_all(cls) -> List[CustomerModel]:
        return cls.query.all()

    @classmethod
    def text_search(cls, term: str) -> List[CustomerModel]:
        return (
            cls.query.filter(cls.__ts_vector__.match(f"{term}:*"))
            .order_by(cls.account_id)
            .all()
        )
