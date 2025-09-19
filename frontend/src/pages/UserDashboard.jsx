import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const UserDashboard = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ fontWeight: 700, mb: 2 }}>Welcome</Typography>
      <Card>
        <CardContent>
          <Typography variant="h6">Start with AI Assistant</Typography>
          <Typography variant="body2" sx={{ color: '#64748b' }}>Use the AI Chat on the dashboard to create and classify tickets quickly.</Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default UserDashboard;


