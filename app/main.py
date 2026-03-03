from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

# from . import models
from .database import engine
from .routers import post, user, auth, vote


# This line creates the tables in the database if they do not exist. It is commented out because we are using Alembic for database migrations. If you want to create the tables without using Alembic, uncomment the line below.
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="RAS API",
              version="1.0.0",
              description="My backend service",
              docs_url="/docs",        # Swagger UI (default)
              redoc_url="/redoc",      # ReDoc (default)
              openapi_url="/openapi.json",)  # default is "/openapi.json"

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"Message": "Welcome to my api!"}
