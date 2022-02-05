from typing import Dict, Tuple, Union
from flask_jwt_extended.utils import get_jwt, get_jwt_identity
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required
from werkzeug.security import safe_str_cmp
from flask_restful import Resource
from flask import request
from common.blocklist import BLOCKLIST
from models.user_model import UserModel
from schemas.user_schema import UserSchema, LoginSchema
import bcrypt

# from common.error_logger import logger

from flask_apispec.annotations import doc, use_kwargs
from flask_apispec import marshal_with
from flask_apispec import MethodResource
from webargs import fields

DUPLICATION_ERROR = "Username '{}', already exists."
USER_CREATED = "User '{}', created successfully."
USER_NOT_FOUND = "User(s) not found."
USER_DELETION = "User was successfully deleted."
INCORRECT_CREDENTIALS = "Username and/or password incorrect."
LOG_OUT = "Successfully logged out."
SERVER_ERROR = "Internal error, could not complete operation."

user_schema = UserSchema()
login_schema = LoginSchema()
user_list_schema = UserSchema(many=True)


class UserRegistration(MethodResource, Resource):
    @doc(tags=["User"])
    @use_kwargs(user_schema, location=("json"), apply=False)
    @marshal_with(user_schema, apply=False)
    def post(self) -> Tuple[Dict, int]:
        user_json = request.get_json()
        user: UserModel = user_schema.load(user_json)

        hashed = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
        user.password = hashed.decode("ascii")

        if UserModel.find_by_username(user.user_name):
            return {"message": DUPLICATION_ERROR.format(user.user_name)}, 400

        try:
            user.save_to_db()
            return {"message": USER_CREATED.format(user.user_name)}, 201
        except:
            return {"message": SERVER_ERROR}, 500


class User(Resource, MethodResource):
    @doc(tags=["User"])
    @marshal_with(user_schema, apply=False)
    def get(self, user_id: int) -> Union[Dict, Tuple[Dict, int]]:
        user = UserModel.find_by_id(user_id)

        if not user:
            return {"message": USER_NOT_FOUND}, 404

        return user_schema.dump(user)

    @doc(tags=["User"])
    @use_kwargs(user_schema, location=("json"), apply=False)
    @marshal_with(user_schema, apply=False)
    def put(self, user_id: int) -> Tuple[Dict, int]:
        user_json = request.get_json()
        user_data = user_schema.load(user_json)
        try:
            user = UserModel.find_by_id(user_id)
        except:
            return {"message": SERVER_ERROR}, 500

        if user:
            try:
                user.user_name = user_data.user_name
                user.fname = user_data.fname
                user.lname = user_data.lname
                user.role = user_data.role

                user.save_to_db()
                return user_schema.dump(user), 200
            except:
                return {"message": SERVER_ERROR}, 500

        return {"message": USER_NOT_FOUND}, 404

    @doc(tags=["User"])
    @marshal_with(user_schema, apply=False)
    def delete(self, user_id: int):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {"message": USER_NOT_FOUND}, 404

        user.delete_from_db()
        return {"message": USER_DELETION}, 200


class AllUsers(Resource, MethodResource):
    @doc(tags=["User"])
    @marshal_with(user_list_schema, code=200, apply=False)
    def get(cls) -> Tuple[Dict, int]:
        try:
            users = UserModel.find_all()
        except:
            return {"message": SERVER_ERROR}, 500

        return {"users": user_list_schema.dump(users)}, 200


class UserSearch(Resource, MethodResource):
    @doc(tags=["User"])
    @marshal_with(user_list_schema, code=200, apply=False)
    def get(self, term: str) -> Tuple[Dict, int]:
        try:
            users = UserModel.text_search(term)
        except:
            return {"message": SERVER_ERROR}, 500

        if users:
            return {"users": user_list_schema.dump(users)}, 200

        return {"message": USER_NOT_FOUND}, 404


class UserLogin(Resource, MethodResource):
    @doc(tags=["User Authentication"])
    @use_kwargs(login_schema, location=("json"), apply=False)
    @marshal_with(login_schema, apply=False)
    def post(self) -> Tuple[Dict, int]:
        user_json = request.get_json()
        password = user_json["password"]

        user = UserModel.find_by_username(user_json["user_name"])

        if user and bcrypt.checkpw(
            password.encode("utf-8"), user.password.encode("utf-8")
        ):
            access_token = create_access_token(identity=user.user_id, fresh=True)
            refresh_token = create_refresh_token(user.user_id)

            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        return {"message": INCORRECT_CREDENTIALS}, 401


class UserLogout(Resource, MethodResource):
    @doc(tags=["User Authentication"])
    @use_kwargs({"Authorization": fields.Str()}, location=("headers"), apply=False)
    @jwt_required()
    def post(self) -> Tuple[Dict, int]:
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)

        return {"message": LOG_OUT}, 200


class TokenRefresh(Resource, MethodResource):
    @doc(tags=["User Authentication"])
    @use_kwargs({"Authorization": fields.Str()}, location=("headers"), apply=False)
    @jwt_required(refresh=True)
    def post(self) -> Tuple[Dict, int]:
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200


class UpdatePassword(Resource):
    def put(self, user_id: int) -> Tuple[Dict, int]:
        user_json = request.get_json()
        user_data = user_schema.load(user_json)

        try:
            user = UserModel.find_by_id(user_id)

            if user:
                new_password = user_data.password.encode("utf-8")
                user.password = bcrypt.hashpw(new_password, bcrypt.gensalt()).decode(
                    "ascii"
                )

                user.save_to_db()
                return user_schema.dump(user), 200
            else:
                return {"message": USER_NOT_FOUND}, 404

        except Exception as err:
            # logger.error(err, exc_info=True)
            return {"message": SERVER_ERROR}, 500
