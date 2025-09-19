import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import TicketClassification from './components/TicketClassification';
import ClassificationOne from './pages/ClassificationOne';
import ClassificationTwo from './pages/ClassificationTwo';
import ClassificationThree from './pages/ClassificationThree';
import { 
  Box, 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  Container,
  Card,
  CardContent,
  Grid,
  Avatar,
  Chip,
  IconButton,
  Drawer,
  List,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Badge,
  TextField,
  InputAdornment,
  Paper,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tooltip
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  ConfirmationNumber as TicketIcon,
  People as PeopleIcon,
  School as KnowledgeIcon,
  Chat as ChatIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  Menu as MenuIcon,
  Search as SearchIcon,
  Add as AddIcon,
  TrendingUp,
  Assignment,
  Schedule,
  CheckCircle,
  ArrowUpward,
  ArrowDownward,
  Speed as SpeedIcon,
  BugReport,
  Computer,
  WifiOff,
  Security,
  MoreVert,
  Person as PersonIcon
} from '@mui/icons-material';
import './App.css';

const drawerWidth = 280;

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

function AppContent() {
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const menuItems = React.useMemo(() => [
    { id: 'dashboard', label: 'Dashboard', icon: DashboardIcon, color: '#3b82f6', path: '/' },
    { id: 'tickets', label: 'Tickets', icon: TicketIcon, color: '#10b981', badge: 12, path: '/tickets' },
    { id: 'users', label: 'Users', icon: PeopleIcon, color: '#f59e0b', path: '/users' },
    { id: 'knowledge', label: 'Knowledge Base', icon: KnowledgeIcon, color: '#8b5cf6', path: '/knowledge' },
    { id: 'chat', label: 'AI Chat', icon: ChatIcon, color: '#06b6d4', path: '/chat' },
    { id: 'category1', label: 'Category One', icon: Computer, color: '#3b82f6', path: '/category1' },
    { id: 'category2', label: 'Category Two', icon: BugReport, color: '#10b981', path: '/category2' },
    { id: 'category3', label: 'Category Three', icon: Security, color: '#f59e0b', path: '/category3' },
    { id: 'settings', label: 'Settings', icon: SettingsIcon, color: '#6b7280', path: '/settings' },
  ], []);

  const stats = [
    { 
      title: 'Total Tickets', 
      value: '1,234', 
      change: '+12%', 
      icon: Assignment, 
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      progress: 85
    },
    { 
      title: 'Open Tickets', 
      value: '456', 
      change: '+5%', 
      icon: Schedule, 
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      progress: 65
    },
    { 
      title: 'Resolved Today', 
      value: '89', 
      change: '+23%', 
      icon: CheckCircle, 
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      progress: 92
    },
    { 
      title: 'Avg Response Time', 
      value: '2.4h', 
      change: '-8%', 
      icon: SpeedIcon, 
      gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
      progress: 78
    },
  ];

  const recentTickets = [
    { 
      id: 'PG-2025001', 
      title: 'VPN Connection Issue', 
      user: 'John Smith', 
      priority: 'High', 
      status: 'Open', 
      time: '2 hours ago',
      category: 'Network'
    },
    { 
      id: 'PG-2025002', 
      title: 'Password Reset Request', 
      user: 'Sarah Johnson', 
      priority: 'Medium', 
      status: 'In Progress', 
      time: '4 hours ago',
      category: 'Access Control'
    },
    { 
      id: 'PG-2025003', 
      title: 'Software Installation', 
      user: 'Mike Wilson', 
      priority: 'Low', 
      status: 'Resolved', 
      time: '1 day ago',
      category: 'Software'
    },
    { 
      id: 'PG-2025004', 
      title: 'Hardware Replacement', 
      user: 'Lisa Brown', 
      priority: 'Urgent', 
      status: 'Open', 
      time: '30 minutes ago',
      category: 'Hardware'
    },
    { 
      id: 'PG-2025005', 
      title: 'Email Configuration', 
      user: 'David Lee', 
      priority: 'Medium', 
      status: 'Closed', 
      time: '3 days ago',
      category: 'Email'
    }
  ];

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'open': return '#f59e0b';
      case 'in progress': return '#3b82f6';
      case 'resolved': return '#10b981';
      case 'closed': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority.toLowerCase()) {
      case 'low': return '#10b981';
      case 'medium': return '#f59e0b';
      case 'high': return '#ef4444';
      case 'urgent': return '#dc2626';
      case 'critical': return '#991b1b';
      default: return '#6b7280';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category.toLowerCase()) {
      case 'network': return WifiOff;
      case 'hardware': return Computer;
      case 'software': return BugReport;
      case 'access control': return Security;
      default: return Assignment;
    }
  };

  // Use location for active menu highlighting
  const location = useLocation();
  // const navigate = useNavigate(); // Removed duplicate declaration
  const currentPath = location.pathname;
  
  // Find active section based on path
  const getActiveSection = React.useCallback((path) => {
    if (path === '/') return 'dashboard';
    const item = menuItems.find(item => item.path === path);
    return item ? item.id : 'dashboard';
  }, [menuItems]);
  
  const [activeSection, setActiveSection] = useState(getActiveSection(currentPath));
  
  // Update active section when location changes
  React.useEffect(() => {
    setActiveSection(getActiveSection(currentPath));
  }, [currentPath, getActiveSection]);
  
  const handleMenuClick = (item) => {
    setActiveSection(item.id);
    navigate(item.path);
    setMobileOpen(false); // Close drawer on mobile
  };
  
  const drawer = (
    <Box sx={{ height: '100%', bgcolor: 'white', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
      <Box sx={{ p: 3, background: 'linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%)' }}>
        <Typography variant="h5" sx={{ color: 'white', fontWeight: 700, textAlign: 'center' }}>
          POWERGRID
        </Typography>
        <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.8)', textAlign: 'center', mt: 0.5 }}>
          AI Ticketing System
        </Typography>
      </Box>
      <List sx={{ px: 2, py: 2 }}>
        {menuItems.map((item) => (
          <ListItemButton
            key={item.id}
            onClick={() => handleMenuClick(item)}
            sx={{
              borderRadius: '12px',
              mb: 1,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              backgroundColor: activeSection === item.id ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
              '&:hover': {
                backgroundColor: activeSection === item.id ? 'rgba(59, 130, 246, 0.15)' : 'rgba(0,0,0,0.04)',
                transform: 'translateX(6px)',
              }
            }}
          >
            <ListItemIcon sx={{ minWidth: '48px' }}>
              <Box 
                sx={{ 
                  p: 1.5, 
                  borderRadius: '10px',
                  backgroundColor: activeSection === item.id ? item.color : 'rgba(0,0,0,0.06)',
                  transition: 'all 0.2s ease'
                }}
              >
                <item.icon 
                  sx={{ 
                    color: activeSection === item.id ? 'white' : item.color,
                    fontSize: '20px'
                  }} 
                />
              </Box>
            </ListItemIcon>
            <ListItemText 
              primary={item.label} 
              sx={{
                '& .MuiListItemText-primary': {
                  fontWeight: activeSection === item.id ? 600 : 500,
                  color: activeSection === item.id ? '#1e40af' : '#374151',
                  fontSize: '0.95rem'
                }
              }}
            />
            {item.badge && (
              <Chip 
                label={item.badge} 
                size="small" 
                sx={{ 
                  height: '22px', 
                  fontSize: '11px',
                  fontWeight: 600,
                  backgroundColor: '#ef4444',
                  color: 'white',
                  '& .MuiChip-label': {
                    px: 1
                  }
                }}
              />
            )}
          </ListItemButton>
        ))}
      </List>
    </Box>
  );

  const [messages, setMessages] = useState([{
    text: "Hello! I'm your AI assistant. I can help you with:\n• Creating and managing tickets\n• Finding solutions in the knowledge base\n• Routing tickets to the right team\n• Providing status updates",
    sender: 'ai',
    timestamp: new Date().toISOString()
  }]);
  const navigate = useNavigate();
  const messagesEndRef = React.useRef(null);
  
  // Scroll to bottom of messages
  React.useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);
  
  // Handle sending a message
  const handleSendMessage = async () => {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    const userMessage = {
      text: message,
      sender: 'user',
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    input.value = '';
    
    try {
      // Import the ticket service
      const ticketService = await import('./services/ticketService.js');
      
      // Classify the message
      const category = await ticketService.default.classifyMessage(message);
      
      // Add AI response
      const aiResponse = {
        text: `I've classified your query as: ${category}. Redirecting you to the appropriate dashboard...`,
        sender: 'ai',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiResponse]);
      
      // Redirect based on classification
      setTimeout(() => {
        if (category === 'Hardware') {
          navigate('/category1');
        } else if (category === 'Software') {
          navigate('/category2');
        } else {
          navigate('/category3');
        }
      }, 1500);
      
    } catch (error) {
      console.error('Error processing message:', error);
      
      // Add error message
      const errorMessage = {
        text: 'Sorry, I encountered an error processing your request. Please try again.',
        sender: 'ai',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
  };
  
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#f8fafc' }}>
      {/* App Bar */}
      <AppBar 
        position="fixed" 
        className="glass-card"
        sx={{ 
          width: { md: `calc(100% - ${drawerWidth}px)` }, 
          ml: { md: `${drawerWidth}px` },
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
          boxShadow: '0 4px 30px rgba(0, 0, 0, 0.1)',
        }}
      >
        <Toolbar sx={{ px: 3 }}>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ 
              display: { md: 'none' }, 
              mr: 1, 
              color: '#374151' 
            }}
          >
            <MenuIcon />
          </IconButton>
          
          <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', gap: 2 }}>
            <TextField
              variant="outlined"
              placeholder="Search tickets, users, or articles..."
              size="small"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon sx={{ color: '#9ca3af' }} />
                  </InputAdornment>
                )
              }}
              sx={{
                width: '400px',
                '& .MuiOutlinedInput-root': {
                  borderRadius: '25px',
                  backgroundColor: 'white',
                  '& fieldset': {
                    border: '1px solid #e5e7eb',
                  },
                  '&:hover fieldset': {
                    border: '1px solid #3b82f6',
                  },
                  '&.Mui-focused fieldset': {
                    border: '1px solid #3b82f6',
                  },
                },
              }}
            />
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              sx={{
                borderRadius: '25px',
                textTransform: 'none',
                fontWeight: 600,
                px: 3,
                py: 1,
                background: 'linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%)',
                boxShadow: '0 4px 15px rgba(14, 165, 233, 0.3)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
                  boxShadow: '0 6px 20px rgba(14, 165, 233, 0.4)',
                }
              }}
            >
              New Ticket
            </Button>
            
            <IconButton sx={{ color: '#374151' }}>
              <Badge badgeContent={5} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
            
            <Tooltip title="John Doe">
              <Avatar 
                sx={{ 
                  width: 40, 
                  height: 40, 
                  cursor: 'pointer',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  fontSize: '16px',
                  fontWeight: 600,
                  border: '2px solid rgba(59, 130, 246, 0.2)',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    border: '2px solid rgba(59, 130, 246, 0.4)',
                    transform: 'scale(1.05)'
                  }
                }}
              >
                JD
              </Avatar>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              border: 'none',
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box
        component="main"
        className="flex-1 p-6"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          mt: '80px'
        }}
      >
        <Container maxWidth="xl" className="animate-fadeIn">
          <Routes>
            <Route path="/" element={
              <>
                {/* Welcome Header */}
                <Box sx={{ mb: 5 }}>
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
                    Welcome back, John! 👋
                  </Typography>
                  <Typography variant="h6" sx={{ color: '#64748b', fontWeight: 500 }}>
                    Here's what's happening with your tickets today
                  </Typography>
                </Box>

                {/* Statistics Cards */}
                <Grid container spacing={4} sx={{ mb: 6 }}>
                  {stats.map((stat, index) => (
                    <Grid size={{ xs: 12, sm: 6, lg: 3 }} key={index}>
                      <Card 
                        className="glass-card"
                        sx={{
                          height: '100%',
                          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                          '&:hover': {
                            transform: 'translateY(-8px) scale(1.02)',
                            boxShadow: '0 20px 40px rgba(0,0,0,0.2)'
                          }
                        }}
                      >
                        <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
                          {/* Icon and Change */}
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
                            <Box 
                              sx={{
                                width: 56,
                                height: 56,
                                borderRadius: '16px',
                                background: stat.gradient,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                boxShadow: '0 8px 32px rgba(0,0,0,0.3)'
                              }}
                            >
                              <stat.icon sx={{ color: 'white', fontSize: 28 }} />
                            </Box>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                              {stat.change.startsWith('+') ? (
                                <ArrowUpward sx={{ fontSize: 16, color: '#10b981' }} />
                              ) : (
                                <ArrowDownward sx={{ fontSize: 16, color: '#ef4444' }} />
                              )}
                              <Typography 
                                variant="body2" 
                                sx={{
                                  fontWeight: 600,
                                  color: stat.change.startsWith('+') ? '#10b981' : '#ef4444'
                                }}
                              >
                                {stat.change}
                              </Typography>
                            </Box>
                          </Box>

                          {/* Value and Title */}
                          <Box sx={{ flex: 1 }}>
                            <Typography 
                              variant="h3" 
                              sx={{ 
                                fontWeight: 700, 
                                color: '#1e293b',
                                mb: 1,
                                background: stat.gradient,
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent'
                              }}
                            >
                              {stat.value}
                            </Typography>
                            <Typography variant="body1" sx={{ color: '#64748b', fontWeight: 500, mb: 2 }}>
                              {stat.title}
                            </Typography>
                            
                            {/* Progress Bar */}
                            <Box>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="caption" sx={{ color: '#64748b' }}>Progress</Typography>
                                <Typography variant="caption" sx={{ color: '#64748b' }}>{stat.progress}%</Typography>
                              </Box>
                              <LinearProgress 
                                variant="determinate" 
                                value={stat.progress}
                                sx={{
                                  height: 6,
                                  borderRadius: 3,
                                  backgroundColor: 'rgba(0,0,0,0.1)',
                                  '& .MuiLinearProgress-bar': {
                                    borderRadius: 3,
                                    background: stat.gradient
                                  }
                                }}
                              />
                            </Box>
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>

                {/* Ticket Classifications */}
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
                    Ticket Classifications
                  </Typography>
                  <TicketClassification />
                </Box>
                
                {/* Main Content Area */}
                <Grid container spacing={4}>
                  {/* Recent Tickets Table */}
                  <Grid size={{ xs: 12, lg: 8 }}>
                    <Card className="glass-card" sx={{ height: 'fit-content' }}>
                      <Box sx={{ p: 3, borderBottom: '1px solid rgba(0,0,0,0.1)' }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="h5" sx={{ fontWeight: 700, color: '#1e293b' }}>
                            Recent Tickets
                          </Typography>
                          <Button 
                            variant="outlined" 
                            size="small"
                            sx={{ 
                              borderRadius: '20px',
                              textTransform: 'none',
                              borderColor: '#3b82f6',
                              color: '#3b82f6',
                              '&:hover': {
                                borderColor: '#2563eb',
                                backgroundColor: '#eff6ff'
                              }
                            }}
                          >
                            View All
                          </Button>
                        </Box>
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
                            {recentTickets.map((ticket) => {
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
                                        {ticket.id}
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
                    </Card>
                  </Grid>
                  
                  {/* AI Assistant */}
                  <Grid size={{ xs: 12, lg: 4 }}>
                    <Card className="glass-card" sx={{ height: '600px' }}>
                      <Box sx={{ p: 3, borderBottom: '1px solid rgba(0,0,0,0.1)' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Box 
                            sx={{
                              width: 40,
                              height: 40,
                              borderRadius: '12px',
                              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center'
                            }}
                          >
                            <ChatIcon sx={{ color: 'white', fontSize: 20 }} />
                          </Box>
                          <Box>
                            <Typography variant="h6" sx={{ fontWeight: 600, color: '#1e293b' }}>
                              AI Assistant
                            </Typography>
                            <Typography variant="caption" sx={{ color: '#10b981' }}>
                              ● Online
                            </Typography>
                          </Box>
                        </Box>
                      </Box>
                      <Box sx={{ p: 3, height: 'calc(100% - 88px)', display: 'flex', flexDirection: 'column' }}>
                        {/* Chat Messages */}
                        <Box sx={{ flex: 1, mb: 2, overflowY: 'auto' }}>
                          {messages.map((message, index) => (
                            <Box key={index} sx={{ mb: 2 }}>
                              <Typography variant="body2" sx={{ 
                                bgcolor: message.sender === 'user' ? '#3b82f6' : '#f1f5f9', 
                                p: 2, 
                                borderRadius: message.sender === 'user' ? '12px 12px 4px 12px' : '12px 12px 12px 4px',
                                color: message.sender === 'user' ? 'white' : '#475569',
                                mb: 1,
                                float: message.sender === 'user' ? 'right' : 'left',
                                maxWidth: '80%',
                                clear: 'both'
                              }}>
                                {message.text}
                              </Typography>
                              <Typography variant="caption" sx={{ 
                                color: '#64748b', 
                                ml: message.sender === 'user' ? 0 : 1,
                                mr: message.sender === 'user' ? 1 : 0,
                                float: message.sender === 'user' ? 'right' : 'left',
                                clear: 'both'
                              }}>
                                {message.sender === 'user' ? 'You' : 'AI Assistant'} • {new Date(message.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                              </Typography>
                            </Box>
                          ))}
                          <div ref={messagesEndRef} />
                        </Box>
                        
                        {/* Chat Input */}
                        <Box>
                          <TextField
                            fullWidth
                            placeholder="Ask me anything about tickets or IT issues..."
                            variant="outlined"
                            size="small"
                            multiline
                            rows={2}
                            id="chat-input"
                            onKeyDown={(e) => {
                              if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                document.getElementById('send-message-btn').click();
                              }
                            }}
                            InputProps={{
                              endAdornment: (
                                <InputAdornment position="end">
                                  <IconButton 
                                    id="send-message-btn"
                                    size="small" 
                                    onClick={handleSendMessage}
                                    sx={{ 
                                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                      color: 'white',
                                      '&:hover': {
                                        background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)'
                                      }
                                    }}
                                  >
                                    <ChatIcon sx={{ fontSize: 16 }} />
                                  </IconButton>
                                </InputAdornment>
                              )
                            }}
                            sx={{
                              '& .MuiOutlinedInput-root': {
                                borderRadius: '12px',
                                '& fieldset': {
                                  borderColor: 'rgba(0,0,0,0.1)'
                                },
                                '&:hover fieldset': {
                                  borderColor: '#3b82f6'
                                },
                                '&.Mui-focused fieldset': {
                                  borderColor: '#3b82f6'
                                }
                              }
                            }}
                          />
                        </Box>
                      </Box>
                    </Card>
                  </Grid>
                </Grid>
              </>
            } />
            
            {/* Classification Dashboard Routes */}
            <Route path="/category1" element={<ClassificationOne />} />
            <Route path="/category2" element={<ClassificationTwo />} />
            <Route path="/category3" element={<ClassificationThree />} />
            
            {/* Other routes can be added here */}
            <Route path="*" element={<Typography variant="h4">Page Not Found</Typography>} />
          </Routes>
        </Container>
      </Box>
    </Box>
  );
}

export default App;
