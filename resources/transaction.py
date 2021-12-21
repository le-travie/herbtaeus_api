from flask_jwt_extended import jwt_required, get_jwt
from flask_jwt_extended.utils import get_jwt_identity
from flask import request
from flask_restful import Resource
from typing import Dict, Tuple
from models.transaction_model import TransactionModel
from schemas.transaction_schema import TransactionSchema

INSERT_ERROR = "An error occured while adding the transactiion."
NOT_FOUND = "Could not find the transaction(s)."
DELETION = "Transaction entry successfully deleted."
SERVER_ERROR = "Operation could not be completed."

transaction_schema = TransactionSchema()
transaction_list = TransactionSchema(many=True)


class NewTransaction(Resource):
    @classmethod
    def post(cls) -> Tuple[Dict, int]:
        transaction_json = request.get_json()
        transaction: TransactionModel = transaction_schema.load(transaction_json)

        try:
            transaction.save_to_db()
        except:
            return {"message": SERVER_ERROR}, 500

        return transaction_schema.dump(transaction), 201


class Transaction(Resource):
    @classmethod
    def get(cls, transaction_id: int) -> Tuple[Dict, int]:
        try:
            transaction = TransactionModel.find_by_id(transaction_id)
        except:
            return {"message": SERVER_ERROR}, 500

        if transaction:
            return transaction_schema.dump(transaction)

        return {"message": NOT_FOUND}, 404

    @classmethod
    def put(cls, transaction_id: int) -> Tuple[Dict, int]:
        try:
            transaction = TransactionModel.find_by_id(transaction_id)
        except:
            return {"message": SERVER_ERROR}, 500

        if transaction:
            try:
                transaction.save_to_db()
                return transaction_schema.dump(transaction), 200
            except:
                return {"message": SERVER_ERROR}, 500

        return {"message": NOT_FOUND}, 404

    @classmethod
    def delete(cls, transaction_id: int):
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


class TransactionList(Resource):
    @classmethod
    @jwt_required()
    def get(cls) -> Tuple[Dict, int]:
        try:
            transactions = TransactionModel.get_all()
        except:
            return {"message": SERVER_ERROR}, 500

        return {"transactions": transaction_list.dump(transactions)}, 200


class TransactionSearch(Resource):
    @classmethod
    @jwt_required()
    def get(cls, term: str) -> Tuple[Dict, int]:
        try:
            results = TransactionModel.text_search(term)
        except:
            return {"message": SERVER_ERROR}, 500

        if results:
            return {"transactions": transaction_list.dump(results)}, 200
