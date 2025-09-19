import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
import json

from src.core.config import settings
from src.models.ticket import Ticket, TicketStatus, TicketPriority, TicketCategory, TicketSource, SLAInfo
from src.models.user import User
from src.ai.gemini_service import gemini_service, ClassificationResult
from src.services.knowledge_service import knowledge_service

logger = logging.getLogger(__name__)


class TicketIngestionService:
    """
    Service for ingesting tickets from multiple sources: GLPI, Solman, Chatbot, Email, Web Form
    Provides unified ticket processing and standardization across all sources
    """
    
    def __init__(self):
        self.glpi_session_token = None
        self.glpi_base_url = settings.GLPI_URL
        self.solman_base_url = settings.SOLMAN_URL
        self.email_polling_interval = settings.EMAIL_POLLING_INTERVAL
        self.email_credentials = {
            "username": settings.EMAIL_USERNAME,
            "password": settings.EMAIL_PASSWORD,
            "server": settings.EMAIL_SERVER,
            "port": settings.EMAIL_PORT,
            "use_ssl": settings.EMAIL_USE_SSL
        }
        self.source_adapters = {
            TicketSource.GLPI: self.ingest_from_glpi,
            TicketSource.SOLMAN: self.ingest_from_solman,
            TicketSource.EMAIL: self.ingest_from_email,
            TicketSource.WEB_FORM: self.ingest_from_web_form,
            TicketSource.CHATBOT: self.ingest_chatbot_query
        }
        
    async def ingest_chatbot_query(self, 
                                  user_query: str, 
                                  user_id: str,
                                  user_email: str,
                                  user_name: str,
                                  user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a chatbot query with AI classification and solution generation
        """
        try:
            logger.info(f"Processing chatbot query from {user_email}: {user_query}")
            
            # Step 1: Classify the query using Gemini AI
            classification = await gemini_service.classify_ticket(user_query, user_context)
            
            # Step 2: Find solutions based on classification
            solutions = await knowledge_service.find_solutions(classification, user_query, user_context)
            
            # Step 3: Check if this can be auto-resolved
            auto_resolution = await self._check_auto_resolution(classification, solutions, user_context)
            
            if auto_resolution["can_auto_resolve"]:
                # Auto-resolve without creating a ticket
                return {
                    "status": "resolved",
                    "classification": classification,
                    "solutions": solutions,
                    "auto_resolution": auto_resolution,
                    "message": "Your issue has been resolved automatically.",
                    "resolution_time": "Immediate"
                }
            else:
                # Create ticket for further processing
                ticket = await self._create_ticket_from_classification(
                    user_query, classification, user_id, user_email, user_name, TicketSource.CHATBOT
                )
                
                return {
                    "status": "ticket_created",
                    "ticket_id": str(ticket.id),
                    "ticket_number": ticket.ticket_number,
                    "classification": classification,
                    "solutions": solutions,
                    "estimated_resolution": f"{solutions[0].estimated_time} minutes" if solutions else "Unknown",
                    "message": "A ticket has been created. Here are some suggested solutions while we process it."
                }
                
        except Exception as e:
            logger.error(f"Error processing chatbot query: {str(e)}")
            # Create basic ticket as fallback
            ticket = await self._create_basic_ticket(
                user_query, user_id, user_email, user_name, TicketSource.CHATBOT
            )
            return {
                "status": "ticket_created",
                "ticket_id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "message": "A ticket has been created and will be processed by our support team.",
                "error": "AI classification temporarily unavailable"
            }
    
    async def _check_auto_resolution(self, 
                                    classification: ClassificationResult, 
                                    solutions: List,
                                    user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Check if a ticket can be auto-resolved based on classification and available solutions
        """
        # Auto-resolve criteria
        auto_resolvable_categories = ["Password"]  # Add more categories as needed
        
        can_auto_resolve = False
        auto_action = None
        
        if (classification.category in auto_resolvable_categories and 
            classification.confidence > 0.8 and solutions):
            
            # Check if top solution is self-service or automated
            top_solution = solutions[0]
            if (top_solution.solution_type.value in ["self_service_link", "automated_script"] and
                top_solution.confidence > 0.9):
                
                can_auto_resolve = True
                
                # If it has an automated action, prepare it
                if top_solution.automated_action:
                    auto_action = top_solution.automated_action
        
        return {
            "can_auto_resolve": can_auto_resolve,
            "auto_action": auto_action,
            "confidence": classification.confidence,
            "reasoning": f"Category: {classification.category}, Confidence: {classification.confidence}"
        }
    
    async def _create_ticket_from_classification(self, 
                                               user_query: str,
                                               classification: ClassificationResult,
                                               user_id: Optional[str],
                                               user_email: str,
                                               user_name: str,
                                               source: TicketSource,
                                               source_reference: Optional[str] = None,
                                               title: Optional[str] = None) -> Ticket:
        """
        Create a ticket from AI classification results
        
        Args:
            user_query: The original query or description from the user
            classification: AI classification result
            user_id: ID of the requester
            user_email: Email of the requester
            user_name: Name of the requester
            source: Source system (GLPI, Solman, Chatbot, etc.)
            source_reference: External system reference ID (optional)
            title: Custom title (optional, will be generated if not provided)
            
        Returns:
            Created Ticket object
        """
        # Generate unique ticket number
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        ticket_number = f"{settings.TICKET_NUMBER_PREFIX}-{timestamp}"
        
        # Map AI priority to ticket priority
        priority_mapping = {
            "Low": TicketPriority.LOW,
            "Medium": TicketPriority.MEDIUM,
            "High": TicketPriority.HIGH,
            "Urgent": TicketPriority.URGENT,
            "Critical": TicketPriority.CRITICAL
        }
        
        priority = priority_mapping.get(classification.priority, TicketPriority.MEDIUM)
        
        # Set SLA based on priority
        sla_times = {
            TicketPriority.CRITICAL: {"response": 1, "resolution": 4},
            TicketPriority.URGENT: {"response": 2, "resolution": 8},
            TicketPriority.HIGH: {"response": 4, "resolution": 24},
            TicketPriority.MEDIUM: {"response": 8, "resolution": 48},
            TicketPriority.LOW: {"response": 24, "resolution": 72}
        }
        
        sla_config = sla_times[priority]
        now = datetime.utcnow()
        
        sla_info = SLAInfo(
            response_time_hours=sla_config["response"],
            resolution_time_hours=sla_config["resolution"]
        )
        
        # Generate title if not provided
        if not title:
            title = f"{classification.category} Issue" if len(user_query) > 100 else user_query[:100]
        
        # Create AI analysis object
        ai_analysis = AIAnalysis(
            classification_confidence=classification.confidence,
            predicted_category=self._map_external_category(classification.category.upper()),
            predicted_priority=priority,
            sentiment_score=classification.sentiment if hasattr(classification, 'sentiment') else 0.0,
            keywords=classification.suggested_keywords,
            similar_tickets=classification.similar_tickets if hasattr(classification, 'similar_tickets') else [],
            suggested_assignee=classification.suggested_assignee if hasattr(classification, 'suggested_assignee') else None
        )
        
        # Create ticket
        ticket = Ticket(
            ticket_number=ticket_number,
            title=title,
            description=user_query,
            requester_id=user_id,
            requester_email=user_email,
            requester_name=user_name,
            priority=priority,
            source=source,
            source_reference=source_reference,
            sla_info=sla_info,
            tags=classification.suggested_keywords,
            ai_analysis=ai_analysis
        )
        
        # Try to map category to enum
        try:
            if classification.category.upper() == "VPN":
                ticket.category = TicketCategory.VPN
            elif classification.category.upper() == "PASSWORD":
                ticket.category = TicketCategory.PASSWORD_RESET
            elif classification.category.upper() == "EMAIL":
                ticket.category = TicketCategory.EMAIL
            elif classification.category.upper() == "HARDWARE":
                ticket.category = TicketCategory.HARDWARE
            elif classification.category.upper() == "SOFTWARE":
                ticket.category = TicketCategory.SOFTWARE
            elif classification.category.upper() == "NETWORK":
                ticket.category = TicketCategory.NETWORK
            else:
                ticket.category = TicketCategory.OTHER
        except:
            ticket.category = TicketCategory.OTHER
        
        await ticket.insert()
        logger.info(f"Created ticket {ticket.ticket_number} with AI classification: {classification.category}")
        return ticket
    
    async def _create_basic_ticket(self, 
                                 user_query: str,
                                 user_id: Optional[str],
                                 user_email: str,
                                 user_name: str,
                                 source: TicketSource,
                                 source_reference: Optional[str] = None,
                                 title: Optional[str] = None) -> Ticket:
        """
        Create a basic ticket without AI classification (fallback)
        
        Args:
            user_query: The original query or description from the user
            user_id: ID of the requester
            user_email: Email of the requester
            user_name: Name of the requester
            source: Source system (GLPI, Solman, Chatbot, etc.)
            source_reference: External system reference ID (optional)
            title: Custom title (optional, will be generated if not provided)
            
        Returns:
            Created Ticket object
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        ticket_number = f"{settings.TICKET_NUMBER_PREFIX}-{timestamp}"
        
        sla_info = SLAInfo(
            response_time_hours=settings.DEFAULT_RESPONSE_TIME,
            resolution_time_hours=settings.DEFAULT_RESOLUTION_TIME
        )
        
        # Generate title if not provided
        if not title:
            title = user_query[:100] if len(user_query) > 100 else user_query
        
        ticket = Ticket(
            ticket_number=ticket_number,
            title=title,
            description=user_query,
            requester_id=user_id,
            requester_email=user_email,
            requester_name=user_name,
            priority=TicketPriority.MEDIUM,
            category=TicketCategory.OTHER,
            source=source,
            source_reference=source_reference,
            sla_info=sla_info
        )
        
        await ticket.insert()
        logger.info(f"Created basic ticket {ticket.ticket_number} from {source.value}")
        return ticket


    async def ingest_from_glpi(self, ticket_data: Dict[str, Any]) -> Ticket:
        """
        Ingest a ticket from GLPI system
        
        Args:
            ticket_data: Raw ticket data from GLPI API
            
        Returns:
            Processed Ticket object
        """
        try:
            logger.info(f"Ingesting ticket from GLPI: {ticket_data.get('id', 'unknown')}")            
            
            # Extract basic ticket information
            title = ticket_data.get('name', 'No Title')
            description = ticket_data.get('content', 'No Description')
            source_reference = str(ticket_data.get('id'))
            
            # Extract requester information
            requester_info = ticket_data.get('_users_id_recipient', {})
            requester_id = str(requester_info.get('id', 'unknown'))
            requester_email = requester_info.get('email', 'unknown@example.com')
            requester_name = requester_info.get('name', 'Unknown User')
            
            # Map GLPI priority to our system
            glpi_priority = int(ticket_data.get('priority', 3))
            priority_mapping = {
                1: TicketPriority.LOW,
                2: TicketPriority.LOW,
                3: TicketPriority.MEDIUM,
                4: TicketPriority.HIGH,
                5: TicketPriority.URGENT,
                6: TicketPriority.CRITICAL
            }
            priority = priority_mapping.get(glpi_priority, TicketPriority.MEDIUM)
            
            # Map GLPI category
            glpi_category = ticket_data.get('itilcategories_id', {})
            category_name = glpi_category.get('name', '').upper() if isinstance(glpi_category, dict) else ''
            
            # Map to our category system
            category = self._map_external_category(category_name)
            
            # Process with AI for enhanced classification
            classification = await gemini_service.classify_ticket(description)
            
            # Create the ticket
            ticket = await self._create_ticket_from_classification(
                description, 
                classification,
                requester_id,
                requester_email,
                requester_name,
                TicketSource.GLPI,
                source_reference=source_reference,
                title=title
            )
            
            # Add any attachments
            if 'documents' in ticket_data and isinstance(ticket_data['documents'], list):
                for doc in ticket_data['documents']:
                    attachment = Attachment(
                        filename=doc.get('filename', 'unknown'),
                        file_path=doc.get('filepath', ''),
                        file_size=doc.get('filesize', 0),
                        content_type=doc.get('mime', 'application/octet-stream')
                    )
                    ticket.attachments.append(attachment)
            
            await ticket.save()
            return ticket
            
        except Exception as e:
            logger.error(f"Error ingesting GLPI ticket: {str(e)}")
            # Create basic ticket as fallback
            return await self._create_basic_ticket(
                description if 'description' in locals() else "GLPI Ticket",
                requester_id if 'requester_id' in locals() else "unknown",
                requester_email if 'requester_email' in locals() else "unknown@example.com",
                requester_name if 'requester_name' in locals() else "Unknown User",
                TicketSource.GLPI,
                source_reference=source_reference if 'source_reference' in locals() else None
            )
    
    async def ingest_from_solman(self, ticket_data: Dict[str, Any]) -> Ticket:
        """
        Ingest a ticket from SAP Solution Manager
        
        Args:
            ticket_data: Raw ticket data from Solman API
            
        Returns:
            Processed Ticket object
        """
        try:
            logger.info(f"Ingesting ticket from Solman: {ticket_data.get('IncidentID', 'unknown')}")
            
            # Extract basic ticket information
            title = ticket_data.get('ShortText', 'No Title')
            description = ticket_data.get('Description', 'No Description')
            source_reference = ticket_data.get('IncidentID')
            
            # Extract requester information
            requester_id = ticket_data.get('ReporterID', 'unknown')
            requester_email = ticket_data.get('ReporterEmail', 'unknown@example.com')
            requester_name = ticket_data.get('ReporterName', 'Unknown User')
            
            # Map Solman priority to our system
            solman_priority = ticket_data.get('Priority', 'medium').lower()
            priority_mapping = {
                'very high': TicketPriority.CRITICAL,
                'high': TicketPriority.HIGH,
                'medium': TicketPriority.MEDIUM,
                'low': TicketPriority.LOW,
                'very low': TicketPriority.LOW
            }
            priority = priority_mapping.get(solman_priority, TicketPriority.MEDIUM)
            
            # Map Solman category
            solman_category = ticket_data.get('Category', '').upper()
            category = self._map_external_category(solman_category)
            
            # Process with AI for enhanced classification
            classification = await gemini_service.classify_ticket(description)
            
            # Create the ticket
            ticket = await self._create_ticket_from_classification(
                description, 
                classification,
                requester_id,
                requester_email,
                requester_name,
                TicketSource.SOLMAN,
                source_reference=source_reference,
                title=title
            )
            
            # Add any attachments
            if 'Attachments' in ticket_data and isinstance(ticket_data['Attachments'], list):
                for doc in ticket_data['Attachments']:
                    attachment = Attachment(
                        filename=doc.get('FileName', 'unknown'),
                        file_path=doc.get('FilePath', ''),
                        file_size=doc.get('FileSize', 0),
                        content_type=doc.get('ContentType', 'application/octet-stream')
                    )
                    ticket.attachments.append(attachment)
            
            await ticket.save()
            return ticket
            
        except Exception as e:
            logger.error(f"Error ingesting Solman ticket: {str(e)}")
            # Create basic ticket as fallback
            return await self._create_basic_ticket(
                description if 'description' in locals() else "Solman Ticket",
                requester_id if 'requester_id' in locals() else "unknown",
                requester_email if 'requester_email' in locals() else "unknown@example.com",
                requester_name if 'requester_name' in locals() else "Unknown User",
                TicketSource.SOLMAN,
                source_reference=source_reference if 'source_reference' in locals() else None
            )
    
    async def ingest_from_email(self, email_data: Dict[str, Any]) -> Ticket:
        """
        Ingest a ticket from email
        
        Args:
            email_data: Parsed email data
            
        Returns:
            Processed Ticket object
        """
        try:
            logger.info(f"Ingesting ticket from email: {email_data.get('subject', 'unknown')}")
            
            # Extract basic ticket information
            title = email_data.get('subject', 'No Subject')
            description = email_data.get('body', 'No Content')
            source_reference = email_data.get('message_id')
            
            # Extract requester information
            from_field = email_data.get('from', {})
            requester_email = from_field.get('email', 'unknown@example.com')
            requester_name = from_field.get('name', 'Unknown User')
            requester_id = requester_email  # Use email as ID for email-sourced tickets
            
            # Process with AI for enhanced classification
            classification = await gemini_service.classify_ticket(description)
            
            # Create the ticket
            ticket = await self._create_ticket_from_classification(
                description, 
                classification,
                requester_id,
                requester_email,
                requester_name,
                TicketSource.EMAIL,
                source_reference=source_reference,
                title=title
            )
            
            # Add any attachments
            if 'attachments' in email_data and isinstance(email_data['attachments'], list):
                for attachment_data in email_data['attachments']:
                    attachment = Attachment(
                        filename=attachment_data.get('filename', 'unknown'),
                        file_path=attachment_data.get('path', ''),
                        file_size=attachment_data.get('size', 0),
                        content_type=attachment_data.get('content_type', 'application/octet-stream')
                    )
                    ticket.attachments.append(attachment)
            
            await ticket.save()
            return ticket
            
        except Exception as e:
            logger.error(f"Error ingesting email ticket: {str(e)}")
            # Create basic ticket as fallback
            return await self._create_basic_ticket(
                description if 'description' in locals() else "Email Ticket",
                requester_id if 'requester_id' in locals() else "unknown",
                requester_email if 'requester_email' in locals() else "unknown@example.com",
                requester_name if 'requester_name' in locals() else "Unknown User",
                TicketSource.EMAIL,
                source_reference=source_reference if 'source_reference' in locals() else None
            )
    
    async def ingest_from_web_form(self, form_data: Dict[str, Any]) -> Ticket:
        """
        Ingest a ticket from web form submission
        
        Args:
            form_data: Web form submission data
            
        Returns:
            Processed Ticket object
        """
        try:
            logger.info(f"Ingesting ticket from web form: {form_data.get('title', 'unknown')}")
            
            # Extract basic ticket information
            title = form_data.get('title', 'No Title')
            description = form_data.get('description', 'No Description')
            
            # Extract requester information
            requester_id = form_data.get('user_id', 'unknown')
            requester_email = form_data.get('email', 'unknown@example.com')
            requester_name = form_data.get('name', 'Unknown User')
            
            # Extract additional metadata
            location = form_data.get('location')
            asset_tag = form_data.get('asset_tag')
            
            # Process with AI for enhanced classification
            classification = await gemini_service.classify_ticket(description)
            
            # Create the ticket
            ticket = await self._create_ticket_from_classification(
                description, 
                classification,
                requester_id,
                requester_email,
                requester_name,
                TicketSource.WEB_FORM,
                title=title
            )
            
            # Add additional metadata
            if location:
                ticket.location = location
            if asset_tag:
                ticket.asset_tag = asset_tag
            
            # Add any attachments
            if 'attachments' in form_data and isinstance(form_data['attachments'], list):
                for attachment_data in form_data['attachments']:
                    attachment = Attachment(
                        filename=attachment_data.get('filename', 'unknown'),
                        file_path=attachment_data.get('path', ''),
                        file_size=attachment_data.get('size', 0),
                        content_type=attachment_data.get('content_type', 'application/octet-stream')
                    )
                    ticket.attachments.append(attachment)
            
            await ticket.save()
            return ticket
            
        except Exception as e:
            logger.error(f"Error ingesting web form ticket: {str(e)}")
            # Create basic ticket as fallback
            return await self._create_basic_ticket(
                description if 'description' in locals() else "Web Form Ticket",
                requester_id if 'requester_id' in locals() else "unknown",
                requester_email if 'requester_email' in locals() else "unknown@example.com",
                requester_name if 'requester_name' in locals() else "Unknown User",
                TicketSource.WEB_FORM
            )
    
    async def ingest_ticket(self, source: TicketSource, data: Dict[str, Any]) -> Ticket:
        """
        Unified method to ingest tickets from any source
        
        Args:
            source: The source of the ticket
            data: Source-specific ticket data
            
        Returns:
            Processed Ticket object
        """
        if source in self.source_adapters:
            return await self.source_adapters[source](data)
        else:
            logger.error(f"Unsupported ticket source: {source}")
            raise ValueError(f"Unsupported ticket source: {source}")
    
    def _map_external_category(self, external_category: str) -> TicketCategory:
        """
        Map external system categories to our internal category system
        
        Args:
            external_category: Category string from external system
            
        Returns:
            Mapped TicketCategory
        """
        category_mapping = {
            "NETWORK": TicketCategory.NETWORK,
            "NETWORKING": TicketCategory.NETWORK,
            "CONNECTIVITY": TicketCategory.NETWORK,
            
            "HARDWARE": TicketCategory.HARDWARE,
            "EQUIPMENT": TicketCategory.HARDWARE,
            "DEVICE": TicketCategory.HARDWARE,
            
            "SOFTWARE": TicketCategory.SOFTWARE,
            "APPLICATION": TicketCategory.SOFTWARE,
            "PROGRAM": TicketCategory.SOFTWARE,
            
            "ACCESS": TicketCategory.ACCESS_CONTROL,
            "PERMISSION": TicketCategory.ACCESS_CONTROL,
            "AUTHORIZATION": TicketCategory.ACCESS_CONTROL,
            
            "EMAIL": TicketCategory.EMAIL,
            "MAIL": TicketCategory.EMAIL,
            
            "VPN": TicketCategory.VPN,
            "REMOTE ACCESS": TicketCategory.VPN,
            
            "PRINTER": TicketCategory.PRINTER,
            "PRINTING": TicketCategory.PRINTER,
            
            "PASSWORD": TicketCategory.PASSWORD_RESET,
            "RESET PASSWORD": TicketCategory.PASSWORD_RESET,
            
            "ACCOUNT": TicketCategory.ACCOUNT_MANAGEMENT,
            "USER ACCOUNT": TicketCategory.ACCOUNT_MANAGEMENT,
        }
        
        # Try to find a match in our mapping
        for key, value in category_mapping.items():
            if key in external_category:
                return value
        
        # Default to OTHER if no match found
        return TicketCategory.OTHER


# Global instance
ingestion_service = TicketIngestionService()
