from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from beanie import Document
from pydantic import Field
from pymongo import IndexModel


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    PUSH = "push"


class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Document):
    recipient_id: str
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    
    # Message content
    title: str
    message: str
    channel: NotificationChannel
    priority: NotificationPriority = NotificationPriority.NORMAL
    
    # Related resource
    resource_type: Optional[str] = None  # ticket, user, system
    resource_id: Optional[str] = None
    
    # Status
    is_sent: bool = False
    is_read: bool = False
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Retry logic
    retry_count: int = 0
    max_retries: int = 3
    next_retry_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "notifications"
        indexes = [
            IndexModel([("recipient_id", 1)]),
            IndexModel([("is_sent", 1)]),
            IndexModel([("is_read", 1)]),
            IndexModel([("channel", 1)]),
            IndexModel([("priority", 1)]),
            IndexModel([("created_at", -1)]),
            IndexModel([("resource_type", 1), ("resource_id", 1)]),
            IndexModel([("next_retry_at", 1), ("is_sent", 1)])
        ]
