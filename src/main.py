from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager

from src.api.routes import router as api_router, limiter
from src.database.connection import init_db


def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exceeded handler with informative error message."""
    response = JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "You have exceeded the rate limit. Please try again later.",
            "detail": str(exc.detail),
        },
    )
    response.headers["Retry-After"] = str(exc.retry_after)
    return response


app = FastAPI(
    title="Research Paper Summarizer",
    description="Retrieves and summarizes the latest arXiv papers based on your knowledge level.",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[settings.FRONTEND_ORIGIN],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
