import axios from 'axios';
import io from 'socket.io-client';

const API_BASE_URL = 'http://localhost:8000/api/v1';
const SOCKET_URL = 'http://localhost:8000';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Socket.IO instance
let socket = null;

export const connectSocket = () => {
  if (!socket) {
    socket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'],
    });
  }
  return socket;
};

export const disconnectSocket = () => {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
};

// Chatbot API calls
export const classifyMessage = async (message, userInfo) => {
  try {
    const response = await apiClient.post('/chatbot/classify', {
      message,
      user_id: userInfo.user_id || 'user_123',
      user_name: userInfo.user_name || 'John Doe',
      user_email: userInfo.user_email || 'user@example.com',
      context: userInfo.context || {}
    });
    return response.data;
  } catch (error) {
    console.error('Error classifying message:', error);
    throw error;
  }
};

export const getTicket = async (ticketId) => {
  try {
    const response = await apiClient.get(`/chatbot/tickets/${ticketId}`);
    return response.data;
  } catch (error) {
    console.error('Error getting ticket:', error);
    throw error;
  }
};

export const sendMessage = async (ticketId, message, senderInfo) => {
  try {
    const response = await apiClient.post(`/chatbot/tickets/${ticketId}/message`, {
      message,
      sender_id: senderInfo.sender_id || 'user_123',
      sender_name: senderInfo.sender_name || 'John Doe',
      sender_type: senderInfo.sender_type || 'user'
    });
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

export const getTicketsByCategory = async (category, status) => {
  try {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (status) params.append('status', status);
    
    const response = await apiClient.get(`/chatbot/tickets?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Error getting tickets by category:', error);
    throw error;
  }
};

export const getCategories = async () => {
  try {
    const response = await apiClient.get('/chatbot/categories');
    return response.data;
  } catch (error) {
    console.error('Error getting categories:', error);
    throw error;
  }
};

// Dashboard API calls
export const getDashboardData = async (userEmail) => {
  try {
    console.log('Making API call to /dashboard/ with user email:', userEmail);
    const response = await apiClient.get('/dashboard/', {
      params: { user_email: userEmail }
    });
    console.log('Dashboard API response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error getting dashboard data:', error);
    console.error('Error details:', error.response?.data || error.message);
    throw error;
  }
};

export const getDashboardStats = async (userEmail) => {
  try {
    const response = await apiClient.get('/dashboard/stats', {
      params: { user_email: userEmail }
    });
    return response.data;
  } catch (error) {
    console.error('Error getting dashboard stats:', error);
    throw error;
  }
};

export const resolveTicket = async (ticketId, userEmail) => {
  try {
    const response = await apiClient.post(`/dashboard/resolve-ticket/${ticketId}`, null, {
      params: { user_email: userEmail }
    });
    return response.data;
  } catch (error) {
    console.error('Error resolving ticket:', error);
    throw error;
  }
};

// Socket.IO event handlers
export const socketEvents = {
  joinTicket: (ticketId, userId) => {
    if (socket) {
      socket.emit('join_ticket', { ticket_id: ticketId, user_id: userId });
    }
  },
  
  leaveTicket: (ticketId, userId) => {
    if (socket) {
      socket.emit('leave_ticket', { ticket_id: ticketId, user_id: userId });
    }
  },
  
  sendMessage: (ticketId, message, senderInfo) => {
    if (socket) {
      socket.emit('send_message', {
        ticket_id: ticketId,
        message,
        sender_id: senderInfo.sender_id || 'user_123',
        sender_name: senderInfo.sender_name || 'John Doe',
        sender_type: senderInfo.sender_type || 'user'
      });
    }
  },
  
  markMessageRead: (messageId, ticketId) => {
    if (socket) {
      socket.emit('mark_message_read', {
        message_id: messageId,
        ticket_id: ticketId
      });
    }
  },
  
  typing: (ticketId, userId, userName, isTyping) => {
    if (socket) {
      socket.emit('typing', {
        ticket_id: ticketId,
        user_id: userId,
        user_name: userName,
        is_typing: isTyping
      });
    }
  },
  
  onNewMessage: (callback) => {
    if (socket) {
      socket.on('new_message', callback);
    }
  },
  
  onMessageRead: (callback) => {
    if (socket) {
      socket.on('message_read', callback);
    }
  },
  
  onUserTyping: (callback) => {
    if (socket) {
      socket.on('user_typing', callback);
    }
  },
  
  onTicketUpdated: (callback) => {
    if (socket) {
      socket.on('ticket_updated', callback);
    }
  },
  
  onJoinedTicket: (callback) => {
    if (socket) {
      socket.on('joined_ticket', callback);
    }
  },
  
  onError: (callback) => {
    if (socket) {
      socket.on('error', callback);
    }
  },
  
  removeAllListeners: () => {
    if (socket) {
      socket.removeAllListeners();
    }
  }
};

// Export the API service functions
export const apiService = {
  classifyMessage,
  getTicket,
  sendMessage,
  getTicketsByCategory,
  getCategories,
  getDashboardData,
  getDashboardStats,
  resolveTicket,
  connectSocket,
  disconnectSocket
};

export default apiClient;
