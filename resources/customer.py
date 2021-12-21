from flask import request
from flask_restful import Resource
from models.customer_model import CustomerModel
from schemas.customer_schema import CustomerSchema
from typing import Dict, List, Tuple

INSERT_ERROR = "An error occured while adding the customer."
CUSTOMER_NOT_FOUND = "Could not find customer(s)."
CUSTOMER_DELETED = "Customer account deleted."
CUSTOMER_CREATED = "Customer account created successfully."
SERVER_ERROR = "Operation could not be completed."

customer_schema = CustomerSchema()
customer_list_schema = CustomerSchema(many=True)


class Customer(Resource):
    @classmethod
    def get(cls, account_id: int) -> Tuple[Dict, int]:
        try:
            customer = CustomerModel.find_by_id(account_id)
        except:
            return {"message": SERVER_ERROR}, 500

        if customer is not None:
            return customer_schema.dump(customer)

        return {"message": CUSTOMER_NOT_FOUND}, 404
