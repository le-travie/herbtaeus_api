from marshmallow import fields, Schema
from sqlalchemy.orm import load_only
from ma import ma
from models.user_model import UserModel


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_only = ("password",)
        dump_only = ("user_id",)
        exclude = ("__ts_vector__",)
        include_relationships = True
        load_instance = True


class LoginSchema(Schema):
    user_name = fields.Str(required=True)
    password = fields.Str(required=True)
    load_instance = True
