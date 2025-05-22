from fastapi import APIRouter, Depends

from src.modules.reg_module.jwt_module.depends import _get_access_token_from_headers
from src.modules.reg_module.routes import router as auth_router

main_router = APIRouter()
main_router.include_router(auth_router)


@main_router.post("/test")
async def test(_: None = Depends(_get_access_token_from_headers)):
    pass
