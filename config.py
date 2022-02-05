from dotenv import dotenv_values
from urllib.parse import quote

fetcher = dotenv_values(".env")
user_name = fetcher.get("USER")
password = quote(fetcher.get("PASSWORD"))
host = fetcher.get("HOST")
port = fetcher.get("PORT")
database = fetcher.get("DATABASE")

DEBUG = False
SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{user_name}:{password}@{host}:{port}/{database}"
)
