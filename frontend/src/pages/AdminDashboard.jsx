import React from 'react';
import { Box, Typography, Card, CardContent, Grid } from '@mui/material';

const AdminDashboard = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ fontWeight: 700, mb: 2 }}>Admin Dashboard</Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6">User Management</Typography>
              <Typography variant="body2" sx={{ color: '#64748b' }}>Access Users page from the sidebar to manage accounts.</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6">System Settings</Typography>
              <Typography variant="body2" sx={{ color: '#64748b' }}>Configure application settings from the Settings page.</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AdminDashboard;


