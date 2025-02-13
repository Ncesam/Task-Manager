from fastapi import FastAPI
from app.backend.routes.User import router as user_router

app = FastAPI()


app.include_router(user_router)

