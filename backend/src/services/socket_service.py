import socketio
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:5174", 
        "http://127.0.0.1:5174",
        "http://localhost:5175", 
        "http://127.0.0.1:5175"
    ],
    logger=True,
    engineio_logger=True
)

# Create Socket.IO app
socket_app = socketio.ASGIApp(sio)

# Store active connections by user_id
active_connections: Dict[str, str] = {}
# Store room memberships (ticket_id -> set of user_ids)
ticket_rooms: Dict[str, set] = {}


@sio.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    logger.info(f"Client connected: {sid}")
    return True


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {sid}")
    
    # Remove from active connections
    user_id = None
    for uid, connection_id in active_connections.items():
        if connection_id == sid:
            user_id = uid
            break
    
    if user_id:
        del active_connections[user_id]
        # Remove from all ticket rooms
        for ticket_id, members in ticket_rooms.items():
            members.discard(user_id)
            if not members:
                del ticket_rooms[ticket_id]


@sio.event
async def join_ticket(sid, data):
    """Join a ticket room for real-time chat"""
    try:
        ticket_id = data.get('ticket_id')
        user_id = data.get('user_id')
        
        if not ticket_id or not user_id:
            await sio.emit('error', {'message': 'Missing ticket_id or user_id'}, room=sid)
            return
        
        # Store connection
        active_connections[user_id] = sid
        
        # Join ticket room
        await sio.enter_room(sid, f"ticket_{ticket_id}")
        
        # Track room membership
        if ticket_id not in ticket_rooms:
            ticket_rooms[ticket_id] = set()
        ticket_rooms[ticket_id].add(user_id)
        
        logger.info(f"User {user_id} joined ticket {ticket_id}")
        await sio.emit('joined_ticket', {
            'ticket_id': ticket_id,
            'message': f'Joined ticket {ticket_id}'
        }, room=sid)
        
    except Exception as e:
        logger.error(f"Error joining ticket: {str(e)}")
        await sio.emit('error', {'message': 'Failed to join ticket'}, room=sid)


@sio.event
async def leave_ticket(sid, data):
    """Leave a ticket room"""
    try:
        ticket_id = data.get('ticket_id')
        user_id = data.get('user_id')
        
        if ticket_id:
            await sio.leave_room(sid, f"ticket_{ticket_id}")
            
            # Remove from room membership
            if ticket_id in ticket_rooms:
                ticket_rooms[ticket_id].discard(user_id)
                if not ticket_rooms[ticket_id]:
                    del ticket_rooms[ticket_id]
        
        logger.info(f"User {user_id} left ticket {ticket_id}")
        
    except Exception as e:
        logger.error(f"Error leaving ticket: {str(e)}")


@sio.event
async def send_message(sid, data):
    """Handle sending a message in a ticket"""
    try:
        ticket_id = data.get('ticket_id')
        message = data.get('message')
        sender_id = data.get('sender_id')
        sender_name = data.get('sender_name')
        sender_type = data.get('sender_type', 'user')
        
        if not all([ticket_id, message, sender_id, sender_name]):
            await sio.emit('error', {'message': 'Missing required fields'}, room=sid)
            return
        
        # Create message object
        message_data = {
            'message_id': f"msg_{datetime.utcnow().timestamp()}",
            'ticket_id': ticket_id,
            'sender_id': sender_id,
            'sender_name': sender_name,
            'sender_type': sender_type,
            'content': message,
            'timestamp': datetime.utcnow().isoformat(),
            'is_read': False
        }
        
        # Broadcast to all users in the ticket room
        await sio.emit('new_message', message_data, room=f"ticket_{ticket_id}")
        
        logger.info(f"Message sent in ticket {ticket_id} by {sender_name}")
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        await sio.emit('error', {'message': 'Failed to send message'}, room=sid)


@sio.event
async def mark_message_read(sid, data):
    """Mark a message as read"""
    try:
        message_id = data.get('message_id')
        ticket_id = data.get('ticket_id')
        
        if not message_id or not ticket_id:
            await sio.emit('error', {'message': 'Missing message_id or ticket_id'}, room=sid)
            return
        
        # Broadcast read status to all users in the ticket room
        await sio.emit('message_read', {
            'message_id': message_id,
            'ticket_id': ticket_id,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f"ticket_{ticket_id}")
        
    except Exception as e:
        logger.error(f"Error marking message as read: {str(e)}")
        await sio.emit('error', {'message': 'Failed to mark message as read'}, room=sid)


@sio.event
async def typing(sid, data):
    """Handle typing indicator"""
    try:
        ticket_id = data.get('ticket_id')
        user_id = data.get('user_id')
        user_name = data.get('user_name')
        is_typing = data.get('is_typing', False)
        
        if not all([ticket_id, user_id, user_name]):
            return
        
        # Broadcast typing status to other users in the ticket room
        await sio.emit('user_typing', {
            'ticket_id': ticket_id,
            'user_id': user_id,
            'user_name': user_name,
            'is_typing': is_typing,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f"ticket_{ticket_id}", skip_sid=sid)
        
    except Exception as e:
        logger.error(f"Error handling typing indicator: {str(e)}")


async def broadcast_ticket_update(ticket_id: str, update_data: Dict[str, Any]):
    """Broadcast ticket updates to all users in the ticket room"""
    try:
        await sio.emit('ticket_updated', {
            'ticket_id': ticket_id,
            'update': update_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f"ticket_{ticket_id}")
        
    except Exception as e:
        logger.error(f"Error broadcasting ticket update: {str(e)}")


async def broadcast_new_ticket(ticket_data: Dict[str, Any]):
    """Broadcast new ticket to relevant users"""
    try:
        category = ticket_data.get('category')
        
        # Broadcast to users monitoring this category
        await sio.emit('new_ticket', {
            'ticket': ticket_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f"category_{category}")
        
    except Exception as e:
        logger.error(f"Error broadcasting new ticket: {str(e)}")


# Export the socket app for use in main.py
__all__ = ['socket_app', 'sio', 'broadcast_ticket_update', 'broadcast_new_ticket']
