from fastapi import Depends, HTTPException, status
from app.core.dependencies import get_current_user


def require_role(*roles: str):
    def checker(user=Depends(get_current_user)):
        if user.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes"
            )
        return user
    return checker
