import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Avatar,
  Chip,
  IconButton,
  Button,
  Grid,
  TextField,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  MoreVert,
  Computer,
  BugReport,
  Security,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { apiService } from '../services/apiService';
import authService from '../services/authService';

const Tickets = () => {
  const [tickets, setTickets] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');

  // Load tickets data
  const loadTickets = async () => {
    try {
      setIsLoading(true);
      const userEmail = authService.getEmail();
      if (!userEmail) {
        console.warn('No user email found');
        return;
      }
      
      const data = await apiService.getDashboardData(userEmail);
      setTickets(data.recent_tickets || []);
    } catch (error) {
      console.error('Error loading tickets:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadTickets();
  }, []);

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'Hardware & Infrastructure': return Computer;
      case 'Software & Digital Services': return BugReport;
      case 'Access & Security': return Security;
      default: return Computer;
    }
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'open': return '#f59e0b';
      case 'in progress': return '#3b82f6';
      case 'resolved': return '#10b981';
      case 'closed': return '#6b7280';
      default: return '#64748b';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority.toLowerCase()) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#64748b';
    }
  };

  // Filter tickets based on search and filters
  const filteredTickets = tickets.filter(ticket => {
    const matchesSearch = ticket.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         ticket.ticket_number.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || ticket.status.toLowerCase() === statusFilter;
    const matchesPriority = priorityFilter === 'all' || ticket.priority.toLowerCase() === priorityFilter;
    
    return matchesSearch && matchesStatus && matchesPriority;
  });

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, color: '#1e293b', mb: 1 }}>
            Tickets
          </Typography>
          <Typography variant="body1" sx={{ color: '#64748b' }}>
            Manage and track your support tickets
          </Typography>
        </Box>
        
        <Button
          variant="outlined"
          onClick={loadTickets}
          disabled={isLoading}
          startIcon={isLoading ? <RefreshIcon /> : <RefreshIcon />}
          sx={{
            borderColor: '#3b82f6',
            color: '#3b82f6',
            '&:hover': {
              borderColor: '#2563eb',
              backgroundColor: 'rgba(59, 130, 246, 0.04)'
            }
          }}
        >
          {isLoading ? 'Refreshing...' : 'Refresh'}
        </Button>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search tickets..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon sx={{ color: '#64748b' }} />
                    </InputAdornment>
                  ),
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '12px',
                  }
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  label="Status"
                  onChange={(e) => setStatusFilter(e.target.value)}
                  sx={{ borderRadius: '12px' }}
                >
                  <MenuItem value="all">All Status</MenuItem>
                  <MenuItem value="open">Open</MenuItem>
                  <MenuItem value="in progress">In Progress</MenuItem>
                  <MenuItem value="resolved">Resolved</MenuItem>
                  <MenuItem value="closed">Closed</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={priorityFilter}
                  label="Priority"
                  onChange={(e) => setPriorityFilter(e.target.value)}
                  sx={{ borderRadius: '12px' }}
                >
                  <MenuItem value="all">All Priority</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<FilterIcon />}
                sx={{
                  borderColor: '#64748b',
                  color: '#64748b',
                  borderRadius: '12px',
                  '&:hover': {
                    borderColor: '#475569',
                    backgroundColor: 'rgba(100, 116, 139, 0.04)'
                  }
                }}
              >
                Filters
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tickets Table */}
      <Card>
        <CardContent sx={{ p: 0 }}>
          <Box sx={{ p: 3, borderBottom: '1px solid rgba(0,0,0,0.1)' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, color: '#1e293b' }}>
              All Tickets ({filteredTickets.length})
            </Typography>
          </Box>
          
          <Box sx={{ overflowX: 'auto' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600, color: '#64748b', fontSize: '0.875rem' }}>Ticket ID</TableCell>
                  <TableCell sx={{ fontWeight: 600, color: '#64748b', fontSize: '0.875rem' }}>Title</TableCell>
                  <TableCell sx={{ fontWeight: 600, color: '#64748b', fontSize: '0.875rem' }}>User</TableCell>
                  <TableCell sx={{ fontWeight: 600, color: '#64748b', fontSize: '0.875rem' }}>Priority</TableCell>
                  <TableCell sx={{ fontWeight: 600, color: '#64748b', fontSize: '0.875rem' }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 600, color: '#64748b', fontSize: '0.875rem' }}>Time</TableCell>
                  <TableCell sx={{ fontWeight: 600, color: '#64748b', fontSize: '0.875rem' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredTickets.map((ticket) => {
                  const CategoryIcon = getCategoryIcon(ticket.category);
                  return (
                    <TableRow 
                      key={ticket.id}
                      sx={{ 
                        '&:hover': { backgroundColor: '#f8fafc' },
                        borderBottom: '1px solid rgba(0,0,0,0.05)'
                      }}
                    >
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <CategoryIcon sx={{ fontSize: 16, color: '#64748b' }} />
                          <Typography variant="body2" sx={{ fontWeight: 600, color: '#3b82f6' }}>
                            {ticket.ticket_number}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 500, color: '#1e293b' }}>
                          {ticket.title}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#64748b' }}>
                          {ticket.category}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Avatar sx={{ width: 32, height: 32, fontSize: '0.875rem', bgcolor: '#3b82f6' }}>
                            {ticket.user.split(' ').map(n => n[0]).join('')}
                          </Avatar>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {ticket.user}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={ticket.priority} 
                          size="small"
                          sx={{ 
                            backgroundColor: getPriorityColor(ticket.priority) + '20',
                            color: getPriorityColor(ticket.priority),
                            fontWeight: 600,
                            fontSize: '0.75rem',
                            height: 24
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={ticket.status} 
                          size="small"
                          sx={{ 
                            backgroundColor: getStatusColor(ticket.status) + '20',
                            color: getStatusColor(ticket.status),
                            fontWeight: 600,
                            fontSize: '0.75rem',
                            height: 24
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ color: '#64748b' }}>
                          {ticket.time}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <IconButton size="small" sx={{ color: '#64748b' }}>
                          <MoreVert sx={{ fontSize: 16 }} />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </Box>
          
          {filteredTickets.length === 0 && (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="body1" sx={{ color: '#64748b' }}>
                {searchQuery || statusFilter !== 'all' || priorityFilter !== 'all' 
                  ? 'No tickets match your filters' 
                  : 'No tickets found. Create your first ticket using the AI Assistant!'}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Tickets;
