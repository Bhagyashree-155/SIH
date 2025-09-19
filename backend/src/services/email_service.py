import imaplib
import email
import asyncio
import logging
from datetime import datetime, timedelta
from email.header import decode_header
from typing import Dict, List, Any, Optional

from src.core.config import settings
from src.services.ingestion_service import ingestion_service
from src.models.ticket import TicketSource

logger = logging.getLogger(__name__)

class EmailPollingService:
    """
    Service for polling email servers and converting emails to tickets
    """
    def __init__(self):
        self.polling_interval = settings.EMAIL_POLLING_INTERVAL
        self.credentials = settings.EMAIL_CREDENTIALS
        self.last_check_time = datetime.utcnow() - timedelta(hours=24)  # Start with last 24 hours
        self.running = False
        self.polling_task = None
    
    async def start_polling(self):
        """
        Start the email polling service
        """
        if self.running:
            logger.warning("Email polling service is already running")
            return
        
        self.running = True
        self.polling_task = asyncio.create_task(self._polling_loop())
        logger.info("Email polling service started")
    
    async def stop_polling(self):
        """
        Stop the email polling service
        """
        if not self.running:
            logger.warning("Email polling service is not running")
            return
        
        self.running = False
        if self.polling_task:
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass
        logger.info("Email polling service stopped")
    
    async def _polling_loop(self):
        """
        Main polling loop that runs at regular intervals
        """
        while self.running:
            try:
                await self._check_emails()
                self.last_check_time = datetime.utcnow()
            except Exception as e:
                logger.error(f"Error checking emails: {str(e)}")
            
            # Wait for the next polling interval
            await asyncio.sleep(self.polling_interval)
    
    async def _check_emails(self):
        """
        Check for new emails and process them into tickets
        """
        if not self.credentials:
            logger.warning("No email credentials configured, skipping email check")
            return
        
        for account in self.credentials:
            try:
                # Connect to the IMAP server
                mail = imaplib.IMAP4_SSL(account["imap_server"])
                mail.login(account["username"], account["password"])
                mail.select("INBOX")
                
                # Search for emails newer than last check
                since_date = self.last_check_time.strftime("%d-%b-%Y")
                status, messages = mail.search(None, f'(SINCE "{since_date}")')
                
                if status != "OK":
                    logger.error(f"Error searching for emails: {status}")
                    continue
                
                # Process each email
                for message_id in messages[0].split():
                    status, msg_data = mail.fetch(message_id, "(RFC822)")
                    
                    if status != "OK":
                        logger.error(f"Error fetching email {message_id}: {status}")
                        continue
                    
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    
                    # Extract email data
                    email_data = self._parse_email(email_message)
                    
                    # Create ticket from email
                    await ingestion_service.ingest_from_email(email_data)
                    
                    # Mark as read
                    mail.store(message_id, "+FLAGS", "\\Seen")
                
                mail.close()
                mail.logout()
            
            except Exception as e:
                logger.error(f"Error processing emails from {account['username']}: {str(e)}")
    
    def _parse_email(self, email_message) -> Dict[str, Any]:
        """
        Parse an email message into a format suitable for ticket creation
        
        Args:
            email_message: The email message object to parse
            
        Returns:
            Dict containing parsed email data
        """
        # Get subject
        subject = ""
        if email_message["subject"]:
            subject_parts = decode_header(email_message["subject"])
            subject = ""
            for part, encoding in subject_parts:
                if isinstance(part, bytes):
                    part = part.decode(encoding or "utf-8", errors="replace")
                subject += part
        
        # Get sender
        from_parts = decode_header(email_message["from"])
        sender = ""
        for part, encoding in from_parts:
            if isinstance(part, bytes):
                part = part.decode(encoding or "utf-8", errors="replace")
            sender += part
        
        # Extract email address
        email_address = ""
        if "<" in sender and ">" in sender:
            email_address = sender.split("<")[1].split(">")[0]
        else:
            email_address = sender.strip()
        
        # Get sender name
        sender_name = ""
        if "<" in sender:
            sender_name = sender.split("<")[0].strip()
        else:
            sender_name = email_address.split("@")[0]
        
        # Get body
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                # Get text content
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or "utf-8"
                    body = payload.decode(charset, errors="replace")
                    break
        else:
            payload = email_message.get_payload(decode=True)
            charset = email_message.get_content_charset() or "utf-8"
            body = payload.decode(charset, errors="replace")
        
        # Get attachments
        attachments = []
        if email_message.is_multipart():
            for part in email_message.walk():
                content_disposition = str(part.get("Content-Disposition"))
                
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        # Decode filename if needed
                        filename_parts = decode_header(filename)
                        filename = ""
                        for part_name, encoding in filename_parts:
                            if isinstance(part_name, bytes):
                                part_name = part_name.decode(encoding or "utf-8", errors="replace")
                            filename += part_name
                        
                        # Get attachment content
                        payload = part.get_payload(decode=True)
                        
                        attachments.append({
                            "filename": filename,
                            "content": payload,
                            "content_type": part.get_content_type()
                        })
        
        # Create email data dictionary
        email_data = {
            "title": subject,
            "description": body,
            "email": email_address,
            "name": sender_name,
            "source_reference": email_message["message-id"] or "",
            "received_at": email_message["date"],
            "attachments": attachments
        }
        
        return email_data

# Create a singleton instance
email_service = EmailPollingService()