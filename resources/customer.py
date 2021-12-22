from flask import request
from flask_restful import Resource
from models.customer_model import CustomerModel
from schemas.customer_schema import CustomerSchema
from typing import Dict, Tuple

from flask_apispec import marshal_with
from flask_apispec import MethodResource
from flask_apispec.annotations import doc, use_kwargs

INSERT_ERROR = "An error occured while adding the customer."
CUSTOMER_NOT_FOUND = "Could not find customer(s)."
CUSTOMER_DELETED = "Customer account deleted."
SERVER_ERROR = "Operation could not be completed."

customer_schema = CustomerSchema()
customer_list_schema = CustomerSchema(many=True)


class NewCustomer(Resource, MethodResource):
    @doc(tags=["Customer"])
    @use_kwargs(customer_schema, location=("json"), apply=False)
    @marshal_with(customer_schema, code=201, apply=False)
    def post(self) -> Tuple[Dict, int]:
        customer_json = request.get_json()
        customer: CustomerModel = customer_schema.load(customer_json)

        try:
            customer.save_to_db()
        except:
            return {"message": SERVER_ERROR}, 500

        return customer_schema.dump(customer), 201


class Customer(Resource, MethodResource):
    @doc(tags=["Customer"])
    @marshal_with(customer_schema, apply=False)
    def get(cls, account_id: int) -> Tuple[Dict, int]:
        try:
            customer = CustomerModel.find_by_id(account_id)
        except:
            return {"message": SERVER_ERROR}, 500

        if customer is not None:
            return customer_schema.dump(customer)

        return {"message": CUSTOMER_NOT_FOUND}, 404

    @doc(tags=["Customer"])
    @use_kwargs(customer_schema, location=("json"), apply=False)
    @marshal_with(customer_schema, apply=False)
    def put(cls, account_id: int) -> Tuple[Dict, int]:
        customer_json = request.get_json()
        customer_data = customer_schema.load(customer_json)

        try:
            customer = CustomerModel.find_by_id(account_id)
        except:
            return {"message": SERVER_ERROR}, 500

        if customer:
            try:
                customer.fname = customer_data.fname
                customer.lname = customer_data.lname
                customer.address = customer_data.address
                customer.email = customer_data.email
                customer.tel_num = customer_data.tel_num
                customer.mobile_num = customer_data.mobile_num
                customer.service_type = customer_data.service_type
                customer.comments = customer_data.comments

                customer.save_to_db()
                return customer_schema.dump(customer), 200
            except:
                return {"message": SERVER_ERROR}, 500

        return {"message": CUSTOMER_NOT_FOUND}, 404

    @doc(tags=["Customer"])
    @marshal_with(customer_schema, apply=False)
    def delete(cls, account_id: int):
        customer = CustomerModel.find_by_id(account_id)
        if customer:
            try:
                customer.delete_from_db()
                return {"message": CUSTOMER_DELETED}, 200
            except:
                return {"message": SERVER_ERROR}, 500

        else:
            return {"message": CUSTOMER_NOT_FOUND}, 404


class AllCustomers(Resource, MethodResource):
    @doc(tags=["Customer"])
    @marshal_with(customer_list_schema, code=200, apply=False)
    def get(self) -> Tuple[Dict, int]:
        try:
            customers = CustomerModel.find_all()
        except:
            return {"message": SERVER_ERROR}, 500

        return {"customers": customer_list_schema.dump(customers)}, 200


class CustomerSearch(Resource, MethodResource):
    @doc(tags=["Customer"])
    @marshal_with(customer_list_schema, code=200, apply=False)
    def get(self, term: str) -> Tuple[Dict, int]:
        try:
            results = CustomerModel.text_search(term)
        except:
            return {"message": SERVER_ERROR}, 500

        if results:
            return {"customers": customer_list_schema.dump(results)}, 200

        return {"message": CUSTOMER_NOT_FOUND}, 404
