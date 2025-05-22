import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.core.redis_initializer import init_redis
from src.database import init_models
from src.modules.grpc_token_validator.grpc_token_validator import run_grpc
from src.routes import main_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    # starts grpc service
    run_grpc()
    # init redis
    init_redis()
    # init psql models
    await init_models()
    yield


app = FastAPI(
    lifespan=lifespan,
)
app.include_router(main_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
)
