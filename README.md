# POWERGRID AI-Based Ticketing System

## Overview

A centralized AI-based ticketing system that consolidates multiple platforms (GLPI, Solman, email) into a single intelligent platform for POWERGRID's IT operations.

## Key Features

- **Unified Ingestion**: Collect tickets from all sources (chatbot, email, GLPI, Solman, web form, etc.)
- **Automated Classification**: NLP-powered ticket categorization
- **Intelligent Routing**: AI-driven team assignment based on urgency and context
- **Self-Service Resolution**: Chatbot for common issues (password reset, VPN access)
- **Knowledge Base**: Smart article suggestions and creation
- **Alerts & Notifications**: Email and SMS notifications for important updates
- **Multi-Source Support**: Seamless integration with multiple ticket sources
- **Email Polling**: Automatic conversion of emails to tickets

## Architecture

```
├── backend/                 # Python FastAPI backend
│   ├── src/
│   │   ├── api/            # REST API endpoints
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── ai/            # NLP and ML components
│   │   ├── integrations/  # External system connectors
│   │   └── utils/         # Helper functions
├── frontend/               # React.js frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Application pages
│   │   ├── services/      # API clients
│   │   └── utils/         # Helper functions
├── database/              # Database schemas and migrations
├── docs/                  # Documentation
├── tests/                 # Test suites
├── config/               # Configuration files
└── scripts/              # Deployment and utility scripts
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI/ML**: spaCy, Transformers, scikit-learn
- **Task Queue**: Celery with Redis
- **Authentication**: JWT with OAuth2

### Frontend
- **Framework**: React.js with TypeScript
- **State Management**: Redux Toolkit
- **UI Library**: Material-UI (MUI)
- **HTTP Client**: Axios

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Message Queue**: Redis
- **Email**: SMTP integration
- **SMS**: Twilio integration

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Redis 6+

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd powergrid-ai-ticketing
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Database Setup**
   ```bash
   # Configure PostgreSQL connection in config/database.yaml
   # Run migrations
   cd backend
   alembic upgrade head
   ```

5. **Start Services**
   ```bash
   # Start backend
   cd backend && uvicorn src.main:app --reload

   # Start frontend
   cd frontend && npm start

   # Start Redis (for background tasks)
   redis-server

   # Start Celery worker
   cd backend && celery -A src.worker worker --loglevel=info
   ```

## Development

### API Documentation
Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

### Environment Variables
Copy `.env.example` to `.env` and configure your environment variables:
```
DATABASE_URL=postgresql://user:password@localhost/powergrid_tickets
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-secret-key
SMTP_SERVER=smtp.company.com
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary to POWERGRID.

## Support

For support, email support@powergrid.in or contact the development team.
