import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Typography,
  Paper,
  Avatar,
  Chip,
  InputAdornment,
  CircularProgress,
  Alert,
  Divider
} from '@mui/material';
import {
  Send as SendIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
  CheckCircle as ReadIcon
} from '@mui/icons-material';
import { apiService, socketEvents } from '../services/apiService';

const ChatInterface = ({ ticketId, category, onTicketUpdate }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [typingUsers, setTypingUsers] = useState([]);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  // Sender info (in dashboards this is a technician/agent)
  const senderInfo = {
    sender_id: 'agent_123',
    sender_name: 'Technician',
    sender_type: 'agent'
  };

  useEffect(() => {
    if (ticketId) {
      loadTicketMessages();
      const cleanup = connectToSocket();
      
      return cleanup;
    }
  }, [ticketId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadTicketMessages = async () => {
    try {
      setIsLoading(true);
      const ticketData = await apiService.getTicket(ticketId);
      setMessages(ticketData.chat_messages || []);
    } catch (error) {
      setError('Failed to load messages');
      console.error('Error loading messages:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const connectToSocket = () => {
    // Temporarily disable Socket.IO to avoid connection errors
    // TODO: Fix Socket.IO connection issues
    console.log('Socket.IO connection disabled for now');
    
    // For now, we'll use polling to get new messages
    const pollInterval = setInterval(() => {
      loadTicketMessages();
    }, 5000); // Poll every 5 seconds
    
    return () => clearInterval(pollInterval);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;

    const messageText = newMessage.trim();
    setNewMessage('');
    setIsLoading(true);

    try {
      // Send message via API
      await apiService.sendMessage(ticketId, messageText, senderInfo);
      
      // Clear typing indicator
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      socketEvents.typing(ticketId, senderInfo.sender_id, senderInfo.sender_name, false);
      
    } catch (error) {
      setError('Failed to send message');
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTyping = (e) => {
    const value = e.target.value;
    setNewMessage(value);

    // Send typing indicator
    socketEvents.typing(ticketId, senderInfo.sender_id, senderInfo.sender_name, true);

    // Clear previous timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Set timeout to stop typing indicator
    typingTimeoutRef.current = setTimeout(() => {
      socketEvents.typing(ticketId, senderInfo.sender_id, senderInfo.sender_name, false);
    }, 1000);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'Hardware & Infrastructure':
        return '#3b82f6';
      case 'Software & Digital Services':
        return '#10b981';
      case 'Access & Security':
        return '#f59e0b';
      default:
        return '#6b7280';
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Chat Header */}
      <Paper 
        elevation={1} 
        sx={{ 
          p: 2, 
          borderRadius: '12px 12px 0 0',
          background: `linear-gradient(135deg, ${getCategoryColor(category)}20 0%, ${getCategoryColor(category)}10 100%)`,
          borderBottom: `2px solid ${getCategoryColor(category)}40`
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar sx={{ bgcolor: getCategoryColor(category) }}>
            <BotIcon />
          </Avatar>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600, color: '#1e293b' }}>
              {category} Support
            </Typography>
            <Typography variant="body2" sx={{ color: '#64748b' }}>
              AI-powered assistance for your technical issues
            </Typography>
          </Box>
          <Chip 
            label="Online" 
            size="small" 
            sx={{ 
              bgcolor: '#10b981', 
              color: 'white',
              fontWeight: 600
            }} 
          />
        </Box>
      </Paper>

      {/* Messages Area */}
      <Box 
        sx={{ 
          flex: 1, 
          overflowY: 'auto', 
          p: 2, 
          bgcolor: '#f8fafc',
          '&::-webkit-scrollbar': {
            width: '6px',
          },
          '&::-webkit-scrollbar-track': {
            background: '#f1f5f9',
          },
          '&::-webkit-scrollbar-thumb': {
            background: '#cbd5e1',
            borderRadius: '3px',
          },
        }}
      >
        {isLoading && messages.length === 0 && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {messages.map((message, index) => (
          <Box key={message.message_id || index} sx={{ mb: 2 }}>
            <Box
              sx={{
                display: 'flex',
                justifyContent: message.sender_type === 'user' ? 'flex-end' : 'flex-start',
                alignItems: 'flex-start',
                gap: 1
              }}
            >
              {message.sender_type !== 'user' && (
                <Avatar sx={{ width: 32, height: 32, bgcolor: getCategoryColor(category) }}>
                  <BotIcon sx={{ fontSize: 16 }} />
                </Avatar>
              )}
              
              <Box
                sx={{
                  maxWidth: '70%',
                  bgcolor: message.sender_type === 'user' ? getCategoryColor(category) : 'white',
                  color: message.sender_type === 'user' ? 'white' : '#1e293b',
                  p: 2,
                  borderRadius: message.sender_type === 'user' 
                    ? '12px 12px 4px 12px' 
                    : '12px 12px 12px 4px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  position: 'relative'
                }}
              >
                <Typography variant="body2" sx={{ lineHeight: 1.5 }}>
                  {message.content}
                </Typography>
                
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                  <Typography variant="caption" sx={{ opacity: 0.7 }}>
                    {message.sender_name}
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.7 }}>
                    •
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.7 }}>
                    {formatTime(message.timestamp)}
                  </Typography>
                  {message.is_read && (
                    <ReadIcon sx={{ fontSize: 12, opacity: 0.7 }} />
                  )}
                </Box>
              </Box>

              {message.sender_type === 'user' && (
                <Avatar sx={{ width: 32, height: 32, bgcolor: '#3b82f6' }}>
                  <PersonIcon sx={{ fontSize: 16 }} />
                </Avatar>
              )}
            </Box>
          </Box>
        ))}

        {/* Typing Indicator */}
        {typingUsers.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 5 }}>
              <Avatar sx={{ width: 24, height: 24, bgcolor: getCategoryColor(category) }}>
                <BotIcon sx={{ fontSize: 12 }} />
              </Avatar>
              <Box sx={{ bgcolor: 'white', p: 1.5, borderRadius: '12px 12px 12px 4px' }}>
                <Typography variant="body2" sx={{ color: '#64748b', fontStyle: 'italic' }}>
                  {typingUsers.map(u => u.user_name).join(', ')} {typingUsers.length === 1 ? 'is' : 'are'} typing...
                </Typography>
              </Box>
            </Box>
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Box>

      {/* Message Input */}
      <Paper elevation={1} sx={{ p: 2, borderRadius: '0 0 12px 12px' }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          placeholder="Type your message here..."
          value={newMessage}
          onChange={handleTyping}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={handleSendMessage}
                  disabled={!newMessage.trim() || isLoading}
                  sx={{
                    bgcolor: getCategoryColor(category),
                    color: 'white',
                    '&:hover': {
                      bgcolor: getCategoryColor(category),
                      opacity: 0.9
                    },
                    '&:disabled': {
                      bgcolor: '#e5e7eb',
                      color: '#9ca3af'
                    }
                  }}
                >
                  {isLoading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
                </IconButton>
              </InputAdornment>
            )
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: '12px',
              '& fieldset': {
                borderColor: '#e5e7eb'
              },
              '&:hover fieldset': {
                borderColor: getCategoryColor(category)
              },
              '&.Mui-focused fieldset': {
                borderColor: getCategoryColor(category)
              }
            }
          }}
        />
      </Paper>
    </Box>
  );
};

export default ChatInterface;
