from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from beanie import Document
from pydantic import BaseModel, Field
from pymongo import IndexModel


class ArticleStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    UNDER_REVIEW = "under_review"


class SolutionType(str, Enum):
    MANUAL_STEPS = "manual_steps"
    AUTOMATED_SCRIPT = "automated_script"
    ESCALATION_REQUIRED = "escalation_required"
    SELF_SERVICE_LINK = "self_service_link"
    KNOWLEDGE_ARTICLE = "knowledge_article"


class AutomatedAction(BaseModel):
    action_type: str  # e.g., "password_reset", "vpn_reconnect", "email_quota_increase"
    script_path: Optional[str] = None
    api_endpoint: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    success_message: str
    failure_message: str


class Solution(BaseModel):
    solution_type: SolutionType
    title: str
    description: str
    steps: List[str] = Field(default_factory=list)
    automated_action: Optional[AutomatedAction] = None
    estimated_resolution_time: int = 15  # minutes
    success_rate: float = 0.0  # percentage of successful resolutions
    last_tested: Optional[datetime] = None
    
    # Self-service options
    portal_link: Optional[str] = None
    video_tutorial_url: Optional[str] = None
    troubleshooting_guide: Optional[str] = None


class KnowledgeArticle(Document):
    # Basic information
    title: str
    description: str
    content: str
    
    # Classification and categorization
    category: str  # e.g., "VPN", "Password", "Email", "Hardware"
    subcategory: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)  # For search optimization
    
    # Problem identification
    problem_patterns: List[str] = Field(default_factory=list)  # Common ways users describe the issue
    error_codes: List[str] = Field(default_factory=list)
    symptoms: List[str] = Field(default_factory=list)
    
    # Solutions
    solutions: List[Solution] = Field(default_factory=list)
    primary_solution: Optional[Solution] = None
    
    # Metadata
    status: ArticleStatus = ArticleStatus.DRAFT
    author_id: str
    author_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_reviewed: Optional[datetime] = None
    
    # Usage statistics
    view_count: int = 0
    helpful_votes: int = 0
    unhelpful_votes: int = 0
    success_resolutions: int = 0
    total_attempts: int = 0
    
    # AI Enhancement
    ai_generated: bool = False
    confidence_score: float = 0.0
    related_articles: List[str] = Field(default_factory=list)
    
    # POWERGRID specific
    affected_systems: List[str] = Field(default_factory=list)  # e.g., ["GLPI", "Solman", "AD"]
    business_impact: str = "Low"  # Low, Medium, High, Critical
    escalation_team: Optional[str] = None
    
    class Settings:
        name = "knowledge_articles"
        indexes = [
            IndexModel([("category", 1)]),
            IndexModel([("tags", 1)]),
            IndexModel([("keywords", 1)]),
            IndexModel([("status", 1)]),
            IndexModel([("author_id", 1)]),
            IndexModel([("created_at", -1)]),
            IndexModel([("success_resolutions", -1)]),
            IndexModel([("confidence_score", -1)]),
            # Text search index for content
            IndexModel([("title", "text"), ("description", "text"), ("content", "text"), ("keywords", "text")]),
            # Compound indexes for common queries
            IndexModel([("category", 1), ("status", 1)]),
            IndexModel([("tags", 1), ("status", 1)])
        ]


class TicketResolution(Document):
    """Track how tickets were resolved to improve AI suggestions"""
    ticket_id: str
    original_query: str
    classified_category: str
    classified_subcategory: Optional[str] = None
    
    # Resolution details
    resolution_method: str  # "knowledge_base", "automated_action", "manual_resolution", "escalated"
    knowledge_article_id: Optional[str] = None
    solution_used: Optional[Solution] = None
    
    # Outcome
    resolved_successfully: bool
    resolution_time_minutes: int
    user_satisfaction: Optional[int] = None  # 1-5 rating
    user_feedback: Optional[str] = None
    
    # Learning data
    resolver_id: Optional[str] = None  # Who resolved it
    resolver_name: Optional[str] = None
    actual_solution: Optional[str] = None  # What actually worked
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "ticket_resolutions"
        indexes = [
            IndexModel([("ticket_id", 1)], unique=True),
            IndexModel([("classified_category", 1)]),
            IndexModel([("resolution_method", 1)]),
            IndexModel([("resolved_successfully", 1)]),
            IndexModel([("created_at", -1)]),
            IndexModel([("knowledge_article_id", 1)]),
            IndexModel([("resolver_id", 1)])
        ]


class CommonIssuePattern(Document):
    """AI-learned patterns for better classification"""
    pattern: str
    category: str
    subcategory: Optional[str] = None
    confidence: float
    occurrences: int = 1
    success_rate: float = 0.0
    
    # Context
    typical_keywords: List[str] = Field(default_factory=list)
    seasonal_trend: bool = False  # e.g., VPN issues spike during work-from-home
    user_roles_affected: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "common_issue_patterns"
        indexes = [
            IndexModel([("pattern", "text")]),
            IndexModel([("category", 1)]),
            IndexModel([("confidence", -1)]),
            IndexModel([("occurrences", -1)]),
            IndexModel([("success_rate", -1)])
        ]
