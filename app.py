from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError
from flask_apispec.extension import FlaskApiSpec

from common.blocklist import BLOCKLIST
from common.db import db
from common.marshal import marshy
from dotenv import load_dotenv

from resources.user import (
    UserRegistration,
    User,
    AllUsers,
    UserSearch,
    UserLogin,
    UserLogout,
    TokenRefresh,
    UpdatePassword,
)

from resources.customer import Customer, AllCustomers, CustomerSearch, NewCustomer
from resources.transaction import (
    Transaction,
    TransactionList,
    TransactionSearch,
    NewTransaction,
)


app = Flask(__name__)
load_dotenv(".env", verbose=True)
app.config.from_object("default_config")
app.config.from_envvar("APPLICATON_SETTINGS")
api = Api(app)
jwt = JWTManager(app)
docs = FlaskApiSpec(app)


# do noi use. Needs fixin'
# @jwt.additional_claims_loader
# def add_claims_to_jwt(identity):
#     if identity == 1:
#         return {"role": "Admin"}
#     return {"role": "Standard"}


@jwt.expired_token_loader
def expired_token_callback(jwt_headers, jwt_payload):
    return jsonify(
        {"description": "Your token has expired.", "error": "token_expired."}
    )


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLOCKLIST


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify(
            {"description": "Signature verification failed.", "error": "invalid_token."}
        ),
        401,
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required.",
            }
        ),
        401,
    )


@jwt.needs_fresh_token_loader
def needs_fresh_token_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {
                "description": "This token is not fresh.",
                "error": "fresh_token_required.",
            }
        ),
        401,
    )


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {
                "description": "This token has been revoked.",
                "error": "fresh_token_required.",
            }
        ),
        401,
    )


@app.before_first_request
def create_db():
    db.create_all()


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


api.add_resource(UserRegistration, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UpdatePassword, "/user/change_password/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(AllUsers, "/users")
api.add_resource(UserSearch, "/users/search/<string:term>")
api.add_resource(NewCustomer, "/customer/new")
api.add_resource(Customer, "/customer/<int:account_id>")
api.add_resource(AllCustomers, "/customers")
api.add_resource(CustomerSearch, "/customers/search/<string:term>")
api.add_resource(NewTransaction, "/transaction/new")
api.add_resource(Transaction, "/transaction/<int:transaction_id>")
api.add_resource(TransactionList, "/transactions")
api.add_resource(TransactionSearch, "/transactions/search/<string:term>")

docs.register(User)
docs.register(UserRegistration)
docs.register(UserLogin)
docs.register(UserLogout)
docs.register(UserSearch)
docs.register(AllUsers)
docs.register(TokenRefresh)
docs.register(Customer)
docs.register(AllCustomers)
docs.register(NewCustomer)
docs.register(CustomerSearch)
docs.register(NewTransaction)
docs.register(Transaction)
docs.register(TransactionList)
docs.register(TransactionSearch)


def main() -> None:
    db.init_app(app)
    marshy.init_app(app)
    app.run(port=5000)


if __name__ == "__main__":
    main()
