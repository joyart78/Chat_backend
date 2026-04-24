import operator

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routes.auth import auth
from routes.chat import chat
from routes.users import users

tags_metadata = [
    {
        "name": " Auth",
        "description": "Роуты для авторизации/регистрации. В системе используется JWT авторизация.",
    },
    {
        "name": "Users",
        "description": "Роуты для взаимодействия с информацией о пользователях",
    },
]


app = FastAPI(
    openapi_tags=sorted(tags_metadata, key=operator.itemgetter("name")),
    swagger_ui_parameters={
        "docExpansion": "none",
    },
)


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
