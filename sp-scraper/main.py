import uvicorn

from core.config import API_PORT, API_HOST

if __name__ == "__main__":
    uvicorn.run(
        app="api:api",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        workers=1,
    )
