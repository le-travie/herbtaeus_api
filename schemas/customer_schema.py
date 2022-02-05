from flask_sqlalchemy import model
from common.marshal import marshy
from models.customer_model import CustomerModel


class CustomerSchema(marshy.SQLAlchemyAutoSchema):
    class Meta:
        model = CustomerModel
        dump_only = ("account_id",)
        exclude = ("__ts_vector__",)
        include_relationships = True
        load_instance = True
