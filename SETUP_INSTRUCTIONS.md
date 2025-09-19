# POWERGRID AI Ticketing System - Setup Instructions

## Overview
This is a comprehensive AI-powered ticketing system with three main classification categories and real-time chat functionality using Socket.IO.

## Features
- **AI Classification**: Uses Google Gemini API to classify queries into three categories
- **Three Main Categories**:
  1. **Hardware & Infrastructure**: Physical devices, servers, network equipment, power issues
  2. **Software & Digital Services**: Applications, programs, online services, email, VPN
  3. **Access & Security**: User accounts, permissions, passwords, security settings
- **Real-time Chat**: Socket.IO for live communication between users and support agents
- **MongoDB Integration**: Stores tickets with unique IDs and chat messages
- **Modern UI**: React frontend with Material-UI components

## Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB Atlas account (or local MongoDB)
- Google Gemini API key

## Backend Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file in the backend directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
MONGODB_URL=mongodb+srv://sumitrathod22724:sumit123@cluster0.1bhqcmt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DB_NAME=powergrid_tickets
```

### 3. Test the Setup
```bash
python test_setup.py
```

### 4. Start the Backend Server
```bash
python -m src.main
```

The backend will be available at `http://localhost:8000`

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start the Development Server
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Chatbot Endpoints
- `POST /api/v1/chatbot/classify` - Classify a user query and create a ticket
- `GET /api/v1/chatbot/tickets/{ticket_id}` - Get ticket details with chat messages
- `POST /api/v1/chatbot/tickets/{ticket_id}/message` - Send a message to a ticket
- `GET /api/v1/chatbot/tickets` - Get tickets filtered by category and status
- `GET /api/v1/chatbot/categories` - Get available ticket categories

### Socket.IO Events
- `join_ticket` - Join a ticket room for real-time chat
- `leave_ticket` - Leave a ticket room
- `send_message` - Send a message in a ticket
- `mark_message_read` - Mark a message as read
- `typing` - Send typing indicator

## Usage Flow

1. **User submits query** in the main dashboard chat
2. **AI classifies** the query using Gemini API into one of three categories
3. **User is redirected** to the appropriate category tab
4. **Ticket is created** with unique ID and stored in MongoDB
5. **Real-time chat** begins between user and support agent
6. **Support agent** can manually provide solutions and resolve issues

## Project Structure

```
backend/
├── src/
│   ├── ai/
│   │   └── gemini_service.py          # AI classification service
│   ├── api/
│   │   └── chatbot.py                 # Chatbot API endpoints
│   ├── models/
│   │   └── ticket.py                  # Ticket and chat message models
│   ├── services/
│   │   └── socket_service.py          # Socket.IO real-time communication
│   └── main.py                        # FastAPI application
├── requirements.txt
└── test_setup.py                      # Setup verification script

frontend/
├── src/
│   ├── components/
│   │   └── ChatInterface.jsx          # Reusable chat component
│   ├── pages/
│   │   ├── ClassificationOne.jsx      # Hardware & Infrastructure tab
│   │   ├── ClassificationTwo.jsx      # Software & Digital Services tab
│   │   └── ClassificationThree.jsx    # Access & Security tab
│   ├── services/
│   │   └── apiService.js              # API communication and Socket.IO
│   └── App.jsx                        # Main application component
└── package.json
```

## Configuration

### Gemini API Setup
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

### MongoDB Setup
The system is configured to use the provided MongoDB Atlas cluster. The connection string is already set in the configuration.

## Testing

### Backend Tests
```bash
cd backend
python test_setup.py
```

### Frontend Tests
1. Open `http://localhost:3000`
2. Type a query in the AI chat (e.g., "My laptop won't turn on")
3. The system should classify it and redirect to the appropriate tab
4. You can then chat with the AI assistant in real-time

## Troubleshooting

### Common Issues

1. **Gemini API Error**: Make sure your API key is correctly set in the `.env` file
2. **MongoDB Connection Error**: Check your internet connection and MongoDB Atlas credentials
3. **Socket.IO Connection Issues**: Ensure both frontend and backend are running on the correct ports
4. **Frontend Build Errors**: Run `npm install` to ensure all dependencies are installed

### Logs
- Backend logs are displayed in the terminal where you run `python -m src.main`
- Frontend logs are displayed in the browser console and terminal

## Features in Detail

### AI Classification
- Uses Google Gemini 1.5 Flash model
- Classifies queries into three main categories
- Provides confidence scores and reasoning
- Suggests solutions and assigns priorities

### Real-time Communication
- Socket.IO for instant messaging
- Typing indicators
- Message read receipts
- Room-based communication per ticket

### Ticket Management
- Unique ticket IDs with timestamp and random suffix
- Status tracking (open, in-progress, resolved, closed)
- Priority levels (low, medium, high, urgent, critical)
- Full chat history storage

### User Interface
- Modern Material-UI design
- Responsive layout
- Real-time updates
- Intuitive navigation between categories

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the logs for error messages
3. Ensure all dependencies are properly installed
4. Verify your API keys and database connections

## License

This project is part of the POWERGRID AI Ticketing System for SIH 2025.
