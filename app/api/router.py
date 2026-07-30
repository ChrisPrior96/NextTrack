from fastapi import APIRouter

from app.api.routes import catalogue, health, recommend

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(recommend.router)
api_router.include_router(catalogue.router)
