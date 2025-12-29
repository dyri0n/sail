from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.utils.datetime_utils import now_chile

from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.db.session import SessionLocal
from app.services.audit_service import AuditService


class AuthService:

    def login(self, email: str, password: str, ip_address: str = None):
        db: Session = SessionLocal()

        try:
            user = db.query(User).filter(User.email == email).first()

            if not user or not verify_password(password, user.password_hash):
                AuditService.log_event(
                    action="LOGIN_FAILED",
                    username=email,
                    ip_address=ip_address,
                    level="WARNING",
                    metadata={"reason": "Invalid credentials"}
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales inválidas"
                )

            if not user.is_active:
                AuditService.log_event(
                    action="LOGIN_BLOCKED",
                    user_id=str(user.id),
                    username=user.username,
                    ip_address=ip_address,
                    level="WARNING",
                    metadata={"reason": "Inactive account"}
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cuenta desactivada"
                )

            # Update last login
            user.last_login_at = now_chile()
            db.commit()

            AuditService.log_event(
                action="LOGIN_SUCCESS",
                user_id=str(user.id),
                username=user.username,
                ip_address=ip_address,
                level="INFO",
                metadata={"login_at": now_chile().strftime("%Y-%m-%d %H:%M:%S")}
            )

            token = create_access_token(
                {
                    "sub": str(user.id),
                    "username": user.username,
                    "role": user.role,
                    "area": user.department # user.area was changed to department
                }
            )

            return token

        finally:
            db.close()
