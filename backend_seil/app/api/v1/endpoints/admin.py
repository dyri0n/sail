from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.services.user_service import UserService
from app.services.audit_service import AuditService
from app.schemas.users import UserStatsResponse
from app.schemas.listUsers import UserListResponse
from app.schemas.user_create import UserCreateRequest
from app.schemas.editUser import UserUpdateRequest, PasswordResetRequest
from app.core.permissions import require_role
from app.core.dependencies import get_current_user
from app.core.security import hash_password

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/users/stats",
    response_model=UserStatsResponse,
    dependencies=[Depends(require_role("ADMIN"))]
)
def get_user_stats():
    return UserService().get_stats()

@router.get(
    "/users",
    response_model=UserListResponse,
    dependencies=[Depends(require_role("ADMIN"))]
)
def list_users():
    return UserService().list_users()

@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("ADMIN"))]
)
def create_user(
    payload: UserCreateRequest,
    request: Request,
    current_user=Depends(get_current_user)
):
    user, error = UserService().create_user(payload.dict())
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    # Log the user creation
    AuditService.log_event(
        action="USER_CREATE",
        user_id=current_user.get("sub"),
        username=current_user.get("username"),
        resource="ADMIN",
        ip_address=request.client.host,
        level="INFO",
        metadata={
            "new_user_id": str(user.id),
            "new_username": user.username,
            "new_user_role": user.role
        }
    )
    
    return {"message": "Usuario creado correctamente", "id": str(user.id)}

@router.put("/users/{user_id}", dependencies=[Depends(require_role("ADMIN"))])
def update_user(
    user_id: str,
    payload: UserUpdateRequest,
    request: Request,
    current_user=Depends(get_current_user)
):
    user = UserService().update_user(user_id, payload.dict())
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    # Log the user update
    AuditService.log_event(
        action="USER_UPDATE",
        user_id=current_user.get("sub"),
        username=current_user.get("username"),
        resource="ADMIN",
        ip_address=request.client.host,
        level="INFO",
        metadata={
            "updated_user_id": user_id,
            "updated_fields": list(payload.dict(exclude_unset=True).keys())
        }
    )
    
    return {"message": "Usuario actualizado correctamente"}

@router.delete("/users/{user_id}", dependencies=[Depends(require_role("ADMIN"))])
def deactivate_user(
    user_id: str,
    request: Request,
    current_user=Depends(get_current_user)
):
    success = UserService().deactivate_user(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    # Log the user deactivation
    AuditService.log_event(
        action="USER_DEACTIVATE",
        user_id=current_user.get("sub"),
        username=current_user.get("username"),
        resource="ADMIN",
        ip_address=request.client.host,
        level="AUDIT",
        metadata={"deactivated_user_id": user_id}
    )
    
    return {"message": "Usuario desactivado correctamente"}

@router.post("/users/{user_id}/reset-password", dependencies=[Depends(require_role("ADMIN"))])
def reset_password(
    user_id: str,
    payload: PasswordResetRequest,
    request: Request,
    current_user=Depends(get_current_user)
):
    new_hash = hash_password(payload.new_password)
    success = UserService().reset_password(user_id, new_hash)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    # Log the password reset
    AuditService.log_event(
        action="USER_PASSWORD_RESET",
        user_id=current_user.get("sub"),
        username=current_user.get("username"),
        resource="ADMIN",
        ip_address=request.client.host,
        level="AUDIT",
        metadata={"target_user_id": user_id}
    )
    
    return {"message": "Contraseña restablecida correctamente"}
