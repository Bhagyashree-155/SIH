import React from 'react';
import { Box, Typography, Container } from '@mui/material';
import AIChat from '../components/AIChat';

const AIChatPage = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h3" 
          sx={{ 
            fontWeight: 700, 
            color: '#1e293b', 
            mb: 1,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          AI Chat Assistant
        </Typography>
        <Typography variant="h6" sx={{ color: '#64748b', fontWeight: 500 }}>
          Get instant help with your IT support needs
        </Typography>
      </Box>

      <Box sx={{ 
        height: '70vh',
        minHeight: '500px'
      }}>
        <AIChat />
      </Box>
    </Container>
  );
};

export default AIChatPage;
