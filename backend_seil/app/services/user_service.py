from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password
from app.services.audit_service import AuditService


class UserService:

    def get_stats(self):
        db = SessionLocal()
        try:
            total = db.query(User).count()
            active = db.query(User).filter(User.is_active.is_(True)).count()
            admins = db.query(User).filter(User.role == "ADMIN").count()
            last_access = db.query(func.max(User.last_login_at)).scalar()

            return {
                "total_users": total,
                "active_users": active,
                "admin_users": admins,
                "last_access": last_access
            }
        finally:
            db.close()

    def create_user(self, data: dict):
        db = SessionLocal()
        try:
            # Check if exists
            existing = db.query(User).filter(
                (User.email == data["email"]) | (User.username == data["username"])
            ).first()
            
            if existing:
                return None, "Email o username ya existe"
            
            # Default password
            hashed = hash_password("luckiaArica")
            
            new_user = User(
                name=data["name"],
                email=data["email"],
                username=data["username"],
                role=data["role"],
                department=data.get("department"),
                password_hash=hashed
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            AuditService.log_event(
                action="USER_CREATED",
                username=new_user.username,
                level="INFO",
                metadata={"created_user": new_user.username, "role": new_user.role}
            )
            
            return new_user, None
        finally:
            db.close()

    def list_users(self):
        db = SessionLocal()
        try:
            users = db.query(User).order_by(User.created_at.desc()).all()
            return {
                "users": [
                    {
                        "id": str(u.id),
                        "name": u.name,
                        "email": u.email,
                        "username": u.username,
                        "role": u.role,
                        "is_active": u.is_active,
                        "last_login_at": u.last_login_at,
                        "department": u.department
                    }
                    for u in users
                ]
            }
        finally:
            db.close()

    def update_user(self, user_id: str, data: dict):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            for key, value in data.items():
                setattr(user, key, value)
            
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()

    def deactivate_user(self, user_id: str):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            user.is_active = False
            db.commit()
            return True
        finally:
            db.close()

    def reset_password(self, user_id: str, new_password_hash: str):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            user.password_hash = new_password_hash
            db.commit()
            return True
        finally:
            db.close()

