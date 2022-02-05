from dotenv import dotenv_values
from urllib.parse import quote
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

params = dotenv_values(".env")
user_name = params.get("USER")
password = quote(
    params.get("PASSWORD")
)  # Allows use of special characters in db password for URI
host = params.get("HOST")
port = params.get("PORT")
database = params.get("DATABASE")

DEBUG = True  # Set false in produciton environment
SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{user_name}:{password}@{host}:{port}/{database}"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
PROPAGATE_EXCEPTIONS = True
JWT_SECRET_KEY = params.get("JWT_SECRET_KEY")
APP_SECRET_KEY = params.get("APP_SECRET_KEY")
JWT_BLOCKLIST_ENABLED = True
JWT_BLOCKLIST_TOKEN_CHECKS = ["access", "refresh"]
APISPEC_SPEC = APISpec(
    title="Payment Tracking API",
    version="v1.2",
    plugins=[MarshmallowPlugin()],
    openapi_version="2.0.0",
)

APISPEC_SWAGGER_URL = "/swagger/"
APISPEC_SWAGGER_UI_URL = "/swagger-ui/"
