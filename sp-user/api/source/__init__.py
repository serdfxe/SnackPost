import logging
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Header, Depends, HTTPException, status, Response
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from core.fastapi.dependencies import get_repository
from core.db.repository import DatabaseRepository
from app.models.source import Source
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

SourceRepository = Annotated[
    DatabaseRepository[Source],
    Depends(get_repository(Source)),
]

@source_router.get("/", response_model=SourceListResponseDTO)
async def get_sources_route(
    repository: SourceRepository,
    x_user_id: Annotated[int, Header()],
    skip: int = 0,
    limit: int = 100,
):
    try:
        sources = await repository.filter(
            Source.user_id == x_user_id,
            skip=skip,
            limit=limit
        )
        return {
            "data": sources,
            "count": await repository.count(Source.user_id == x_user_id),
            "skip": skip,
            "limit": limit
        }
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )

@source_router.post("/", response_model=SourceResponseDTO, status_code=201)
async def create_source_route(
    repository: SourceRepository,
    x_user_id: Annotated[int, Header()],
    data: SourceCreateDTO,
):
    try:
        if await repository.get(
            (Source.user_id == x_user_id) & 
            (Source.url == str(data.url))
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Source already exists"
            )
            
        source = await repository.create(
            user_id=x_user_id,
            url=str(data.url),
            type=data.type
        )
        return source
        
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )

@source_router.patch("/{source_id}", response_model=SourceResponseDTO)
async def update_source_route(
    repository: SourceRepository,
    x_user_id: Annotated[int, Header()],
    source_id: UUID,
    data: SourceUpdateDTO,
):
    source = await repository.get(
        (Source.id == source_id) & 
        (Source.user_id == x_user_id)
    )
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    try:
        return await repository.update(
            source.id,
            data.model_dump(exclude_unset=True)
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )

@source_router.delete("/{source_id}", status_code=204)
async def delete_source_route(
    repository: SourceRepository,
    x_user_id: Annotated[int, Header()],
    source_id: UUID,
):
    source = await repository.get(
        (Source.id == source_id) & 
        (Source.user_id == x_user_id)
    )
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    await repository.delete(Source.id == source.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@source_router.post(
    "/{source_id}/check",
    responses={
        200: {"description": "Source checked successfully."},
        404: {"description": "Source not found or access denied."},
    },
)
async def check_source_route(
    repository: SourceRepository,
    x_user_id: Annotated[int, Header()],
    source_id: int,
):
    """
    Manually trigger a check for new content from this source.
    """
    logger.info(f"Manual check triggered for source {source_id} by user {x_user_id}")

    try:
        source = await repository.get(
            (Source.id == source_id) & 
            (Source.user_id == x_user_id)
        )
        
        if not source:
            logger.warning(f"Source {source_id} not found for user {x_user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source not found or access denied."
            )
            
        # Здесь можно добавить вызов Celery задачи для немедленной проверки
        # Например: check_source.delay(source_id)
        
        return {"status": "check_initiated", "source_id": source_id}

    except SQLAlchemyError as e:
        logger.error(f"Database error while checking source: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred."
        )
        
    except Exception as e:
        logger.error(f"Unexpected error while checking source: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )