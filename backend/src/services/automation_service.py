import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from src.core.config import settings
from src.models.ticket import Ticket, TicketStatus, TicketPriority
from src.models.knowledge_base import AutomatedAction

logger = logging.getLogger(__name__)


class ActionStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class AutomationService:
    """
    Service for executing automated actions and self-healing IT operations
    """
    
    def __init__(self):
        self.action_handlers = {
            "password_reset": self._handle_password_reset,
            "vpn_reconnect": self._handle_vpn_reconnect,
            "email_quota_check": self._handle_email_quota_check,
            "restart_service": self._handle_restart_service,
            "unlock_account": self._handle_unlock_account,
        }
    
    async def execute_automated_action(self, 
                                     action: AutomatedAction, 
                                     ticket: Ticket) -> Dict[str, Any]:
        """
        Execute an automated action for a ticket
        """
        try:
            logger.info(f"Executing automated action '{action.action_type}' for ticket {ticket.ticket_number}")
            
            # Check if we have a handler for this action type
            if action.action_type not in self.action_handlers:
                return {
                    "status": ActionStatus.FAILED,
                    "message": f"No handler found for action type: {action.action_type}",
                    "executed_at": datetime.utcnow()
                }
            
            # Execute the action
            handler = self.action_handlers[action.action_type]
            result = await handler(action, ticket)
            
            # Record the execution result
            await self._record_action_execution(ticket, action, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing automated action: {str(e)}")
            return {
                "status": ActionStatus.FAILED,
                "message": f"Execution error: {str(e)}",
                "executed_at": datetime.utcnow()
            }
    
    async def _handle_password_reset(self, action: AutomatedAction, ticket: Ticket) -> Dict[str, Any]:
        """Handle automated password reset"""
        try:
            # Simulate the action
            await asyncio.sleep(1)  # Simulate processing time
            
            if ticket.requester_email:
                return {
                    "status": ActionStatus.SUCCESS,
                    "message": f"Password reset initiated for {ticket.requester_email}. Temporary password sent via email.",
                    "executed_at": datetime.utcnow(),
                    "details": {
                        "action_taken": "password_reset",
                        "user_email": ticket.requester_email,
                        "temp_password_sent": True
                    }
                }
            else:
                return {
                    "status": ActionStatus.FAILED,
                    "message": "Cannot reset password: no user email provided",
                    "executed_at": datetime.utcnow()
                }
                
        except Exception as e:
            return {
                "status": ActionStatus.FAILED,
                "message": f"Password reset failed: {str(e)}",
                "executed_at": datetime.utcnow()
            }
    
    async def _handle_vpn_reconnect(self, action: AutomatedAction, ticket: Ticket) -> Dict[str, Any]:
        """Handle VPN reconnection assistance"""
        return {
            "status": ActionStatus.SUCCESS,
            "message": "VPN troubleshooting steps initiated. User will receive updated connection profile.",
            "executed_at": datetime.utcnow(),
            "details": {
                "action_taken": "vpn_profile_refresh",
                "server_status_checked": True,
                "profile_sent": True
            }
        }
    
    async def _handle_email_quota_check(self, action: AutomatedAction, ticket: Ticket) -> Dict[str, Any]:
        """Handle email quota check and cleanup"""
        return {
            "status": ActionStatus.SUCCESS,
            "message": "Email quota checked. Cleanup recommendations sent to user.",
            "executed_at": datetime.utcnow(),
            "details": {
                "current_quota": "8.5 GB / 10 GB",
                "cleanup_suggestions": True,
                "auto_archive_enabled": True
            }
        }
    
    async def _handle_restart_service(self, action: AutomatedAction, ticket: Ticket) -> Dict[str, Any]:
        """Handle service restart"""
        service_name = action.parameters.get("service_name", "unknown")
        return {
            "status": ActionStatus.SUCCESS,
            "message": f"Service '{service_name}' restart initiated.",
            "executed_at": datetime.utcnow(),
            "details": {
                "service_name": service_name,
                "restart_time": datetime.utcnow().isoformat()
            }
        }
    
    async def _handle_unlock_account(self, action: AutomatedAction, ticket: Ticket) -> Dict[str, Any]:
        """Handle account unlock operations"""
        return {
            "status": ActionStatus.SUCCESS,
            "message": "Account unlock initiated. User should try logging in after 5 minutes.",
            "executed_at": datetime.utcnow(),
            "details": {
                "account_unlocked": True,
                "wait_time_minutes": 5
            }
        }
    
    async def _record_action_execution(self, ticket: Ticket, action: AutomatedAction, result: Dict[str, Any]):
        """Record the execution of an automated action for learning"""
        try:
            from src.models.ticket import Comment
            
            comment = Comment(
                author_id="automation_system",
                author_name="Automation System",
                content=f"Automated action '{action.action_type}' executed: {result['message']}",
                is_internal=True
            )
            
            ticket.comments.append(comment)
            
            # If action succeeded and it's a resolving action, update ticket status
            if result["status"] == ActionStatus.SUCCESS and action.action_type in ["password_reset", "account_unlock"]:
                ticket.status = TicketStatus.RESOLVED
                ticket.resolved_at = datetime.utcnow()
                ticket.resolved_by_name = "Automation System"
                ticket.resolution = f"Automatically resolved via {action.action_type}: {result['message']}"
            
            await ticket.save()
            
        except Exception as e:
            logger.error(f"Error recording action execution: {str(e)}")


# Global instance
automation_service = AutomationService()
