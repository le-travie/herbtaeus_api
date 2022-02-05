from __future__ import annotations
from typing import List
from common.db import db
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.types import TypeDecorator
from .transaction_model import *


class TsVector(TypeDecorator):
    impl = TSVECTOR
    cache_ok = True


class UserModel(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(50), nullable=False, unique=True)
    fname = db.Column(db.String(65), nullable=False)
    lname = db.Column(db.String(65), nullable=False)
    password = db.Column(db.String(254), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    __ts_vector__ = db.Column(
        TsVector(),
        db.Computed(
            "to_tsvector('english', user_name || ' ' || fname || ' ' || lname || ' ' || role )",
            persisted=True,
        ),
    )

    transaction = db.relationship("TransactionModel")

    __table_args__ = (db.Index("vector_idx", __ts_vector__, postgresql_using="gin"),)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username: str) -> UserModel:
        return cls.query.filter_by(user_name=username).first()

    @classmethod
    def find_by_id(cls, user_id: int) -> UserModel:
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod
    def find_all(cls) -> List[UserModel]:
        return cls.query.order_by(cls.user_id).all()

    @classmethod
    def text_search(cls, term: str) -> List[UserModel]:
        return (
            cls.query.filter(cls.__ts_vector__.match(f"{term}:*"))
            .order_by(cls.user_id)
            .all()
        )
