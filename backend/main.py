from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers import account_controller, auth_controller, post_controller, system_controller

print(" APP STARTING...")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system_controller.router)
app.include_router(auth_controller.router)
app.include_router(post_controller.router)
app.include_router(account_controller.router)
