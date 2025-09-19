from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any
from src.models.ticket import Ticket, TicketCategory, TicketPriority, TicketStatus
from src.ai.gemini_service import gemini_service

router = APIRouter()

@router.get("/")
async def get_ticket_classifications() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get ticket classifications by category, priority, and status
    """
    try:
        # Get all tickets
        tickets = await Ticket.find_all().to_list()
        
        # Initialize counters
        categories = {}
        priorities = {}
        statuses = {}
        
        # Count tickets by classification
        for ticket in tickets:
            # Category
            category = ticket.category.value if ticket.category else "Other"
            if category in categories:
                categories[category] += 1
            else:
                categories[category] = 1
                
            # Priority
            priority = ticket.priority.value if ticket.priority else "Medium"
            if priority in priorities:
                priorities[priority] += 1
            else:
                priorities[priority] = 1
                
            # Status
            status = ticket.status.value if ticket.status else "Open"
            if status in statuses:
                statuses[status] += 1
            else:
                statuses[status] = 1
        
        # Format response
        return {
            "categories": [{"name": k, "count": v} for k, v in categories.items()],
            "priorities": [{"name": k, "count": v} for k, v in priorities.items()],
            "statuses": [{"name": k, "count": v} for k, v in statuses.items()]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ticket classifications: {str(e)}")

@router.get("/ai-categories")
async def get_ai_categories() -> Dict[str, List[str]]:
    """
    Get AI-defined ticket categories and subcategories
    """
    try:
        # Get categories from the Gemini service
        categories = gemini_service.categories
        
        # Format response
        return {
            "categories": list(categories.keys()),
            "subcategories": {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting AI categories: {str(e)}")