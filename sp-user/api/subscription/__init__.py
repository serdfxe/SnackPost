import logging
from typing import Annotated
from fastapi import APIRouter, Header, Depends, HTTPException, status, Response

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from datetime import datetime, timezone

from core.fastapi.dependencies import get_repository
from core.db.repository import DatabaseRepository

from app.models.subscription import Subscription
from app.models.user import User

from .dto import (
    SubscriptionResponseDTO,
    SubscriptionCreateDTO,
    SubscriptionUpdateDTO,
)


subscription_router = APIRouter(
    prefix="/subscription",
    tags=["subscription"],
)
logger = logging.getLogger(__name__)


SubscriptionRepository = Annotated[
    DatabaseRepository[Subscription],
    Depends(get_repository(Subscription)),
]

UserRepository = Annotated[
    DatabaseRepository[User],
    Depends(get_repository(User)),
]


@subscription_router.get(
    "/",
    response_model=SubscriptionResponseDTO,
    responses={
        200: {"description": "Subscription data retrieved successfully."},
        404: {"description": "Subscription not found."},
    },
)
async def get_subscription_route(
    repository: SubscriptionRepository,
    x_user_id: Annotated[int, Header()],
):
    """
    Get subscription data for the user associated with the provided X-User-Id.
    """
    logger.info(f"Attempting to fetch subscription for user ID: {x_user_id}")
    
    try:
        subscription = await repository.get(Subscription.user_id == x_user_id)
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching subscription for user {x_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred."
        )
        
    except Exception as e:
        logger.error(f"Unexpected error while fetching subscription for user {x_user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )
    
    if not subscription:
            logger.warning(f"Subscription not found for user ID: {x_user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found."
            )

    logger.info(f"Successfully retrieved subscription for user ID: {x_user_id}")
    return subscription


@subscription_router.post(
    "/",
    response_model=SubscriptionResponseDTO,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Subscription created successfully."},
        409: {"description": "Conflict. Subscription already exists."},
    },
)
async def create_subscription_route(
    repository: SubscriptionRepository,
    data: SubscriptionCreateDTO,
):
    """
    Create a new subscription for a user.
    """
    logger.info(f"Attempting to create subscription for user ID: {data.user_id}")
    logger.debug(f"Subscription creation data: {data.model_dump()}")

    try:
        subscription = await repository.create(**data.model_dump())
        logger.info(f"Successfully created subscription with ID: {subscription.id}")
        return subscription

    except IntegrityError as e:
        logger.warning(f"Subscription creation conflict: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subscription already exists for this user."
        )
    
    except SQLAlchemyError as e:
        logger.error(f"Database error during subscription creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred."
        )
    
    except Exception as e:
        logger.error(f"Unexpected error during subscription creation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )


@subscription_router.patch(
    "/",
    response_model=SubscriptionResponseDTO,
    responses={
        200: {"description": "Subscription updated successfully."},
        404: {"description": "Subscription not found."},
    },
)
async def update_subscription_route(
    repository: SubscriptionRepository,
    x_user_id: Annotated[int, Header()],
    data: SubscriptionUpdateDTO,
):
    """
    Update subscription for the user associated with the provided X-User-Id.
    """
    logger.info(f"Attempting to update subscription for user ID: {x_user_id}")
    logger.debug(f"Subscription update data: {data.model_dump()}")

    try:
        subscription = await repository.get(Subscription.user_id == x_user_id)
        if not subscription:
            logger.warning(f"Subscription not found for user ID: {x_user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found."
            )

        updated_data = data.model_dump(exclude_unset=True)
        updated_subscription = await repository.update(subscription.id, updated_data)
        
        logger.info(f"Successfully updated subscription for user ID: {x_user_id}")
        return updated_subscription

    except SQLAlchemyError as e:
        logger.error(f"Database error while updating subscription for user {x_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred."
        )
        
    except Exception as e:
        logger.error(f"Unexpected error while updating subscription for user {x_user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )


@subscription_router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Subscription deleted successfully."},
        404: {"description": "Subscription not found."},
    },
)
async def delete_subscription_route(
    repository: SubscriptionRepository,
    x_user_id: Annotated[int, Header()],
):
    """
    Delete subscription for the user associated with the provided X-User-Id.
    """
    logger.info(f"Attempting to delete subscription for user ID: {x_user_id}")

    try:
        subscription = await repository.get(Subscription.user_id == x_user_id)
        if not subscription:
            logger.warning(f"Subscription not found for user ID: {x_user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found."
            )

        deleted = await repository.delete(subscription.id)
        if not deleted:
            logger.error(f"Failed to delete subscription for user ID: {x_user_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete subscription."
            )

        logger.info(f"Successfully deleted subscription for user ID: {x_user_id}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting subscription for user {x_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while deleting subscription."
        )
        
    except Exception as e:
        logger.error(f"Unexpected error while deleting subscription for user {x_user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting subscription."
        )


@subscription_router.get("/check")
async def check_subscription_route(
    x_user_id: Annotated[int, Header()],
    subs_repository: SubscriptionRepository,
    user_repository: UserRepository,
    response: Response = Response(),
) -> bool:
    """
    Check if user has an active subscription.
    Returns True if subscription is active and not expired, False otherwise.
    """
    try:
        subscription = await subs_repository.get(Subscription.user_id == x_user_id)
        
        if not subscription or not subscription.is_active:
            return False

        if subscription.expires_at and subscription.expires_at < datetime.now(timezone.utc):
            return False

        response.headers["X-User-Id"] = str((await user_repository.get(User.user_id == x_user_id)).id)

        return True

    except Exception as e:
        logger.error(f"Error checking subscription for user {x_user_id}: {str(e)}", exc_info=True)
        return False
