import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Avatar,
  Chip
} from '@mui/material';
import {
  Computer as HardwareIcon,
  BugReport as SoftwareIcon,
  Security as SecurityIcon,
  ArrowForward as ArrowForwardIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const TicketClassification = () => {
  const navigate = useNavigate();

  const categories = [
    {
      id: 'hardware',
      title: 'Hardware & Infrastructure',
      description: 'Hardware issues, system failures, and physical infrastructure problems',
      icon: HardwareIcon,
      color: '#3b82f6',
      gradient: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
      examples: ['Laptop not turning on', 'Printer issues', 'Network equipment failure', 'Power problems'],
      path: '/category1'
    },
    {
      id: 'software',
      title: 'Software & Digital Services',
      description: 'Software issues, application errors, and digital service problems',
      icon: SoftwareIcon,
      color: '#10b981',
      gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
      examples: ['Application crashes', 'Email problems', 'VPN connection issues', 'Software installation'],
      path: '/category2'
    },
    {
      id: 'security',
      title: 'Access & Security',
      description: 'Access control, permissions, and security-related issues',
      icon: SecurityIcon,
      color: '#f59e0b',
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
      examples: ['Password reset', 'Account access', 'File permissions', 'Security settings'],
      path: '/category3'
    }
  ];

  const handleCategoryClick = (path) => {
    navigate(path);
  };

  return (
    <Grid container spacing={3}>
      {categories.map((category) => (
        <Grid item xs={12} md={4} key={category.id}>
          <Card
            sx={{
              height: '100%',
              cursor: 'pointer',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              '&:hover': {
                transform: 'translateY(-8px) scale(1.02)',
                boxShadow: '0 20px 40px rgba(0,0,0,0.2)'
              }
            }}
            onClick={() => handleCategoryClick(category.path)}
          >
            <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
              {/* Header */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <Avatar
                  sx={{
                    width: 56,
                    height: 56,
                    background: category.gradient,
                    boxShadow: '0 8px 32px rgba(0,0,0,0.3)'
                  }}
                >
                  <category.icon sx={{ fontSize: 28, color: 'white' }} />
                </Avatar>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: '#1e293b', mb: 0.5 }}>
                    {category.title}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748b' }}>
                    {category.description}
                  </Typography>
                </Box>
              </Box>

              {/* Examples */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" sx={{ color: '#64748b', mb: 1.5, fontWeight: 600 }}>
                  Common Issues:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {category.examples.map((example, index) => (
                    <Chip
                      key={index}
                      label={example}
                      size="small"
                      sx={{
                        bgcolor: category.color + '20',
                        color: category.color,
                        fontWeight: 500,
                        fontSize: '0.75rem',
                        height: 24
                      }}
                    />
                  ))}
                </Box>
              </Box>

              {/* Action Button */}
              <Box sx={{ mt: 'auto' }}>
                <Button
                  fullWidth
                  variant="contained"
                  endIcon={<ArrowForwardIcon />}
                  sx={{
                    background: category.gradient,
                    borderRadius: '12px',
                    textTransform: 'none',
                    fontWeight: 600,
                    py: 1.5,
                    '&:hover': {
                      background: category.gradient,
                      opacity: 0.9,
                      transform: 'translateY(-2px)'
                    }
                  }}
                >
                  View Tickets
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default TicketClassification;
