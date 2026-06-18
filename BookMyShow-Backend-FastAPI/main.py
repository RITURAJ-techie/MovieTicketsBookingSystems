from fastapi import FastAPI
from app.routes import admin_routes, user_routes
import asyncio
from app.background_tasks.auto_unlock import auto_unlock_expired_seats
from app.config.postgres_config import engine
from app.models.postgres import Base

from contextlib import asynccontextmanager

Base.metadata.create_all(bind = engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    unlock_task = asyncio.create_task(auto_unlock_expired_seats())
    
    yield  

    # Shutdown
    unlock_task.cancel()

app = FastAPI(
    title="Book My Show",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(admin_routes.admin_router)
app.include_router(user_routes.user_router)
