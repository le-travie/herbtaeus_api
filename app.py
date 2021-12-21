from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from db import db
from ma import ma
from common.blocklist import BLOCKLIST
from marshmallow import ValidationError
from common.db_connector import URL
from os import urandom

from resources.user import (
    UserRegistration,
    User,
    AllUsers,
    UserSearch,
    UserLogin,
    UserLogout,
    TokenRefresh,
)

from resources.customer import Customer, AllCustomers, CustomerSearch, NewCustomer
from resources.transaction import (
    Transaction,
    TransactionList,
    TransactionSearch,
    NewTransaction,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.secret_key = urandom(24)
api = Api(app)

jwt = JWTManager(app)


@app.before_first_request
def create_db():
    db.create_all()


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


api.add_resource(UserRegistration, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(AllUsers, "/users")
api.add_resource(UserSearch, "/users/search/<string:term>")
api.add_resource(NewCustomer, "/customer/new")
api.add_resource(Customer, "/customer/<int:account_id>")
api.add_resource(AllCustomers, "/customers")
api.add_resource(CustomerSearch, "/customers/search/<string:term>")
api.add_resource(Transaction, "/transaction/<int:transaction_id>")
api.add_resource(NewTransaction, "/transaction/new")
api.add_resource(TransactionList, "/transactions")
api.add_resource(TransactionSearch, "/transactions/search/<string:term>")

if __name__ == "__main__":
    db.init_app(app)
    ma.init_app(app)
    app.run(port=5000, debug=True)
