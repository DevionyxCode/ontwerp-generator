from fastapi import APIRouter
from api.erd.router import router as erd_router
from api.userstories.router import router as userstories_router
from api.scrumboard.router import router as scrumboard_router
from api.classdiagram.router import router as classdiagram_router
from api.narratives.router import router as narratives_router
from api.usecases.router import router as usecases_router
from api.ai.router import router as ai_router

router = APIRouter()

router.include_router(erd_router, prefix="/erd")
router.include_router(userstories_router, prefix="/userstories")
router.include_router(scrumboard_router, prefix="/scrumboard")
router.include_router(classdiagram_router, prefix="/classdiagram")
router.include_router(narratives_router, prefix="/narratives")
router.include_router(usecases_router, prefix="/usecases")
router.include_router(ai_router, prefix="/ai")