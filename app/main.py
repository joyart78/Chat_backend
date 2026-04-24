from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routes.auth import auth
from routes.chat import chat

app = FastAPI()


default_errors = {
    401: {"description": "Unauthorized"},
    403: {"description": "No permission"},
    404: {"description": "Object not found"},
    409: {"description": "Collision occurred. Entity already exists"},
    410: {"description": "Already Expired"},
}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth, prefix="/auth", tags=[" Auth"], responses=default_errors)
app.include_router(chat, prefix="/chat", tags=["Chat"], responses=default_errors)
app.include_router(users, prefix="/users", tags=["Users"], responses=default_errors)
