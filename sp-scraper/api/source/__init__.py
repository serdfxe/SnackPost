import logging

from typing import Annotated

from fastapi import APIRouter, Header, Depends, HTTPException, status, Response

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from uuid import UUID

from app.models.source import Source
from app.services.source import SourceService, get_source_service

from utils.content_tracker import ContentTracker

from .dto import (
    SourceResponseDTO,
    SourceCreateDTO,
    SourceUpdateDTO,
    SourceListResponseDTO,
)


source_router = APIRouter(
    prefix="/sources",
    tags=["sources"],
)
logger = logging.getLogger(__name__)


@source_router.get("/")
async def get_sources_route(
    service: Annotated[SourceService, Depends(get_source_service())],
    x_user_id: Annotated[int, Header()],
    skip: int = 0,
    limit: int = 100,
) -> SourceListResponseDTO:
    try:
        sources = await service.get_all(user_id=x_user_id, skip=skip, limit=limit)

        count = await service.repo.count(Source.user_id == x_user_id)

        return {"data": sources, "count": count, "skip": skip, "limit": limit}
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )


@source_router.post(
    "/",
    status_code=201,
    responses={
        201: {"detail": "Successfully created"},
        409: {"detail": "Source already exists"},
    },
)
async def create_source_route(
    service: Annotated[SourceService, Depends(get_source_service())],
    x_user_id: Annotated[int, Header()],
    data: SourceCreateDTO,
) -> SourceResponseDTO:
    try:
        existing = await service.repo.get(
            (Source.user_id == x_user_id) & (Source.url == str(data.url))
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Source already exists"
            )

        source = await service.create_with_user(
            user_id=x_user_id, source_data=data.model_dump()
        )
        return source

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid data"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error"
        )


@source_router.patch("/{source_id}")
async def update_source_route(
    service: Annotated[SourceService, Depends(get_source_service())],
    x_user_id: Annotated[int, Header()],
    source_id: UUID,
    data: SourceUpdateDTO,
) -> SourceResponseDTO:
    # First verify the source exists and belongs to the user
    source = await service.repo.get(
        (Source.id == source_id) & (Source.user_id == x_user_id)
    )
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source not found"
        )

    try:
        return await service.update(
            id=source_id, data=data.model_dump(exclude_unset=True)
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error"
        )


@source_router.delete("/{source_id}", status_code=204)
async def delete_source_route(
    service: Annotated[SourceService, Depends(get_source_service())],
    x_user_id: Annotated[int, Header()],
    source_id: UUID,
):
    source = await service.repo.get(
        (Source.id == source_id) & (Source.user_id == x_user_id)
    )
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source not found"
        )

    await service.delete(id=source_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@source_router.get("/articles/all")
async def get_all_articels(
    x_user_id: Annotated[int, Header()],
    service: Annotated[SourceService, Depends(get_source_service())],
):
    sources = await service.get_all(user_id=x_user_id)

    tracker = ContentTracker()

    res = []

    for i in sources:
        res.extend(await tracker.get_content(i.url, x_user_id))

    return res
