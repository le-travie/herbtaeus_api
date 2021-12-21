from dotenv import dotenv_values
from urllib.parse import quote

params = dotenv_values(".env")
user_name = params.get("USER")
password = quote(params.get("PASSWORD"))
host = params.get("HOST")
port = params.get("PORT")
database = params.get("DATABASE")

URL = f"postgresql://{user_name}:{password}@{host}:{port}/{database}"
