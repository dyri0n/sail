from app.db.session import SessionLocal
from app.models.audit import AuditLog
from app.utils.datetime_utils import now_chile
from sqlalchemy import func, desc
from typing import Optional, List, Dict, Any
from datetime import datetime

class AuditService:
    @staticmethod
    def log_event(
        action: str,
        user_id: str = None,
        username: str = None,
        resource: str = None,
        ip_address: str = None,
        level: str = "INFO",
        metadata: dict = None
    ):
        db = SessionLocal()
        try:
            log = AuditLog(
                user_id=user_id,
                username=username,
                action=action,
                resource=resource,
                ip_address=ip_address,
                level=level,
                metadata_json=metadata,
                timestamp=now_chile()
            )
            db.add(log)
            db.commit()
        finally:
            db.close()
    
    @staticmethod
    def get_logs(
        nivel: Optional[str] = None,
        modulo: Optional[str] = None,
        usuario: Optional[str] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Obtiene logs de auditoría con filtros opcionales
        
        Args:
            nivel: Filtro por nivel (INFO, WARN, ERROR, etc.)
            modulo: Filtro por módulo/recurso
            usuario: Filtro por username
            fecha_inicio: Fecha de inicio (ISO format)
            fecha_fin: Fecha de fin (ISO format)
            limit: Número máximo de logs a retornar
            offset: Número de logs a saltar (para paginación)
        """
        db = SessionLocal()
        try:
            query = db.query(AuditLog)
            
            # Aplicar filtros
            if nivel:
                query = query.filter(AuditLog.level == nivel)
            if modulo:
                query = query.filter(AuditLog.resource == modulo)
            if usuario:
                query = query.filter(AuditLog.username == usuario)
            if fecha_inicio:
                query = query.filter(AuditLog.timestamp >= datetime.fromisoformat(fecha_inicio))
            if fecha_fin:
                query = query.filter(AuditLog.timestamp <= datetime.fromisoformat(fecha_fin))
            
            # Ordenar por timestamp descendente (más reciente primero)
            query = query.order_by(desc(AuditLog.timestamp))
            
            # Aplicar paginación
            query = query.limit(limit).offset(offset)
            
            logs = query.all()
            
            # Convertir a diccionarios con el formato esperado por el frontend
            result = []
            for log in logs:
                # Mapear action a modulo
                modulo_map = {
                    'LOGIN_SUCCESS': 'AUTH',
                    'LOGIN_FAILED': 'AUTH',
                    'LOGIN_BLOCKED': 'AUTH',
                    'LOGOUT': 'AUTH',
                    'USER_CREATE': 'ADMIN',
                    'USER_UPDATE': 'ADMIN',
                    'USER_DEACTIVATE': 'ADMIN',
                    'USER_PASSWORD_RESET': 'ADMIN',
                    'ETL_TRIGGER': 'ETL',
                    'ETL_COMPLETE': 'ETL',
                    'ETL_FAILED': 'ETL',
                    'FILE_UPLOAD': 'FILES',
                    'FILE_DOWNLOAD': 'FILES'
                }
                
                # Mapear level a nivel en español
                nivel_map = {
                    'INFO': 'INFO',
                    'WARNING': 'WARN',
                    'ERROR': 'ERROR',
                    'SUCCESS': 'SUCCESS',
                    'DEBUG': 'DEBUG',
                    'AUDIT': 'AUDIT'
                }
                
                result.append({
                    'id': str(log.id),
                    'timestamp': log.timestamp.isoformat() if log.timestamp else now_chile().isoformat(),
                    'nivel': nivel_map.get(log.level, log.level),
                    'modulo': log.resource if log.resource else modulo_map.get(log.action, 'SYSTEM'),
                    'mensaje': log.action,
                    'usuario': log.username or 'sistema',
                    'ip': log.ip_address,
                    'detalles': log.metadata_json
                })
            
            return result
        finally:
            db.close()
    
    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """
        Calcula estadísticas de auditoría
        """
        db = SessionLocal()
        try:
            total = db.query(func.count(AuditLog.id)).scalar()
            errores = db.query(func.count(AuditLog.id)).filter(AuditLog.level == 'ERROR').scalar()
            
            # Contar eventos de auditoría (acciones críticas)
            audit_actions = ['USER_CREATE', 'USER_UPDATE', 'USER_DEACTIVATE', 'USER_PASSWORD_RESET']
            auditoria = db.query(func.count(AuditLog.id)).filter(
                AuditLog.action.in_(audit_actions)
            ).scalar()
            
            # Obtener último log
            last_log = db.query(AuditLog).order_by(desc(AuditLog.timestamp)).first()
            ultimo = last_log.timestamp.isoformat() if last_log and last_log.timestamp else now_chile().isoformat()
            
            return {
                'total': total or 0,
                'errores': errores or 0,
                'auditoria': auditoria or 0,
                'ultimo': ultimo
            }
        finally:
            db.close()
    
    @staticmethod
    def get_filter_values() -> Dict[str, List[str]]:
        """
        Obtiene valores únicos para los filtros
        """
        db = SessionLocal()
        try:
            # Niveles disponibles
            niveles_db = db.query(AuditLog.level).distinct().all()
            niveles = ['todos'] + [nivel[0] for nivel in niveles_db if nivel[0]]
            
            # Módulos/recursos disponibles
            modulos_db = db.query(AuditLog.resource).distinct().all()
            actions_db = db.query(AuditLog.action).distinct().all()
            
            # Combinar recursos y mapear actions a módulos
            modulos_set = set()
            for modulo in modulos_db:
                if modulo[0]:
                    modulos_set.add(modulo[0])
            
            # Mapear actions a módulos
            for action in actions_db:
                if action[0]:
                    if 'LOGIN' in action[0] or 'LOGOUT' in action[0]:
                        modulos_set.add('AUTH')
                    elif 'USER' in action[0]:
                        modulos_set.add('ADMIN')
                    elif 'ETL' in action[0]:
                        modulos_set.add('ETL')
                    elif 'FILE' in action[0]:
                        modulos_set.add('FILES')
            
            modulos = ['todos'] + sorted(list(modulos_set))
            
            # Usuarios disponibles
            usuarios_db = db.query(AuditLog.username).distinct().all()
            usuarios = ['todos'] + [usuario[0] for usuario in usuarios_db if usuario[0]]
            
            return {
                'niveles': niveles,
                'modulos': modulos,
                'usuarios': usuarios
            }
        finally:
            db.close()

