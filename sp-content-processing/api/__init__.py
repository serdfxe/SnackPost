from .content import content_router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    api.include_router(content_router)


def create_api() -> FastAPI:
    api = FastAPI(
        title="Content Processing Service",
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
