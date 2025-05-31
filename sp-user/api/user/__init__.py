import logging
from typing import Annotated
from fastapi import APIRouter, Header, Depends, HTTPException, status, Response
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from core.fastapi.dependencies import get_repository
from core.db.repository import DatabaseRepository

from app.models.user import User

from .dto import (
    UserResponseDTO,
    UserCreateDTO,
)


user_router = APIRouter(
    prefix="/user",
    tags=["user"],
)
logger = logging.getLogger(__name__)


UserRepository = Annotated[
    DatabaseRepository[User],
    Depends(get_repository(User)),
]


@user_router.get(
    "/",
    response_model=UserResponseDTO,
    responses={
        200: {"description": "User data retrieved successfully."},
        404: {"description": "User not found."},
    },
)
async def get_user_route(
    repository: UserRepository,
    x_user_id: Annotated[int, Header()],
):
    """
    Get user data. The operation returns the data of the user that is associated with the provided X-User-Id.
    """
    logger.info(f"Attempting to fetch user with ID: {x_user_id}")

    try:
        user = await repository.get(User.user_id == x_user_id)

        if not user:
            logger.warning(f"User not found with ID: {x_user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )

        logger.info(f"Successfully retrieved user with ID: {x_user_id}")
        return user

    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching user {x_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred.",
        )

    except Exception as e:
        logger.error(
            f"Unexpected error while fetching user {x_user_id}: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )


@user_router.post(
    "/",
    response_model=UserResponseDTO,
    responses={
        201: {"description": "User created successfully."},
        409: {"description": "Conflict. User already exists."},
    },
)
async def post_user_route(
    repository: UserRepository,
    data: UserCreateDTO,
):
    """
    Create user. The operation creates new user with provided data.
    """
    logger.info("Attempting to create new user")
    logger.debug(f"User creation data: {data.model_dump()}")

    try:
        user = await repository.create(**data.model_dump())
        logger.info(f"Successfully created user with ID: {user.user_id}")
        return user

    except IntegrityError as e:
        logger.warning(f"User creation conflict: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists."
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error during user creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred.",
        )

    except Exception as e:
        logger.error(f"Unexpected error during user creation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )


@user_router.delete(
    "/",
    responses={
        204: {"description": "User deleted successfully."},
        404: {"description": "User not found."},
    },
)
async def delete_user_route(
    repository: UserRepository,
    x_user_id: Annotated[int, Header()],
):
    """
    Delete user. The operation removes the user that is associated with the provided X-User-Id.
    """
    logger.info(f"Attempting to delete user with ID: {x_user_id}")

    try:
        user = await repository.get(x_user_id)
        if not user:
            logger.warning(f"User not found for deletion with ID: {x_user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )

        deleted = await repository.delete(x_user_id)
        if not deleted:
            logger.error(f"Failed to delete user with ID: {x_user_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user.",
            )

        logger.info(f"Successfully deleted user with ID: {x_user_id}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting user {x_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while deleting user.",
        )

    except Exception as e:
        logger.error(
            f"Unexpected error while deleting user {x_user_id}: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting user.",
        )
