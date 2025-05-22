from fastapi import APIRouter

from src.modules.reg_module.routes import router as auth_router

main_router = APIRouter()
main_router.include_router(auth_router)
