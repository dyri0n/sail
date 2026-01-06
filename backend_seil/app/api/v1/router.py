from fastapi import APIRouter
from app.api.v1.endpoints import auth, admin, audit

router = APIRouter()

router.include_router(auth.router)
router.include_router(admin.router)
router.include_router(audit.router)
