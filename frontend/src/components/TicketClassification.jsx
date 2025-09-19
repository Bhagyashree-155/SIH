import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Grid, 
  Chip,
  LinearProgress,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  BugReport,
  Computer,
  WifiOff,
  Security,
  Assignment,
  ErrorOutline,
  PriorityHigh,
  HourglassEmpty,
  CheckCircle,
  Block
} from '@mui/icons-material';
import ticketService from '../services/ticketService';

const TicketClassification = () => {
  const [loading, setLoading] = useState(true);
  const [classifications, setClassifications] = useState([]);
  
  // Icons mapping for categories
  const categoryIcons = {
    'Hardware': Computer,
    'Software': BugReport,
    'Network': WifiOff,
    'Access Control': Security,
    'Other': Assignment
  };
  
  // Icons mapping for priorities
  const priorityIcons = {
    'Critical': ErrorOutline,
    'High': PriorityHigh,
    'Medium': Assignment,
    'Low': Assignment
  };
  
  // Icons mapping for statuses
  const statusIcons = {
    'Open': Assignment,
    'In Progress': HourglassEmpty,
    'Pending': HourglassEmpty,
    'Resolved': CheckCircle,
    'Closed': Block
  };
  
  // Colors mapping
  const colorMap = {
    'Hardware': '#3b82f6',
    'Software': '#10b981',
    'Network': '#f59e0b',
    'Access Control': '#6366f1',
    'Other': '#64748b',
    'Critical': '#ef4444',
    'High': '#f59e0b',
    'Medium': '#3b82f6',
    'Low': '#10b981',
    'Open': '#3b82f6',
    'In Progress': '#f59e0b',
    'Pending': '#6366f1',
    'Resolved': '#10b981',
    'Closed': '#64748b'
  };
  
  useEffect(() => {
    const loadClassifications = async () => {
      try {
        setLoading(true);
        const data = await ticketService.fetchTicketClassifications();
        
        // Transform the data into the format needed for display
        const formattedData = [
          {
            title: 'By Category',
            items: data.categories.map(item => ({
              name: item.name,
              count: item.count,
              color: colorMap[item.name] || '#64748b',
              icon: categoryIcons[item.name] || Assignment
            }))
          },
          {
            title: 'By Priority',
            items: data.priorities.map(item => ({
              name: item.name,
              count: item.count,
              color: colorMap[item.name] || '#64748b',
              icon: priorityIcons[item.name] || Assignment
            }))
          },
          {
            title: 'By Status',
            items: data.statuses.map(item => ({
              name: item.name,
              count: item.count,
              color: colorMap[item.name] || '#64748b',
              icon: statusIcons[item.name] || Assignment
            }))
          }
        ];
        
        setClassifications(formattedData);
      } catch (error) {
        console.error('Error loading classifications:', error);
        // Set default data in case of error
        setClassifications([
          {
            title: 'By Category',
            items: [
              { name: 'Hardware', count: 35, color: '#3b82f6', icon: Computer },
              { name: 'Software', count: 28, color: '#10b981', icon: BugReport },
              { name: 'Network', count: 22, color: '#f59e0b', icon: WifiOff },
              { name: 'Access Control', count: 15, color: '#6366f1', icon: Security },
              { name: 'Other', count: 10, color: '#64748b', icon: Assignment }
            ]
          },
          {
            title: 'By Priority',
            items: [
              { name: 'Critical', count: 8, color: '#ef4444', icon: ErrorOutline },
              { name: 'High', count: 17, color: '#f59e0b', icon: PriorityHigh },
              { name: 'Medium', count: 42, color: '#3b82f6', icon: Assignment },
              { name: 'Low', count: 43, color: '#10b981', icon: Assignment }
            ]
          },
          {
            title: 'By Status',
            items: [
              { name: 'Open', count: 32, color: '#3b82f6', icon: Assignment },
              { name: 'In Progress', count: 28, color: '#f59e0b', icon: HourglassEmpty },
              { name: 'Pending', count: 15, color: '#6366f1', icon: HourglassEmpty },
              { name: 'Resolved', count: 25, color: '#10b981', icon: CheckCircle },
              { name: 'Closed', count: 10, color: '#64748b', icon: Block }
            ]
          }
        ]);
      } finally {
        setLoading(false);
      }
    };
    
    loadClassifications();
  }, []);

  // Calculate total for percentages
  const getTotalCount = (items) => {
    return items.reduce((sum, item) => sum + item.count, 0);
  };

  return (
    <Grid container spacing={3}>
      {loading ? (
        // Loading state
        <Box sx={{ display: 'flex', justifyContent: 'center', width: '100%', py: 5 }}>
          <CircularProgress />
        </Box>
      ) : (
        // Data display
        classifications.map((classification, index) => {
          const total = getTotalCount(classification.items);
          
          return (
            <Grid size={{ xs: 12, md: 4 }} key={index}>
              <Card className="glass-card" sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                    {classification.title}
                  </Typography>
                  
                  <Box sx={{ mt: 2 }}>
                    {classification.items.map((item, idx) => {
                      const percentage = Math.round((item.count / total) * 100);
                      const ItemIcon = item.icon;
                      
                      return (
                        <Box key={idx} sx={{ mb: 2 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {ItemIcon && (
                                <ItemIcon sx={{ color: item.color, fontSize: 18 }} />
                              )}
                              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                {item.name}
                              </Typography>
                            </Box>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                {item.count}
                              </Typography>
                              <Chip 
                                label={`${percentage}%`} 
                                size="small" 
                                sx={{ 
                                  height: '20px', 
                                  fontSize: '0.7rem',
                                  backgroundColor: `${item.color}20`,
                                  color: item.color,
                                  fontWeight: 600
                                }} 
                              />
                            </Box>
                          </Box>
                          <Tooltip title={`${percentage}% of tickets`}>
                            <LinearProgress 
                              variant="determinate" 
                              value={percentage} 
                              sx={{ 
                                height: 6, 
                                borderRadius: 1,
                                backgroundColor: 'rgba(0,0,0,0.05)',
                                '& .MuiLinearProgress-bar': {
                                  backgroundColor: item.color,
                                  borderRadius: 1
                                }
                              }} 
                            />
                          </Tooltip>
                        </Box>
                      );
                    })}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          );
        })
      )}
    </Grid>
  );
};

export default TicketClassification;