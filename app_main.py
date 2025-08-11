from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routes import session_routes
from db.mongo_client import connect_to_mongo, close_mongo_connection
from security.api_key_auth import get_api_key

app = FastAPI(
    title="CVP Lite - AI Mentor Backend",
    description="Backend API for CVP Lite with Swagger, API Key Auth, and MongoDB",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    session_routes.router,
    prefix="/api",
    dependencies=[Depends(get_api_key)],
    tags=["Sessions"],
)


@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()