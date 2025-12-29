from fastapi import APIRouter, Depends, HTTPException, status
from app.services.user_service import UserService
from app.schemas.users import UserStatsResponse
from app.schemas.listUsers import UserListResponse
from app.schemas.user_create import UserCreateRequest
from app.schemas.editUser import UserUpdateRequest, PasswordResetRequest
from app.core.permissions import require_role
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
def create_user(payload: UserCreateRequest):
    user, error = UserService().create_user(payload.dict())
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return {"message": "Usuario creado correctamente", "id": str(user.id)}

@router.put("/users/{user_id}", dependencies=[Depends(require_role("ADMIN"))])
def update_user(user_id: str, payload: UserUpdateRequest):
    user = UserService().update_user(user_id, payload.dict())
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return {"message": "Usuario actualizado correctamente"}

@router.delete("/users/{user_id}", dependencies=[Depends(require_role("ADMIN"))])
def deactivate_user(user_id: str):
    success = UserService().deactivate_user(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return {"message": "Usuario desactivado correctamente"}

@router.post("/users/{user_id}/reset-password", dependencies=[Depends(require_role("ADMIN"))])
def reset_password(user_id: str, payload: PasswordResetRequest):
    new_hash = hash_password(payload.new_password)
    success = UserService().reset_password(user_id, new_hash)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return {"message": "Contraseña restablecida correctamente"}
