import React from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  TextField,
  Button,
  Paper,
  Divider,
  Avatar,
  Grid
} from '@mui/material';
import { Send as SendIcon, Person as PersonIcon } from '@mui/icons-material';

const ClassificationTwo = () => {
  const [messages, setMessages] = React.useState([
    { id: 1, text: "This query has been classified as Category Two. How can I help you?", sender: 'ai' }
  ]);
  const [newMessage, setNewMessage] = React.useState('');
  const messagesEndRef = React.useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (newMessage.trim() === '') return;
    
    // Add user message
    setMessages(prev => [...prev, { id: Date.now(), text: newMessage, sender: 'user' }]);
    setNewMessage('');
    
    // Simulate response (in a real app, this would be an API call)
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        id: Date.now(), 
        text: "I'm processing your Category Two query. A support agent will respond shortly.", 
        sender: 'ai' 
      }]);
    }, 1000);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Card className="glass-card" sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
            Category Two Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            This dashboard handles queries related to software issues, application errors, and digital service problems.
          </Typography>
        </CardContent>
      </Card>

      <Paper 
        elevation={3} 
        sx={{ 
          flex: 1, 
          display: 'flex', 
          flexDirection: 'column',
          borderRadius: 2,
          overflow: 'hidden',
          bgcolor: 'background.paper'
        }}
      >
        <Box sx={{ p: 2, bgcolor: '#10b981', color: 'white' }}>
          <Typography variant="h6">Support Chat</Typography>
        </Box>
        
        <Box sx={{ 
          flex: 1, 
          p: 2, 
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: 2
        }}>
          {messages.map((message) => (
            <Box 
              key={message.id}
              sx={{
                display: 'flex',
                justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                mb: 2
              }}
            >
              <Grid container spacing={1} justifyContent={message.sender === 'user' ? 'flex-end' : 'flex-start'} wrap="nowrap">
                {message.sender === 'ai' && (
                  <Grid>
                    <Avatar sx={{ bgcolor: '#10b981' }}>
                      AI
                    </Avatar>
                  </Grid>
                )}
                <Grid size={{ xs: 8 }}>
                  <Paper 
                    elevation={1}
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      bgcolor: message.sender === 'user' ? '#e3f2fd' : '#f5f5f5',
                      color: 'text.primary'
                    }}
                  >
                    <Typography variant="body1">{message.text}</Typography>
                  </Paper>
                </Grid>
                {message.sender === 'user' && (
                  <Grid>
                    <Avatar sx={{ bgcolor: '#10b981' }}>
                      <PersonIcon />
                    </Avatar>
                  </Grid>
                )}
              </Grid>
            </Box>
          ))}
          <div ref={messagesEndRef} />
        </Box>
        
        <Divider />
        
        <Box sx={{ p: 2, display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            placeholder="Type your response..."
            variant="outlined"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          />
          <Button 
            variant="contained" 
            color="primary" 
            endIcon={<SendIcon />}
            onClick={handleSendMessage}
            sx={{ borderRadius: 2 }}
          >
            Send
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default ClassificationTwo;