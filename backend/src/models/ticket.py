from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from beanie import Document
from pydantic import BaseModel, Field
from pymongo import IndexModel


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class TicketCategory(str, Enum):
    NETWORK = "network"
    HARDWARE = "hardware"
    SOFTWARE = "software"
    ACCESS_CONTROL = "access_control"
    EMAIL = "email"
    VPN = "vpn"
    PRINTER = "printer"
    PASSWORD_RESET = "password_reset"
    ACCOUNT_MANAGEMENT = "account_management"
    OTHER = "other"


class TicketSource(str, Enum):
    WEB_FORM = "web_form"
    EMAIL = "email"
    CHATBOT = "chatbot"
    PHONE = "phone"
    GLPI = "glpi"
    SOLMAN = "solman"
    WALK_IN = "walk_in"


class Attachment(BaseModel):
    filename: str
    file_path: str
    file_size: int
    content_type: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class Comment(BaseModel):
    author_id: str
    author_name: str
    content: str
    is_internal: bool = False
    attachments: List[Attachment] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AIAnalysis(BaseModel):
    classification_confidence: float
    predicted_category: TicketCategory
    predicted_priority: TicketPriority
    suggested_assignee: Optional[str] = None
    sentiment_score: float
    keywords: List[str] = Field(default_factory=list)
    similar_tickets: List[str] = Field(default_factory=list)
    auto_resolution_suggestions: List[str] = Field(default_factory=list)


class SLAInfo(BaseModel):
    response_time_hours: int
    resolution_time_hours: int
    first_response_deadline: Optional[datetime] = None
    resolution_deadline: Optional[datetime] = None
    first_response_at: Optional[datetime] = None
    is_breached: bool = False


class Ticket(Document):
    # Basic ticket information
    ticket_number: str = Field(..., unique=True)
    title: str
    description: str
    
    # Requestor information
    requester_id: str
    requester_email: str
    requester_name: str
    requester_phone: Optional[str] = None
    
    # Assignment and routing
    assigned_to_id: Optional[str] = None
    assigned_to_name: Optional[str] = None
    team_id: Optional[str] = None
    team_name: Optional[str] = None
    
    # Classification
    status: TicketStatus = TicketStatus.OPEN
    priority: TicketPriority = TicketPriority.MEDIUM
    category: TicketCategory = TicketCategory.OTHER
    subcategory: Optional[str] = None
    
    # Source and metadata
    source: TicketSource
    source_reference: Optional[str] = None  # External system reference
    tags: List[str] = Field(default_factory=list)
    
    # AI Analysis
    ai_analysis: Optional[AIAnalysis] = None
    
    # SLA Information
    sla_info: SLAInfo
    
    # Communication
    comments: List[Comment] = Field(default_factory=list)
    attachments: List[Attachment] = Field(default_factory=list)
    
    # Resolution
    resolution: Optional[str] = None
    resolution_category: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by_id: Optional[str] = None
    resolved_by_name: Optional[str] = None
    
    # Knowledge base linking
    related_articles: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None
    
    # Escalation
    escalation_level: int = 0
    escalated_at: Optional[datetime] = None
    escalated_to: Optional[str] = None
    
    # Custom fields for POWERGRID specific requirements
    location: Optional[str] = None
    asset_tag: Optional[str] = None
    cost_center: Optional[str] = None
    
    # Customer satisfaction
    satisfaction_rating: Optional[int] = None  # 1-5
    satisfaction_feedback: Optional[str] = None
    
    class Settings:
        name = "tickets"
        indexes = [
            IndexModel([("ticket_number", 1)], unique=True),
            IndexModel([("requester_id", 1)]),
            IndexModel([("assigned_to_id", 1)]),
            IndexModel([("team_id", 1)]),
            IndexModel([("status", 1)]),
            IndexModel([("priority", 1)]),
            IndexModel([("category", 1)]),
            IndexModel([("source", 1)]),
            IndexModel([("created_at", -1)]),
            IndexModel([("updated_at", -1)]),
            IndexModel([("status", 1), ("priority", 1)]),
            IndexModel([("tags", 1)]),
            IndexModel([("sla_info.is_breached", 1)])
        ]

    def generate_ticket_number(self) -> str:
        """Generate a unique ticket number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"PG-{timestamp}"
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "VPN Connection Issue",
                "description": "Unable to connect to VPN from home office",
                "requester_email": "employee@powergrid.in",
                "requester_name": "Jane Smith",
                "priority": "medium",
                "category": "vpn",
                "source": "web_form",
                "location": "Mumbai",
                "tags": ["vpn", "remote_access"]
            }
        }
