from fastapi import APIRouter, status, Request, Depends
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login de usuario"
)
def login(payload: LoginRequest, request: Request):
    service = AuthService()
    token = service.login(payload.email, payload.password, ip_address=request.client.host)
    return {"access_token": token}

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(request: Request, current_user=Depends(get_current_user)):
    AuditService.log_event(
        action="LOGOUT",
        user_id=current_user.get("sub"),
        username=current_user.get("username"),
        ip_address=request.client.host,
        level="INFO"
    )
    return {"message": "Sesión cerrada correctamente"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.get("sub"),
        "username": current_user.get("username"),
        "role": current_user.get("role"),
        "area": current_user.get("area")
    }
