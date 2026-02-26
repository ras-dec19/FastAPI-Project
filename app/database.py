from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings


SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"},
)  # pool_pre_ping=True is used to check if the connection is alive before using it, which helps to avoid "Connection is closed" errors when the database connection is lost.

# connect_args={"sslmode": "require"} is used to enforce SSL connection to the database, which is important for security when connecting to a remote database like Neon.  If you're connecting to a local database that doesn't require SSL, you can remove the connect_args parameter.

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# use the code below to connect to the database using psycopg2, but make sure to comment it out when using SQLAlchemy

# while True:
#     try:
#         conn = psycopg2.connect(
#             host="localhost",
#             database="fastapi",
#             user="postgres",
#             password="Ed020401$",
#             cursor_factory=RealDictCursor,
#         )
#         cursor = conn.cursor()
#         print("Database connection was successful!")
#         break
#     except Exception as error:
#         print("Connection to database failed!")
#         print("Error: ", error)
#         time.sleep(2)
