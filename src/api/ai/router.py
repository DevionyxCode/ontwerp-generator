from fastapi import APIRouter
from api.ai.erdtoclassdiagram.router import router as erdtoclassdiagram_router
from api.ai.userstorietoerd.router import router as userstorietoerd_router

router = APIRouter()

router.include_router(erdtoclassdiagram_router)
router.include_router(userstorietoerd_router)