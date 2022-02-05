from common.marshal import marshy
from models.transaction_model import TransactionModel
from models.customer_model import CustomerModel
from models.user_model import UserModel


class TransactionSchema(marshy.SQLAlchemyAutoSchema):
    class Meta:
        model = TransactionModel
        dump_only = ("transaction_id",)
        dump_only = ("date_entered",)
        exclude = ("__ts_vector__",)
        include_fk = True
        include_relationships = True
        load_instance = True
