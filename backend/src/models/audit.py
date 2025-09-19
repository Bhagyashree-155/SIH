from datetime import datetime
from typing import Optional, Dict, Any
from beanie import Document
from pydantic import Field
from pymongo import IndexModel


class AuditLog(Document):
    event_type: str  # LOGIN, LOGOUT, TICKET_CREATED, etc.
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource_type: Optional[str] = None  # user, ticket, knowledge_base, etc.
    resource_id: Optional[str] = None
    action: str  # CREATE, READ, UPDATE, DELETE
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    success: bool = True
    error_message: Optional[str] = None
    
    class Settings:
        name = "audit_logs"
        indexes = [
            IndexModel([("timestamp", -1)]),
            IndexModel([("user_id", 1)]),
            IndexModel([("event_type", 1)]),
            IndexModel([("resource_type", 1), ("resource_id", 1)]),
            IndexModel([("success", 1)]),
            IndexModel([("timestamp", -1), ("user_id", 1)])
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "LOGIN_SUCCESS",
                "user_id": "507f1f77bcf86cd799439011",
                "user_email": "user@powergrid.in",
                "action": "LOGIN",
                "details": {"login_time": "2023-12-01T10:30:00Z"},
                "success": True
            }
        }
