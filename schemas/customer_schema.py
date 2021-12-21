from flask_sqlalchemy import model
from marshmallow_sqlalchemy import load_instance_mixin
from ma import ma
from models.customer_model import CustomerModel


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CustomerModel
        dump_only = ("account_id",)
        exclude = ("__ts_vector__",)
        include_relationships = True
        load_instance = True
