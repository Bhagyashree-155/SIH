# Multi-Source Ticket Ingestion System

## Overview

The Multi-Source Ticket Ingestion System is a core component of the POWERGRID AI Ticketing System that enables seamless collection and processing of tickets from various sources. This unified approach ensures consistent ticket handling regardless of origin, while preserving source-specific metadata.

## Supported Ticket Sources

- **GLPI**: Integration with POWERGRID's existing GLPI ticketing system
- **SAP Solution Manager (Solman)**: Integration with SAP's Solution Manager
- **Email**: Automatic conversion of emails to tickets via IMAP polling
- **Web Form**: User-friendly web interface for ticket submission
- **Chatbot**: Conversational interface for ticket creation

## Architecture

The system follows a modular architecture with these key components:

1. **Source Adapters**: Source-specific modules that handle the unique aspects of each ticket source
2. **Unified Ingestion Pipeline**: Common processing pipeline for all tickets
3. **Email Polling Service**: Background service that checks for new emails and converts them to tickets
4. **API Endpoints**: REST API endpoints for external systems to submit tickets

## Implementation Details

### Ingestion Service

The `TicketIngestionService` class in `ingestion_service.py` is the central component that:

- Provides source-specific ingestion methods (`ingest_from_glpi`, `ingest_from_solman`, etc.)
- Maps external categories to internal ticket categories
- Implements a unified `ingest_ticket` method for consistent processing
- Handles AI classification and auto-resolution checks
- Creates standardized ticket records in the database

### Email Polling Service

The `EmailPollingService` class in `email_service.py`:

- Polls configured email accounts at regular intervals
- Parses emails into a structured format suitable for ticket creation
- Extracts attachments and metadata
- Submits parsed emails to the ingestion service

### API Endpoints

The system provides several REST API endpoints in `tickets.py`:

- `/api/tickets/web-form`: For web form submissions
- `/api/tickets/web-form/with-attachments`: For web form submissions with file attachments
- `/api/tickets/glpi`: For GLPI ticket ingestion
- `/api/tickets/solman`: For Solman ticket ingestion
- `/api/tickets/email`: For manual email ticket ingestion
- `/api/tickets/unified`: Unified endpoint for all sources

## Configuration

The system is configured through settings in `config.py`:

- `EMAIL_POLLING_INTERVAL`: Frequency of email checks (in seconds)
- `EMAIL_CREDENTIALS`: List of email accounts to poll
- `INTEGRATION_API_KEY`: API key for external system authentication
- `UPLOAD_DIR`: Directory for storing attachments

## Usage Examples

### Ingesting a Ticket from GLPI

```python
# Example of how the system processes a GLPI ticket
await ingestion_service.ingest_from_glpi({
    "id": "12345",
    "title": "Network connectivity issue",
    "description": "Unable to connect to the network",
    "requester_email": "user@powergrid.in",
    "requester_name": "John Doe",
    "category": "Network",
    "priority": "High"
})
```

### Submitting a Ticket via API

```bash
# Example API call to submit a ticket from an external system
curl -X POST http://localhost:8000/api/tickets/unified \
  -H "Content-Type: application/json" \
  -d '{
    "source": "GLPI",
    "data": {
      "title": "Software installation request",
      "description": "Need Microsoft Office installed",
      "requester_email": "user@powergrid.in",
      "requester_name": "Jane Smith",
      "priority": "Medium"
    },
    "api_key": "your-integration-api-key"
  }'
```

## Benefits

1. **Centralized Management**: All tickets are processed through a single system
2. **Consistent Experience**: Users receive the same level of service regardless of how they submit tickets
3. **Preserved Context**: Source-specific information is maintained for reference
4. **Unified Analytics**: Comprehensive reporting across all ticket sources
5. **Flexible Integration**: Easy to add new ticket sources in the future

## Future Enhancements

- **SMS Ticket Creation**: Allow ticket creation via SMS messages
- **Mobile App Integration**: Support for mobile app ticket submission
- **Social Media Monitoring**: Convert social media mentions into tickets
- **Voice Recognition**: Create tickets from voice recordings or calls