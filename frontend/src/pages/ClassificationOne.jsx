import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Container,
  Grid,
  Card, 
  CardContent, 
  TextField,
  Button,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider,
  Paper,
  InputAdornment,
  IconButton,
  Badge,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Computer as HardwareIcon,
  Send as SendIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import ChatInterface from '../components/ChatInterface';
import { apiService } from '../services/apiService';

const ClassificationOne = () => {
  const [tickets, setTickets] = useState([]);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [newQuery, setNewQuery] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    total: 0,
    open: 0,
    inProgress: 0,
    resolved: 0
  });

  const category = 'Hardware & Infrastructure';

  useEffect(() => {
    loadTickets();
    loadStats();
  }, []);

  const loadTickets = async () => {
    try {
      setIsLoading(true);
      const response = await apiService.getTicketsByCategory(category);
      setTickets(response.tickets || []);
    } catch (error) {
      setError('Failed to load tickets');
      console.error('Error loading tickets:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await apiService.getTicketsByCategory(category);
      const tickets = response.tickets || [];
      
      setStats({
        total: tickets.length,
        open: tickets.filter(t => t.status === 'open').length,
        inProgress: tickets.filter(t => t.status === 'in_progress').length,
        resolved: tickets.filter(t => t.status === 'resolved').length
      });
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleSubmitQuery = async () => {
    if (!newQuery.trim()) return;

    try {
      setIsSubmitting(true);
      setError(null);
      
      const userInfo = {
        user_id: 'user_123',
        user_name: 'John Doe',
        user_email: 'john.doe@powergrid.in'
      };

      const response = await apiService.classifyMessage(newQuery, userInfo);
      
      // If the query was classified as this category, create a ticket
      if (response.category === category) {
        setSelectedTicket({
          ticket_id: response.ticket_id,
          ticket_number: response.ticket_number,
          category: response.category,
          subcategory: response.subcategory,
          priority: response.priority,
          confidence: response.confidence,
          reasoning: response.reasoning,
          suggested_solutions: response.suggested_solutions
        });
        
        // Add to tickets list
        setTickets(prev => [{
          ticket_id: response.ticket_id,
          ticket_number: response.ticket_number,
          title: `Query: ${newQuery.substring(0, 50)}...`,
          category: response.category,
          subcategory: response.subcategory,
          priority: response.priority,
          status: 'open',
          requester_name: 'John Doe',
          created_at: new Date().toISOString(),
          last_message: newQuery,
          unread_count: 0
        }, ...prev]);
        
        loadStats();
      } else {
        setError(`This query was classified as "${response.category}" and should be handled in the appropriate category.`);
      }
      
      setNewQuery('');
    } catch (error) {
      setError('Failed to process your query');
      console.error('Error submitting query:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTicketSelect = (ticket) => {
    setSelectedTicket(ticket);
  };

  const handleTicketUpdate = (updateData) => {
    // Update ticket in the list
    setTickets(prev => prev.map(ticket => 
      ticket.ticket_id === updateData.ticket_id 
        ? { ...ticket, ...updateData.update }
        : ticket
    ));
    
    // Update stats
    loadStats();
  };

  const filteredTickets = tickets.filter(ticket =>
    ticket.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    ticket.ticket_number.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'low': return '#10b981';
      case 'medium': return '#f59e0b';
      case 'high': return '#ef4444';
      case 'urgent': return '#dc2626';
      case 'critical': return '#991b1b';
      default: return '#6b7280';
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'open': return '#f59e0b';
      case 'in_progress': return '#3b82f6';
      case 'resolved': return '#10b981';
      case 'closed': return '#6b7280';
      default: return '#6b7280';
    }
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Avatar sx={{ bgcolor: '#3b82f6', width: 56, height: 56 }}>
              <HardwareIcon sx={{ fontSize: 28 }} />
            </Avatar>
            <Box>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#1e293b' }}>
                Hardware & Infrastructure
              </Typography>
              <Typography variant="body1" sx={{ color: '#64748b' }}>
                Hardware issues, system failures, and physical infrastructure problems
              </Typography>
            </Box>
          </Box>

          {/* Stats Cards */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)', color: 'white' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 700 }}>
                        {stats.total}
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>
                        Total Tickets
                      </Typography>
                    </Box>
                    <TrendingUpIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)', color: 'white' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 700 }}>
                        {stats.open}
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>
                        Open
                      </Typography>
                    </Box>
                    <ScheduleIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)', color: 'white' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 700 }}>
                        {stats.inProgress}
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>
                        In Progress
                      </Typography>
                    </Box>
                    <HardwareIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', color: 'white' }}>
        <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 700 }}>
                        {stats.resolved}
          </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>
                        Resolved
          </Typography>
                    </Box>
                    <CheckCircleIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                  </Box>
        </CardContent>
      </Card>
            </Grid>
          </Grid>
        </Box>

        <Grid container spacing={4}>
          {/* Left Panel - Query Input and Ticket List */}
          <Grid item xs={12} md={4}>
            {/* New Query Input */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                  Submit New Query
                </Typography>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  placeholder="Describe your hardware or infrastructure issue..."
                  value={newQuery}
                  onChange={(e) => setNewQuery(e.target.value)}
                  disabled={isSubmitting}
                  sx={{ mb: 2 }}
                />
                {error && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                  </Alert>
                )}
                <Button
                  fullWidth
                  variant="contained"
                  onClick={handleSubmitQuery}
                  disabled={!newQuery.trim() || isSubmitting}
                  startIcon={isSubmitting ? <CircularProgress size={20} /> : <SendIcon />}
        sx={{ 
                    background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #2563eb 0%, #1e40af 100%)'
                    }
                  }}
                >
                  {isSubmitting ? 'Processing...' : 'Submit Query'}
                </Button>
              </CardContent>
            </Card>

            {/* Search and Filter */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <TextField
                  fullWidth
                  placeholder="Search tickets..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={loadTickets} size="small">
                          <RefreshIcon />
                        </IconButton>
                      </InputAdornment>
                    )
                  }}
                />
              </CardContent>
            </Card>

            {/* Ticket List */}
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Recent Tickets
                  </Typography>
                  <Badge badgeContent={filteredTickets.length} color="primary">
                    <Typography variant="body2" sx={{ color: '#64748b' }}>
                      Total
                    </Typography>
                  </Badge>
        </Box>
        
                {isLoading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                    <CircularProgress />
                  </Box>
                ) : (
                  <List sx={{ maxHeight: 400, overflowY: 'auto' }}>
                    {filteredTickets.map((ticket, index) => (
                      <React.Fragment key={ticket.ticket_id}>
                        <ListItem
                          button
                          onClick={() => handleTicketSelect(ticket)}
                          selected={selectedTicket?.ticket_id === ticket.ticket_id}
              sx={{
                            borderRadius: '8px',
                            mb: 1,
                            '&.Mui-selected': {
                              bgcolor: '#3b82f620',
                              '&:hover': {
                                bgcolor: '#3b82f630'
                              }
                            }
                          }}
                        >
                          <ListItemAvatar>
                    <Avatar sx={{ bgcolor: '#3b82f6' }}>
                              <HardwareIcon />
                    </Avatar>
                          </ListItemAvatar>
                          <ListItemText
                            primary={ticket.ticket_number}
                            secondary={
                              <Box>
                                <Typography variant="body2" sx={{ color: '#64748b', mb: 0.5 }}>
                                  {ticket.title}
                                </Typography>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                                  <Chip
                                    label={ticket.priority}
                                    size="small"
                                    sx={{
                                      bgcolor: getPriorityColor(ticket.priority) + '20',
                                      color: getPriorityColor(ticket.priority),
                                      fontWeight: 600,
                                      fontSize: '0.7rem',
                                      height: 18
                                    }}
                                  />
                                  <Chip
                                    label={ticket.status}
                                    size="small"
                    sx={{
                                      bgcolor: getStatusColor(ticket.status) + '20',
                                      color: getStatusColor(ticket.status),
                                      fontWeight: 600,
                                      fontSize: '0.7rem',
                                      height: 18
                                    }}
                                  />
                                  {ticket.unread_count > 0 && (
                                    <Badge badgeContent={ticket.unread_count} color="error" />
                                  )}
                                </Box>
            </Box>
                            }
                          />
                        </ListItem>
                        {index < filteredTickets.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                )}
              </CardContent>
            </Card>
              </Grid>

          {/* Right Panel - Chat Interface */}
          <Grid item xs={12} md={8}>
            <Card sx={{ height: '600px' }}>
              {selectedTicket ? (
                <ChatInterface
                  ticketId={selectedTicket.ticket_id}
                  category={category}
                  onTicketUpdate={handleTicketUpdate}
                />
              ) : (
                <Box sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  p: 4,
                  textAlign: 'center'
                }}>
                  <HardwareIcon sx={{ fontSize: 80, color: '#e5e7eb', mb: 2 }} />
                  <Typography variant="h6" sx={{ color: '#64748b', mb: 1 }}>
                    Select a ticket to start chatting
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#9ca3af' }}>
                    Choose a ticket from the list to view the conversation and provide support
                  </Typography>
        </Box>
              )}
            </Card>
          </Grid>
        </Grid>
    </Box>
    </Container>
  );
};

export default ClassificationOne;