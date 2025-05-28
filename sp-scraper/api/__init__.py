from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

import logging

from redis import asyncio as aioredis

from api.scraper import scraper_router
from api.source import source_router
from api.digest import digest_router

from core.config import REDIS_URL
from core.logging import setup_logging


def init_cors(api: FastAPI) -> None:
    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def init_routers(api: FastAPI) -> None:
    api.include_router(scraper_router)
    api.include_router(source_router)
    api.include_router(digest_router)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url(REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


def create_api() -> FastAPI:
    api = FastAPI(
        title="Scraper Service",
        description="Hide API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    init_routers(api=api)
    init_cors(api=api)

    return api


api = create_api()
setup_logging()


@api.get("/")
def read_root():
    return {"message": "Hello, World!"}


@api.get("/health")
def health_check():
    return {"status": "ok"}


@api.middleware("http")
async def log_requests(request: Request, call_next):
    logger = logging.getLogger("api")
    logger.info(f"Request: {request.method} {request.url}")

    try:
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise
