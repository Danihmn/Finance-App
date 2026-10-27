from fastapi import FastAPI

from presentation.exception_handlers import register_exception_handlers
from presentation.routers import auth_router, users_router

app = FastAPI(title="Finance App")

register_exception_handlers(app)

app.include_router(auth_router.router)
app.include_router(users_router.router)
