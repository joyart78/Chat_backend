from fastapi import FastAPI

from routes.auth import auth

app = FastAPI()


default_errors = {
    401: {"description": "Unauthorized"},
    403: {"description": "No permission"},
    404: {"description": "Object not found"},
    409: {"description": "Collision occurred. Entity already exists"},
    410: {"description": "Already Expired"},
}


app.include_router(auth, prefix="/auth", tags=[" Auth"], responses=default_errors)
