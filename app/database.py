from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

###################################################################################################
connect_args = {}

# Only pass sslmode when not using a direct URL that already contains it
if settings.database_sslmode:
    connect_args["sslmode"] = settings.database_sslmode

###################################################################################################
engine = create_engine(
    settings.app_database_url,
    pool_pre_ping=True,
    connect_args=connect_args,
)  # pool_pre_ping=True is used to check if the connection is alive before using it, which helps to avoid "Connection is closed" errors when the database connection is lost.

# connect_args=connect_args is used to enforce SSL connection to the database, which is important for security when connecting to a remote database like Neon.

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
