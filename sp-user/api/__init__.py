from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import logging

from api.user import user_router
from api.subscription import subscription_router

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
    api.include_router(user_router)
    api.include_router(subscription_router)


def create_api() -> FastAPI:
    api = FastAPI(
        title="User Service",
        description="Hide API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
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
