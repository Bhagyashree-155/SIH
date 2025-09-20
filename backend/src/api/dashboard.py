from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import Dict, Any
from src.models.ticket import Ticket, TicketStatus
from src.models.user import User
from beanie import PydanticObjectId
import asyncio

router = APIRouter()

@router.get("/")
async def get_dashboard(user_email: str = None):
    """Get dashboard statistics and recent tickets for a specific user"""
    try:
        if not user_email:
            raise HTTPException(status_code=400, detail="User email is required")
            
        # Get current date for "today" calculations
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate total tickets for this user
        total_tickets = await Ticket.find(Ticket.requester_email == user_email).count()
        
        # Calculate open tickets for this user
        open_tickets = await Ticket.find(
            Ticket.requester_email == user_email,
            Ticket.status == TicketStatus.OPEN
        ).count()
        
        # Calculate resolved today for this user
        resolved_today = await Ticket.find(
            Ticket.requester_email == user_email,
            Ticket.status == TicketStatus.RESOLVED,
            Ticket.resolved_at >= today
        ).count()
        
        # Calculate average response time (simplified - using time between created_at and first response)
        # This is a simplified calculation - in real implementation, you'd track actual response times
        avg_response_time_hours = 2.4  # Placeholder - implement proper calculation
        
        # Get recent tickets for this user (last 10)
        recent_tickets = await Ticket.find(
            Ticket.requester_email == user_email
        ).sort([("created_at", -1)]).limit(10).to_list()
        
        # Format recent tickets for frontend
        formatted_tickets = []
        for ticket in recent_tickets:
            # Calculate time ago
            time_diff = datetime.utcnow() - ticket.created_at
            if time_diff.days > 0:
                time_ago = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                time_ago = f"{hours} hour{'s' if hours > 1 else ''} ago"
            else:
                minutes = time_diff.seconds // 60
                time_ago = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            
            formatted_tickets.append({
                "id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "title": ticket.title,
                "user": ticket.requester_name,
                "priority": ticket.priority.value.title(),
                "status": ticket.status.value.replace("_", " ").title(),
                "time": time_ago,
                "category": ticket.category.value,
                "requester_email": ticket.requester_email
            })
        
        return {
            "stats": {
                "total_tickets": total_tickets,
                "open_tickets": open_tickets,
                "resolved_today": resolved_today,
                "avg_response_time_hours": avg_response_time_hours
            },
            "recent_tickets": formatted_tickets
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard data: {str(e)}")

@router.post("/resolve-ticket/{ticket_id}")
async def resolve_ticket(ticket_id: str, user_email: str = None):
    """Mark a ticket as resolved (only if it belongs to the user)"""
    try:
        if not user_email:
            raise HTTPException(status_code=400, detail="User email is required")
            
        ticket = await Ticket.get(PydanticObjectId(ticket_id))
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
            
        # Verify the ticket belongs to the user
        if ticket.requester_email != user_email:
            raise HTTPException(status_code=403, detail="You can only resolve your own tickets")
        
        # Update ticket status
        ticket.status = TicketStatus.RESOLVED
        ticket.resolved_at = datetime.utcnow()
        ticket.resolved_by_id = "system"  # In real implementation, use actual user ID
        ticket.resolved_by_name = "AI Assistant"
        ticket.updated_at = datetime.utcnow()
        
        await ticket.save()
        
        return {
            "message": "Ticket resolved successfully",
            "ticket_id": str(ticket.id),
            "ticket_number": ticket.ticket_number
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resolving ticket: {str(e)}")

@router.get("/stats")
async def get_dashboard_stats(user_email: str = None):
    """Get only the statistics for dashboard cards for a specific user"""
    try:
        if not user_email:
            raise HTTPException(status_code=400, detail="User email is required")
            
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        total_tickets = await Ticket.find(Ticket.requester_email == user_email).count()
        open_tickets = await Ticket.find(
            Ticket.requester_email == user_email,
            Ticket.status == TicketStatus.OPEN
        ).count()
        resolved_today = await Ticket.find(
            Ticket.requester_email == user_email,
            Ticket.status == TicketStatus.RESOLVED,
            Ticket.resolved_at >= today
        ).count()
        
        return {
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "resolved_today": resolved_today,
            "avg_response_time_hours": 2.4  # Placeholder
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")
