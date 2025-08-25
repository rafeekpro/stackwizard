"""
Security Audit Logger Service
Logs security-related events for compliance and monitoring
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from uuid import UUID
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import select, func
from fastapi import Request

from app.db.database import Base
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Types of audit events"""
    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    TOKEN_REFRESH = "token_refresh"
    TOKEN_REVOKED = "token_revoked"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_COMPLETE = "password_reset_complete"
    
    # Authorization events
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PERMISSION_CHANGED = "permission_changed"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REVOKED = "role_revoked"
    
    # User management events
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_ACTIVATED = "user_activated"
    USER_DEACTIVATED = "user_deactivated"
    USER_VERIFIED = "user_verified"
    
    # Data access events
    DATA_ACCESSED = "data_accessed"
    DATA_CREATED = "data_created"
    DATA_UPDATED = "data_updated"
    DATA_DELETED = "data_deleted"
    DATA_EXPORTED = "data_exported"
    DATA_IMPORTED = "data_imported"
    
    # Security events
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    CSRF_VIOLATION = "csrf_violation"
    INVALID_TOKEN = "invalid_token"
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    
    # Admin events
    ADMIN_ACTION = "admin_action"
    CONFIG_CHANGED = "config_changed"
    SYSTEM_ACCESS = "system_access"


class AuditLogEntry(Base):
    """Database model for audit log entries"""
    __tablename__ = "audit_logs"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=UUID)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    event_type = Column(SQLEnum(AuditEventType), nullable=False, index=True)
    
    # User information
    user_id = Column(PGUUID(as_uuid=True), nullable=True, index=True)
    username = Column(String(255), nullable=True)
    
    # Request information
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(255), nullable=True)
    request_method = Column(String(10), nullable=True)
    request_path = Column(Text, nullable=True)
    
    # Event details
    resource_type = Column(String(100), nullable=True, index=True)
    resource_id = Column(String(255), nullable=True, index=True)
    action = Column(String(100), nullable=True)
    result = Column(String(50), nullable=True)  # success, failure, error
    
    # Additional data
    details = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    service_name = Column(String(100), nullable=True, default="stackwizard")
    environment = Column(String(50), nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": str(self.id),
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value if self.event_type else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "username": self.username,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "request_id": self.request_id,
            "request_method": self.request_method,
            "request_path": self.request_path,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "action": self.action,
            "result": self.result,
            "details": self.details,
            "error_message": self.error_message,
            "service_name": self.service_name,
            "environment": self.environment
        }


