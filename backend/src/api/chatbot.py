from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
import uuid

from src.ai.gemini_service import gemini_service
from src.models.ticket import Ticket, TicketCategory, TicketPriority, TicketStatus, TicketSource, ChatMessage, SLAInfo
from src.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    user_id: str
    user_name: str
    user_email: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    ticket_id: str
    ticket_number: str
    category: str
    subcategory: Optional[str]
    priority: str
    confidence: float
    reasoning: str
    message: str
    suggested_solutions: List[Dict[str, Any]]


class ChatMessageRequest(BaseModel):
    message: str
    sender_id: str
    sender_name: str
    sender_type: str = "user"


@router.post("/classify", response_model=ChatResponse)
async def classify_and_create_ticket(request: ChatRequest):
    """
    Classify user query and create a ticket with AI analysis
    """
    try:
        # Classify the query using Gemini AI
        classification = await gemini_service.classify_ticket(
            user_query=request.message,
            user_context=request.context
        )
        
        # Generate unique ticket number
        ticket_number = Ticket.generate_ticket_number()
        
        # Create ticket
        ticket = Ticket(
            ticket_number=ticket_number,
            title=f"Query: {request.message[:50]}...",
            description=request.message,
            requester_id=request.user_id,
            requester_email=request.user_email,
            requester_name=request.user_name,
            category=TicketCategory(classification.category),
            subcategory=classification.subcategory,
            priority=TicketPriority(classification.priority.lower()),
            status=TicketStatus.OPEN,
            source=TicketSource.CHATBOT,
            ai_analysis={
                "classification_confidence": classification.confidence,
                "predicted_category": classification.category,
                "predicted_priority": classification.priority,
                "suggested_assignee": classification.suggested_assignee,
                "sentiment_score": classification.sentiment_score,
                "keywords": classification.suggested_keywords,
                "similar_tickets": classification.similar_tickets,
                "auto_resolution_suggestions": []
            },
            sla_info=SLAInfo(
                response_time_hours=4,
                resolution_time_hours=24
            ),
            chat_messages=[
                ChatMessage(
                    sender_id=request.user_id,
                    sender_name=request.user_name,
                    sender_type="user",
                    content=request.message
                )
            ]
        )
        
        # Save ticket to database
        await ticket.insert()
        
        # Generate AI response
        ai_response = f"Your query has been classified as '{classification.category}' with {classification.priority} priority. "
        ai_response += f"Confidence: {classification.confidence:.2f}. "
        ai_response += f"Reasoning: {classification.reasoning}"
        
        # Add AI response to chat
        ai_message = ChatMessage(
            sender_id="ai_system",
            sender_name="AI Assistant",
            sender_type="agent",
            content=ai_response
        )
        ticket.chat_messages.append(ai_message)
        await ticket.save()
        
        # Generate suggested solutions
        solutions = await gemini_service.generate_solution(
            classification=classification,
            user_query=request.message
        )
        
        suggested_solutions = []
        for solution in solutions:
            suggested_solutions.append({
                "title": solution.title,
                "description": solution.description,
                "steps": solution.steps,
                "solution_type": solution.solution_type.value,
                "confidence": solution.confidence,
                "estimated_time": solution.estimated_time
            })
        
        return ChatResponse(
            ticket_id=str(ticket.id),
            ticket_number=ticket.ticket_number,
            category=classification.category,
            subcategory=classification.subcategory,
            priority=classification.priority,
            confidence=classification.confidence,
            reasoning=classification.reasoning,
            message=ai_response,
            suggested_solutions=suggested_solutions
        )
        
    except Exception as e:
        logger.error(f"Error in ticket classification: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process your request")


@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    """
    Get ticket details including chat messages
    """
    try:
        ticket = await Ticket.get(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return {
            "ticket_id": str(ticket.id),
            "ticket_number": ticket.ticket_number,
            "title": ticket.title,
            "description": ticket.description,
            "category": ticket.category,
            "subcategory": ticket.subcategory,
            "priority": ticket.priority,
            "status": ticket.status,
            "requester_name": ticket.requester_name,
            "requester_email": ticket.requester_email,
            "created_at": ticket.created_at,
            "chat_messages": [
                {
                    "message_id": msg.message_id,
                    "sender_name": msg.sender_name,
                    "sender_type": msg.sender_type,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "is_read": msg.is_read
                }
                for msg in ticket.chat_messages
            ],
            "ai_analysis": ticket.ai_analysis
        }
    except HTTPException:
        # Pass through 404 and other explicit statuses
        raise
    except Exception as e:
        logger.error(f"Error getting ticket: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve ticket")


@router.post("/tickets/{ticket_id}/message")
async def send_message(ticket_id: str, request: ChatMessageRequest):
    """
    Send a message to a ticket's chat
    """
    try:
        ticket = await Ticket.get(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Create new chat message
        new_message = ChatMessage(
            sender_id=request.sender_id,
            sender_name=request.sender_name,
            sender_type=request.sender_type,
            content=request.message
        )
        
        # Add message to ticket
        ticket.chat_messages.append(new_message)
        ticket.updated_at = datetime.utcnow()
        await ticket.save()
        
        return {
            "message_id": new_message.message_id,
            "timestamp": new_message.timestamp,
            "status": "Message sent successfully"
        }
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send message")


@router.get("/tickets")
async def get_tickets_by_category(category: Optional[str] = None, status: Optional[str] = None):
    """
    Get tickets filtered by category and status
    """
    try:
        query = {}
        if category:
            query["category"] = category
        if status:
            query["status"] = status
        
        tickets = await Ticket.find(query).sort("-created_at").limit(50).to_list()
        
        return {
            "tickets": [
                {
                    "ticket_id": str(ticket.id),
                    "ticket_number": ticket.ticket_number,
                    "title": ticket.title,
                    "category": ticket.category,
                    "subcategory": ticket.subcategory,
                    "priority": ticket.priority,
                    "status": ticket.status,
                    "requester_name": ticket.requester_name,
                    "created_at": ticket.created_at,
                    "last_message": ticket.chat_messages[-1].content if ticket.chat_messages else None,
                    "unread_count": len([msg for msg in ticket.chat_messages if not msg.is_read and msg.sender_type == "user"])
                }
                for ticket in tickets
            ]
        }
    except Exception as e:
        logger.error(f"Error getting tickets: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tickets")


@router.get("/categories")
async def get_categories():
    """
    Get available ticket categories
    """
    return {
        "categories": [
            {
                "key": "Hardware & Infrastructure",
                "name": "Hardware & Infrastructure",
                "description": "Hardware issues, system failures, and physical infrastructure problems"
            },
            {
                "key": "Software & Digital Services", 
                "name": "Software & Digital Services",
                "description": "Software issues, application errors, and digital service problems"
            },
            {
                "key": "Access & Security",
                "name": "Access & Security", 
                "description": "Access control, permissions, and security-related issues"
            }
        ]
    }
