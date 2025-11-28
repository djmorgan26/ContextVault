from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        dict: Service status
    """
    return {"status": "healthy", "service": "context-vault-api"}