class SecurityAuditLogger:
    """Service for logging security-related events"""
    
    def __init__(self):
        self.service_name = "stackwizard"
        self.environment = settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else "production"
        
        # Configure structured logging
        self.structured_logger = logging.getLogger("security.audit")
        self.structured_logger.setLevel(logging.INFO)
        
        # Add file handler for audit logs
        if hasattr(settings, 'AUDIT_LOG_FILE'):
            file_handler = logging.FileHandler(settings.AUDIT_LOG_FILE)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            self.structured_logger.addHandler(file_handler)
    
    def _extract_request_info(self, request: Optional[Request]) -> Dict[str, Any]:
        """Extract relevant information from request"""
        if not request:
            return {}
        
        info = {
            "ip_address": self._get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", "Unknown"),
            "request_method": request.method,
            "request_path": request.url.path,
        }
        
        # Add request ID if available
        if hasattr(request.state, "request_id"):
            info["request_id"] = request.state.request_id
        
        return info
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP address"""
        # Check for proxy headers
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        if request.client:
            return request.client.host
        
        return "Unknown"
    
    async def log_event(
        self,
        db: AsyncSession,
        event_type: AuditEventType,
        user_id: Optional[UUID] = None,
        username: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        result: str = "success",
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        request: Optional[Request] = None
    ) -> AuditLogEntry:
        """
        Log an audit event to the database
        
        Args:
            db: Database session
            event_type: Type of event
            user_id: ID of user performing action
            username: Username of user
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            action: Specific action performed
            result: Result of action (success, failure, error)
            details: Additional details as JSON
            error_message: Error message if applicable
            request: FastAPI request object
        """
        try:
            # Extract request information
            request_info = self._extract_request_info(request)
            
            # Create audit log entry
            audit_entry = AuditLogEntry(
                event_type=event_type,
                user_id=user_id,
                username=username,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id else None,
                action=action,
                result=result,
                details=details,
                error_message=error_message,
                service_name=self.service_name,
                environment=self.environment,
                **request_info
            )
            
            # Save to database
            db.add(audit_entry)
            await db.commit()
            await db.refresh(audit_entry)
            
            # Also log to structured logger
            log_data = audit_entry.to_dict()
            self.structured_logger.info(
                f"AUDIT: {event_type.value}",
                extra={"audit_data": json.dumps(log_data, default=str)}
            )
            
            # Log critical security events with higher severity
            if event_type in [
                AuditEventType.BRUTE_FORCE_ATTEMPT,
                AuditEventType.SUSPICIOUS_ACTIVITY,
                AuditEventType.CSRF_VIOLATION
            ]:
                self.structured_logger.warning(
                    f"SECURITY ALERT: {event_type.value}",
                    extra={"audit_data": json.dumps(log_data, default=str)}
                )
            
            return audit_entry
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
            # Don't raise exception to avoid breaking the main flow
            return None
    
    async def log_login_attempt(
        self,
        db: AsyncSession,
        email: str,
        success: bool,
        user_id: Optional[UUID] = None,
        error_message: Optional[str] = None,
        request: Optional[Request] = None
    ):
        """Log login attempt"""
        await self.log_event(
            db=db,
            event_type=AuditEventType.LOGIN_SUCCESS if success else AuditEventType.LOGIN_FAILED,
            user_id=user_id,
            username=email,
            action="login",
            result="success" if success else "failure",
            details={"email": email},
            error_message=error_message,
            request=request
        )
    
    async def log_data_access(
        self,
        db: AsyncSession,
        user_id: UUID,
        resource_type: str,
        resource_id: str,
        action: str = "read",
        request: Optional[Request] = None
    ):
        """Log data access event"""
        await self.log_event(
            db=db,
            event_type=AuditEventType.DATA_ACCESSED,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            result="success",
            request=request
        )
    
    async def log_admin_action(
        self,
        db: AsyncSession,
        admin_id: UUID,
        action: str,
        target_user_id: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ):
        """Log administrative action"""
        await self.log_event(
            db=db,
            event_type=AuditEventType.ADMIN_ACTION,
            user_id=admin_id,
            resource_type="user" if target_user_id else None,
            resource_id=str(target_user_id) if target_user_id else None,
            action=action,
            result="success",
            details=details,
            request=request
        )
    
    async def log_security_event(
        self,
        db: AsyncSession,
        event_type: AuditEventType,
        details: Dict[str, Any],
        user_id: Optional[UUID] = None,
        request: Optional[Request] = None
    ):
        """Log security-related event"""
        await self.log_event(
            db=db,
            event_type=event_type,
            user_id=user_id,
            result="detected",
            details=details,
            request=request
        )
    
    async def get_user_audit_logs(
        self,
        db: AsyncSession,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
        event_types: Optional[List[AuditEventType]] = None
    ) -> List[AuditLogEntry]:
        """Get audit logs for a specific user"""
        query = select(AuditLogEntry).where(
            AuditLogEntry.user_id == user_id
        )
        
        if event_types:
            query = query.where(AuditLogEntry.event_type.in_(event_types))
        
        query = query.order_by(AuditLogEntry.timestamp.desc())
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_recent_security_events(
        self,
        db: AsyncSession,
        hours: int = 24,
        limit: int = 100
    ) -> List[AuditLogEntry]:
        """Get recent security events"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        security_events = [
            AuditEventType.LOGIN_FAILED,
            AuditEventType.SUSPICIOUS_ACTIVITY,
            AuditEventType.RATE_LIMIT_EXCEEDED,
            AuditEventType.CSRF_VIOLATION,
            AuditEventType.INVALID_TOKEN,
            AuditEventType.BRUTE_FORCE_ATTEMPT
        ]
        
        query = select(AuditLogEntry).where(
            AuditLogEntry.event_type.in_(security_events),
            AuditLogEntry.timestamp >= cutoff_time
        )
        
        query = query.order_by(AuditLogEntry.timestamp.desc())
        query = query.limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def detect_brute_force(
        self,
        db: AsyncSession,
        ip_address: str,
        minutes: int = 5,
        threshold: int = 5
    ) -> bool:
        """
        Detect potential brute force attack from IP
        
        Returns True if threshold exceeded
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        
        query = select(func.count(AuditLogEntry.id)).where(
            AuditLogEntry.event_type == AuditEventType.LOGIN_FAILED,
            AuditLogEntry.ip_address == ip_address,
            AuditLogEntry.timestamp >= cutoff_time
        )
        
        result = await db.execute(query)
        count = result.scalar()
        
        if count >= threshold:
            # Log brute force detection
            await self.log_event(
                db=db,
                event_type=AuditEventType.BRUTE_FORCE_ATTEMPT,
                result="detected",
                details={
                    "ip_address": ip_address,
                    "failed_attempts": count,
                    "time_window_minutes": minutes
                }
            )
            return True
        
        return False


# Global instance
audit_logger = SecurityAuditLogger()