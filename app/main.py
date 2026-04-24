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


origins = [
    "http://localhost",
    "http://77.91.94.81",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth, prefix="/auth", tags=[" Auth"], responses=default_errors)
app.include_router(chat, prefix="/chat", tags=["Chat"], responses=default_errors)
