from flask_jwt_extended import jwt_required, get_jwt
from flask_jwt_extended.utils import get_jwt_identity
from flask import json, request
from flask_restful import Resource
from typing import Dict, Tuple

from sqlalchemy.orm import query
from models.transaction_model import TransactionModel
from schemas.transaction_schema import TransactionSchema

from flask_apispec import marshal_with, doc, use_kwargs
from flask_apispec import MethodResource

INSERT_ERROR = "An error occured while adding the transactiion."
NOT_FOUND = "Could not find the transaction(s)."
DELETION = "Transaction entry successfully deleted."
SERVER_ERROR = "Operation could not be completed."

transaction_schema = TransactionSchema()
transaction_list = TransactionSchema(many=True)


class NewTransaction(Resource, MethodResource):
    @doc(tags=["Transaction"])
    @use_kwargs(transaction_schema, location=("json"), apply=False)
    @marshal_with(transaction_schema, code=201, apply=False)
    def post(self) -> Tuple[Dict, int]:
        transaction_json = request.get_json()

        try:
            transaction: TransactionModel = transaction_schema.load(transaction_json)
            transaction.save_to_db()
        except:
            return {"message": SERVER_ERROR}, 500

        return transaction_schema.dump(transaction), 201


class Transaction(Resource, MethodResource):
    @doc(tags=["Transaction"])
    @marshal_with(transaction_schema, apply=False)
    def get(self, transaction_id: int) -> Tuple[Dict, int]:
        try:
            transaction = TransactionModel.find_by_id(transaction_id)
        except:
            return {"message": SERVER_ERROR}, 500

        if transaction:
            return transaction_schema.dump(transaction)

        return {"message": NOT_FOUND}, 404

    @doc(tags=["Transaction"])
    @use_kwargs(transaction_schema, location=("json"), apply=False)
    @marshal_with(transaction_schema, code=200, apply=False)
    def put(self, transaction_id: int) -> Tuple[Dict, int]:
        json_data = request.get_json()
        transaction_data = transaction_schema.load(json_data)
        try:
            transaction = TransactionModel.find_by_id(transaction_id)
        except:
            return {"message": SERVER_ERROR}, 500

        if transaction:
            try:
                transaction.receipt_num = transaction_data.receipt_num
                transaction.account_id = transaction_data.account_id
                transaction.customer_name = transaction_data.customer_name
                transaction.description = transaction_data.description
                transaction.amount = transaction_data.amount
                transaction.payment_type = transaction_data.payment_type
                transaction.utility = transaction_data.utility
                transaction.service_charge = transaction_data.service_charge
                transaction.balance_due = transaction_data.balance_due
                transaction.processor = transaction_data.processor
                transaction.user_id = transaction_data.user_id

                transaction.save_to_db()
                return transaction_schema.dump(transaction), 200
            except:
                return {"message": SERVER_ERROR}, 500

        return {"message": NOT_FOUND}, 404

    @doc(tags=["Transaction"])
    @marshal_with(transaction_schema, code=200, apply=False)
    def delete(self, transaction_id: int):
        try:
            transaction = TransactionModel.find_by_id(transaction_id)
        except:
            return {"message": SERVER_ERROR}, 500

        if transaction:
            try:
                transaction.delete_from_db()
                return {"message": DELETION}, 200
            except:
                return {"message": SERVER_ERROR}, 500

        return {"message": NOT_FOUND}, 404


class TransactionList(Resource, MethodResource):
    @doc(tags=["Transaction"])
    @marshal_with(transaction_list, code=200, apply=False)
    # @jwt_required()
    def get(self) -> Tuple[Dict, int]:
        try:
            transactions = TransactionModel.get_all()
        except:
            return {"message": SERVER_ERROR}, 500

        return {"transactions": transaction_list.dump(transactions)}, 200


class TransactionSearch(Resource, MethodResource):
    @doc(tags=["Transaction"])
    @marshal_with(transaction_list, code=200, apply=False)
    # @jwt_required()
    def get(self, term: str) -> Tuple[Dict, int]:
        try:
            results = TransactionModel.text_search(term)
        except:
            return {"message": SERVER_ERROR}, 500

        if results:
            return {"transactions": transaction_list.dump(results)}, 200
