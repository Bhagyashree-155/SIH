from datetime import datetime
from typing import Optional, List
from enum import Enum
from beanie import Document
from pydantic import BaseModel, EmailStr, Field
from pymongo import IndexModel


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    TECHNICIAN = "technician"
    END_USER = "end_user"
    ANALYST = "analyst"


class UserProfile(BaseModel):
    department: Optional[str] = None
    designation: Optional[str] = None
    phone: Optional[str] = None
    employee_id: Optional[str] = None
    location: Optional[str] = None
    manager_email: Optional[str] = None


class UserPreferences(BaseModel):
    email_notifications: bool = True
    sms_notifications: bool = False
    language: str = "en"
    timezone: str = "Asia/Kolkata"


class User(Document):
    email: EmailStr = Field(..., unique=True)
    username: str = Field(..., unique=True)
    full_name: str
    hashed_password: str
    role: UserRole = UserRole.END_USER
    profile: UserProfile = Field(default_factory=UserProfile)
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    
    # Status fields
    is_active: bool = True
    is_verified: bool = False
    last_login: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Team associations
    team_ids: List[str] = Field(default_factory=list)
    
    # Skills for routing (for technicians)
    skills: List[str] = Field(default_factory=list)
    
    class Settings:
        name = "users"
        indexes = [
            IndexModel([("email", 1)], unique=True),
            IndexModel([("username", 1)], unique=True),
            IndexModel([("employee_id", 1)]),
            IndexModel([("role", 1)]),
            IndexModel([("is_active", 1)]),
            IndexModel([("team_ids", 1)]),
            IndexModel([("skills", 1)])
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@powergrid.in",
                "username": "john.doe",
                "full_name": "John Doe",
                "role": "technician",
                "profile": {
                    "department": "IT Support",
                    "designation": "Senior Technician",
                    "phone": "+91-9876543210",
                    "employee_id": "EMP001",
                    "location": "Delhi",
                    "manager_email": "manager@powergrid.in"
                },
                "skills": ["network", "windows", "active_directory"]
            }
        }
