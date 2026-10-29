from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool

from infra.jobs.webhook_registration import register_webhooks
from presentation.exception_handlers import register_exception_handlers
from presentation.routers import auth_router, pluggy_items_router, users_router
from presentation.webhooks.pluggy import item_webhooks


@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_in_threadpool(register_webhooks)  # Never raises
    yield


app = FastAPI(title="Finance App", lifespan=lifespan)

register_exception_handlers(app)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(pluggy_items_router.router)
app.include_router(item_webhooks.router)
