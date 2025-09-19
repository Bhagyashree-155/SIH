from fastapi import APIRouter, HTTPException, Depends, Query, Body, File, UploadFile, Form
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import json
import os

from src.models.ticket import Ticket, TicketStatus, TicketPriority, TicketCategory, TicketSource, Attachment
from src.models.user import User
from src.services.ingestion_service import ingestion_service
from src.services.knowledge_service import knowledge_service
from src.ai.gemini_service import gemini_service
from src.core.config import settings

router = APIRouter()


class ChatbotQueryRequest(BaseModel):
    query: str
    user_id: str
    user_email: str
    user_name: str
    context: Optional[Dict[str, Any]] = None


class FeedbackRequest(BaseModel):
    ticket_id: str
    helpful: bool
    feedback: Optional[str] = None
    rating: Optional[int] = None


class TicketUpdateRequest(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to_id: Optional[str] = None
    notes: Optional[str] = None


class WebFormTicketRequest(BaseModel):
    title: str
    description: str
    user_id: Optional[str] = None
    email: str
    name: str
    location: Optional[str] = None
    asset_tag: Optional[str] = None
    priority: Optional[TicketPriority] = TicketPriority.MEDIUM
    category: Optional[TicketCategory] = None


class GLPITicketRequest(BaseModel):
    ticket_data: Dict[str, Any]
    api_key: str = Field(..., description="API key for authentication")


class SolmanTicketRequest(BaseModel):
    ticket_data: Dict[str, Any]
    api_key: str = Field(..., description="API key for authentication")


class EmailTicketRequest(BaseModel):
    email_data: Dict[str, Any]
    api_key: str = Field(..., description="API key for authentication")


@router.post("/chatbot")
async def process_chatbot_query(request: ChatbotQueryRequest):
    """
    Process a chatbot query with AI classification and solution generation.
    This is the main entry point for user queries.
    """
    try:
        result = await ingestion_service.ingest_chatbot_query(
            user_query=request.query,
            user_id=request.user_id,
            user_email=request.user_email,
            user_name=request.user_name,
            user_context=request.context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/")
async def get_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
    category: Optional[TicketCategory] = None,
    requester_email: Optional[str] = None,
    assigned_to_id: Optional[str] = None
):
    """
    Get tickets with filtering and pagination
    """
    try:
        # Build query filter
        query_filter = {}
        if status:
            query_filter["status"] = status
        if priority:
            query_filter["priority"] = priority
        if category:
            query_filter["category"] = category
        if requester_email:
            query_filter["requester_email"] = requester_email
        if assigned_to_id:
            query_filter["assigned_to_id"] = assigned_to_id
        
        # Get tickets
        tickets = await Ticket.find(query_filter).skip(skip).limit(limit).sort("-created_at").to_list()
        
        # Get total count for pagination
        total = await Ticket.find(query_filter).count()
        
        return {
            "tickets": tickets,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tickets: {str(e)}")


@router.get("/{ticket_id}")
async def get_ticket(ticket_id: str):
    """
    Get a specific ticket by ID with AI-generated suggestions if still open
    """
    try:
        ticket = await Ticket.get(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        result = {
            "ticket": ticket,
            "suggestions": []
        }
        
        # If ticket is still open, provide AI suggestions
        if ticket.status in [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]:
            try:
                # Re-classify and get fresh solutions
                classification = await gemini_service.classify_ticket(
                    ticket.description, 
                    {"priority": ticket.priority.value}
                )
                solutions = await knowledge_service.find_solutions(
                    classification, ticket.description
                )
                result["suggestions"] = solutions
            except Exception as ai_error:
                # Don't fail the request if AI suggestions fail
                result["ai_error"] = str(ai_error)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching ticket: {str(e)}")


@router.put("/{ticket_id}")
async def update_ticket(ticket_id: str, update: TicketUpdateRequest):
    """
    Update a ticket status, priority, or assignment
    """
    try:
        ticket = await Ticket.get(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Update fields
        if update.status:
            ticket.status = update.status
        if update.priority:
            ticket.priority = update.priority
        if update.assigned_to_id:
            ticket.assigned_to_id = update.assigned_to_id
            # Could also set assigned_to_name by looking up user
        
        # Add notes as comment if provided
        if update.notes:
            from src.models.ticket import Comment
            comment = Comment(
                author_id="system",  # Should be actual user ID
                author_name="System",
                content=update.notes,
                is_internal=True
            )
            ticket.comments.append(comment)
        
        ticket.updated_at = datetime.utcnow()
        await ticket.save()
        
        return {"message": "Ticket updated successfully", "ticket": ticket}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating ticket: {str(e)}")


@router.post("/{ticket_id}/feedback")
async def submit_feedback(ticket_id: str, feedback: FeedbackRequest):
    """
    Submit feedback for a ticket resolution
    """
    try:
        ticket = await Ticket.get(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Update satisfaction rating
        if feedback.rating:
            ticket.satisfaction_rating = feedback.rating
        if feedback.feedback:
            ticket.satisfaction_feedback = feedback.feedback
        
        await ticket.save()
        
        # Record resolution for learning if ticket was resolved
        if ticket.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
            try:
                # This would need the original classification - simplified for demo
                from src.ai.gemini_service import ClassificationResult
                
                # Record the resolution for knowledge base learning
                await knowledge_service.record_resolution(
                    ticket.description,
                    ticket.resolution,
                    ticket.category,
                    ticket.resolved_at - ticket.created_at if ticket.resolved_at else None
                )
                
                return {"message": "Feedback submitted and resolution recorded for learning"}
            except Exception as e:
                # Don't fail if knowledge recording fails
                return {"message": "Feedback submitted", "warning": f"Knowledge recording failed: {str(e)}"}
        
        return {"message": "Feedback submitted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")


@router.post("/web-form")
async def create_web_form_ticket(request: WebFormTicketRequest):
    """
    Create a ticket from web form submission
    """
    try:
        # Convert to dictionary for ingestion service
        form_data = request.dict()
        
        # Process the ticket through ingestion service
        ticket = await ingestion_service.ingest_from_web_form(form_data)
        
        return {
            "status": "success",
            "message": "Ticket created successfully",
            "ticket_id": str(ticket.id),
            "ticket_number": ticket.ticket_number
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {str(e)}")


@router.post("/web-form/with-attachments")
async def create_web_form_ticket_with_attachments(
    title: str = Form(...),
    description: str = Form(...),
    email: str = Form(...),
    name: str = Form(...),
    user_id: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    asset_tag: Optional[str] = Form(None),
    priority: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    files: List[UploadFile] = File([])
):
    """
    Create a ticket from web form submission with file attachments
    """
    try:
        # Convert form data to dictionary
        form_data = {
            "title": title,
            "description": description,
            "email": email,
            "name": name,
            "user_id": user_id,
            "location": location,
            "asset_tag": asset_tag,
            "priority": priority,
            "category": category,
            "attachments": []
        }
        
        # Process file uploads
        if files:
            upload_dir = os.path.join(settings.UPLOAD_DIR, datetime.utcnow().strftime("%Y%m%d"))
            os.makedirs(upload_dir, exist_ok=True)
            
            for file in files:
                file_path = os.path.join(upload_dir, file.filename)
                
                # Save the file
                with open(file_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # Add to attachments list
                form_data["attachments"].append({
                    "filename": file.filename,
                    "path": file_path,
                    "size": len(content),
                    "content_type": file.content_type
                })
        
        # Process the ticket through ingestion service
        ticket = await ingestion_service.ingest_from_web_form(form_data)
        
        return {
            "status": "success",
            "message": "Ticket created successfully with attachments",
            "ticket_id": str(ticket.id),
            "ticket_number": ticket.ticket_number,
            "attachments_count": len(ticket.attachments)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {str(e)}")


@router.post("/glpi")
async def ingest_glpi_ticket(request: GLPITicketRequest):
    """
    Ingest a ticket from GLPI system
    """
    try:
        # Validate API key
        if request.api_key != settings.INTEGRATION_API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Process the ticket through ingestion service
        ticket = await ingestion_service.ingest_from_glpi(request.ticket_data)
        
        return {
            "status": "success",
            "message": "GLPI ticket ingested successfully",
            "ticket_id": str(ticket.id),
            "ticket_number": ticket.ticket_number
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting GLPI ticket: {str(e)}")


@router.post("/solman")
async def ingest_solman_ticket(request: SolmanTicketRequest):
    """
    Ingest a ticket from SAP Solution Manager
    """
    try:
        # Validate API key
        if request.api_key != settings.INTEGRATION_API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Process the ticket through ingestion service
        ticket = await ingestion_service.ingest_from_solman(request.ticket_data)
        
        return {
            "status": "success",
            "message": "Solman ticket ingested successfully",
            "ticket_id": str(ticket.id),
            "ticket_number": ticket.ticket_number
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting Solman ticket: {str(e)}")


@router.post("/email")
async def ingest_email_ticket(request: EmailTicketRequest):
    """
    Ingest a ticket from email
    """
    try:
        # Validate API key
        if request.api_key != settings.INTEGRATION_API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Process the ticket through ingestion service
        ticket = await ingestion_service.ingest_from_email(request.email_data)
        
        return {
            "status": "success",
            "message": "Email ticket ingested successfully",
            "ticket_id": str(ticket.id),
            "ticket_number": ticket.ticket_number
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting email ticket: {str(e)}")


@router.post("/unified")
async def ingest_unified_ticket(source: TicketSource, data: Dict[str, Any], api_key: str):
    """
    Unified endpoint for ingesting tickets from any source
    """
    try:
        # Validate API key
        if api_key != settings.INTEGRATION_API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Process the ticket through unified ingestion method
        ticket = await ingestion_service.ingest_ticket(source, data)
        
        return {
            "status": "success",
            "message": f"Ticket from {source.value} ingested successfully",
            "ticket_id": str(ticket.id),
            "ticket_number": ticket.ticket_number
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting ticket: {str(e)}")


@router.get("/search/suggestions")
async def search_solutions(q: str = Query(..., min_length=3)):
    """
    Search for solutions based on a query - used for real-time suggestions
    """
    try:
        # First try knowledge base search
        articles = await knowledge_service.search_articles(q, limit=5)
        
        # If no good articles found, use AI to generate suggestions
        if not articles:
            classification = await gemini_service.classify_ticket(q)
            solutions = await knowledge_service.find_solutions(classification, q)
            
            return {
                "query": q,
                "classification": classification,
                "solutions": solutions,
                "articles": []
            }
        
        return {
            "query": q,
            "articles": articles,
            "solutions": []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching solutions: {str(e)}")


@router.get("/analytics/trending")
async def get_trending_issues():
    """
    Get trending issues and analytics
    """
    try:
        trending = await knowledge_service.get_trending_issues()
        return {"trending_issues": trending}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")
