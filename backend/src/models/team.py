from datetime import datetime
from typing import List, Optional
from enum import Enum
from beanie import Document
from pydantic import BaseModel, Field
from pymongo import IndexModel


class TeamMember(BaseModel):
    user_id: str
    username: str
    full_name: str
    role: str
    is_lead: bool = False
    joined_at: datetime = Field(default_factory=datetime.utcnow)


class Team(Document):
    name: str
    description: Optional[str] = None
    department: str
    
    # Team members
    members: List[TeamMember] = Field(default_factory=list)
    lead_id: Optional[str] = None
    
    # Skills and categories this team handles
    skills: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    
    # Status and settings
    is_active: bool = True
    max_concurrent_tickets: int = 50
    
    # Business hours (24-hour format)
    business_hours_start: str = "09:00"
    business_hours_end: str = "17:00"
    business_days: List[str] = Field(default_factory=lambda: ["monday", "tuesday", "wednesday", "thursday", "friday"])
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "teams"
        indexes = [
            IndexModel([("name", 1)], unique=True),
            IndexModel([("department", 1)]),
            IndexModel([("is_active", 1)]),
            IndexModel([("skills", 1)]),
            IndexModel([("categories", 1)]),
            IndexModel([("members.user_id", 1)])
        ]
