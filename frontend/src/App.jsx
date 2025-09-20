import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import TicketClassification from './components/TicketClassification';
import ClassificationOne from './pages/ClassificationOne';
import ClassificationTwo from './pages/ClassificationTwo';
import ClassificationThree from './pages/ClassificationThree';
import Login from './pages/Login';
import Signup from './pages/Signup';
import AdminDashboard from './pages/AdminDashboard';
import UserDashboard from './pages/UserDashboard';
import AIChatPage from './pages/AIChatPage';
import Tickets from './pages/Tickets';
import ProtectedRoute from './components/ProtectedRoute';
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
  Tooltip,
  Tabs,
  Tab,
  CircularProgress
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
  Person as PersonIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import authService from './services/authService';
import { apiService } from './services/apiService';
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
  const [activeTab, setActiveTab] = useState(0);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoadingDashboard, setIsLoadingDashboard] = useState(true);
  const [ticketCount, setTicketCount] = useState(0);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const [isLoggedIn, setIsLoggedIn] = React.useState(authService.isLoggedIn());
  const [role, setRole] = React.useState(authService.getRole());
  const [username, setUsername] = React.useState(authService.getUsername());
  const [email, setEmail] = React.useState(authService.getEmail());
  
  React.useEffect(() => {
    const onAuth = () => {
      setIsLoggedIn(authService.isLoggedIn());
      setRole(authService.getRole());
      setUsername(authService.getUsername());
      setEmail(authService.getEmail());
    };
    window.addEventListener('auth-changed', onAuth);
    return () => window.removeEventListener('auth-changed', onAuth);
  }, []);
  
  const menuItems = React.useMemo(() => {
    const common = [
      { id: 'dashboard', label: 'Dashboard', icon: DashboardIcon, color: '#3b82f6', path: '/', tabIndex: 0 },
      { id: 'tickets', label: 'Tickets', icon: TicketIcon, color: '#10b981', badge: ticketCount, path: '/tickets' },
      { id: 'chat', label: 'AI Chat', icon: ChatIcon, color: '#06b6d4', path: '/chat' },
    ];
    const adminOnly = [
      { id: 'category1', label: 'Hardware & Infrastructure', icon: Computer, color: '#3b82f6', path: '/', tabIndex: 1 },
      { id: 'category2', label: 'Software & Digital Services', icon: BugReport, color: '#10b981', path: '/', tabIndex: 2 },
      { id: 'category3', label: 'Access & Security', icon: Security, color: '#f59e0b', path: '/', tabIndex: 3 },
      { id: 'users', label: 'Users', icon: PeopleIcon, color: '#f59e0b', path: '/users' },
      { id: 'settings', label: 'Settings', icon: SettingsIcon, color: '#6b7280', path: '/settings' },
    ];
    const authOptions = [
      { id: 'login', label: 'Login', icon: PersonIcon, color: '#06b6d4', path: '/login' },
      { id: 'signup', label: 'Sign up', icon: PersonIcon, color: '#06b6d4', path: '/signup' },
    ];
    
    if (!isLoggedIn) return authOptions.concat(common);
    return role === 'admin' ? common.concat(adminOnly) : common;
  }, [isLoggedIn, role, ticketCount]);

  // Dynamic stats based on dashboard data
  const stats = dashboardData ? [
    { 
      title: 'Total Tickets', 
      value: dashboardData.stats.total_tickets.toLocaleString(), 
      change: '+12%', 
      icon: Assignment, 
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      progress: 85
    },
    { 
      title: 'Open Tickets', 
      value: dashboardData.stats.open_tickets.toLocaleString(), 
      change: '+5%', 
      icon: Schedule, 
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      progress: 65
    },
    { 
      title: 'Resolved Today', 
      value: dashboardData.stats.resolved_today.toLocaleString(), 
      change: '+23%', 
      icon: CheckCircle, 
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      progress: 92
    },
    { 
      title: 'Avg Response Time', 
      value: `${dashboardData.stats.avg_response_time_hours}h`, 
      change: '-8%', 
      icon: SpeedIcon, 
      gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
      progress: 78
    },
  ] : [];

  // Dynamic recent tickets based on dashboard data
  const recentTickets = dashboardData ? dashboardData.recent_tickets : [];

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
  const navigate = useNavigate();
  const currentPath = location.pathname;
  
  // Find active section based on path and current tab
  const getActiveSection = React.useCallback((path) => {
    if (path === '/') {
      // For the main page, determine active section based on current tab
      switch (activeTab) {
        case 0: return 'dashboard';
        case 1: return 'category1';
        case 2: return 'category2';
        case 3: return 'category3';
        default: return 'dashboard';
      }
    }
    const item = menuItems.find(item => item.path === path);
    return item ? item.id : 'dashboard';
  }, [menuItems, activeTab]);
  
  const [activeSection, setActiveSection] = useState(getActiveSection(currentPath));
  
  // Update active section when location changes or tab changes
  React.useEffect(() => {
    setActiveSection(getActiveSection(currentPath));
  }, [currentPath, getActiveSection, activeTab]);
  
  const handleMenuClick = (item) => {
    setActiveSection(item.id);
    
    // If the item has a tabIndex, switch to that tab instead of navigating
    if (item.tabIndex !== undefined) {
      setActiveTab(item.tabIndex);
      navigate('/'); // Ensure we're on the main page
    } else {
      navigate(item.path);
    }
    
    setMobileOpen(false); // Close drawer on mobile
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    // Reload dashboard data when switching to Dashboard tab
    if (newValue === 0) {
      loadDashboardData();
    }
  };

  // Function to handle AI responses from category tabs
  const handleCategoryResponse = (response) => {
    const aiResponse = {
      text: response,
      sender: 'ai',
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, aiResponse]);
  };

  // Load dashboard data
  const loadDashboardData = async () => {
    try {
      setIsLoadingDashboard(true);
      console.log('Loading dashboard data...');
      
      // Get user email from localStorage
      const userEmail = authService.getEmail();
      console.log('User email for dashboard:', userEmail);
      
      if (!userEmail) {
        console.warn('No user email found, using fallback data');
        setDashboardData({
          stats: {
            total_tickets: 0,
            open_tickets: 0,
            resolved_today: 0,
            avg_response_time_hours: 0
          },
          recent_tickets: []
        });
        setTicketCount(0);
        return;
      }
      
      const data = await apiService.getDashboardData(userEmail);
      console.log('Dashboard data loaded:', data);
      setDashboardData(data);
      setTicketCount(data.stats.total_tickets || 0);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      // Set fallback data
      setDashboardData({
        stats: {
          total_tickets: 0,
          open_tickets: 0,
          resolved_today: 0,
          avg_response_time_hours: 0
        },
        recent_tickets: []
      });
      setTicketCount(0);
    } finally {
      setIsLoadingDashboard(false);
    }
  };

  // Handle ticket resolution
  const handleResolveTicket = async (ticketId) => {
    try {
      const userEmail = authService.getEmail();
      if (!userEmail) {
        console.error('No user email found for ticket resolution');
        return;
      }
      
      await apiService.resolveTicket(ticketId, userEmail);
      // Reload dashboard data to update stats
      await loadDashboardData();
      
      // Add success message to AI chat
      const successMessage = {
        text: `✅ Ticket ${ticketId} has been marked as resolved! The "Resolved Today" counter has been updated.`,
        sender: 'ai',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, successMessage]);
    } catch (error) {
      console.error('Error resolving ticket:', error);
      const errorMessage = {
        text: `❌ Error resolving ticket: ${error.message}`,
        sender: 'ai',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  // Load dashboard data on component mount
  React.useEffect(() => {
    console.log('Component mounted, loading dashboard data...');
    loadDashboardData();
  }, []);

  // Debug: Log when dashboardData changes
  React.useEffect(() => {
    console.log('Dashboard data updated:', dashboardData);
  }, [dashboardData]);
  
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
  const [linkedTicketId, setLinkedTicketId] = useState(() => localStorage.getItem('last_ticket_id') || null);
  const [isDashboardPolling, setIsDashboardPolling] = useState(false);
  const messagesEndRef = React.useRef(null);
  
  // Scroll to bottom of messages
  React.useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // If a ticket is linked, poll its messages so agent replies appear here
  React.useEffect(() => {
    if (!linkedTicketId) return;
    let stop = false;
    setIsDashboardPolling(true);
    let interval;
    const fetchTicketMessages = async () => {
      try {
        const api = await import('./services/apiService.js');
        const data = await api.getTicket(linkedTicketId);
        const mapped = (data.chat_messages || []).map(m => ({
          text: m.content,
          sender: m.sender_type === 'user' ? 'user' : 'ai',
          timestamp: m.timestamp
        }));
        setMessages(prev => (mapped.length ? mapped : prev));
      } catch (e) {
        const status = e?.response?.status;
        if (status === 404) {
          try { localStorage.removeItem('last_ticket_id'); } catch {}
          setLinkedTicketId(null);
          setIsDashboardPolling(false);
          if (interval) clearInterval(interval);
          stop = true;
        }
      }
    };
    fetchTicketMessages();
    interval = setInterval(() => { if (!stop) fetchTicketMessages(); }, 5000);
    return () => { stop = true; if (interval) clearInterval(interval); setIsDashboardPolling(false); };
  }, [linkedTicketId]);
  
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
      // Import the API service
      const { classifyMessage } = await import('./services/apiService.js');
      
      // Classify the message
      const userInfo = {
        user_id: 'user_123',
        user_name: authService.getUsername() || 'User',
        user_email: authService.getEmail() || 'user@example.com'
      };
      
      const response = await classifyMessage(message, userInfo);
      // Remember the ticket so dashboard chat can reflect agent responses
      if (response.ticket_id) {
        localStorage.setItem('last_ticket_id', response.ticket_id);
        setLinkedTicketId(response.ticket_id);
      }
      
      // Add AI response
      const aiResponse = {
        text: `I've classified your query as: ${response.category} with ${response.priority} priority. Redirecting you to the appropriate dashboard...`,
        sender: 'ai',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiResponse]);
      
      // Redirect based on classification
      setTimeout(() => {
        if (response.category === 'Hardware & Infrastructure') {
          navigate('/category1');
        } else if (response.category === 'Software & Digital Services') {
          navigate('/category2');
        } else if (response.category === 'Access & Security') {
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
  
  // Check if current route is auth page
  const isAuthPage = currentPath === '/login' || currentPath === '/signup';

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#f8fafc' }}>
      {/* App Bar - only show for non-auth pages */}
      {!isAuthPage && (
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
          
          <Box sx={{ flex: 1 }} />

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {isLoggedIn ? (
              <>
                <Button 
                  variant="outlined"
                  sx={{
                    borderRadius: '20px',
                    textTransform: 'none',
                    fontWeight: 600,
                    borderColor: '#3b82f6',
                    color: '#1e40af',
                    bgcolor: 'white',
                    px: 2
                  }}
                >
                  {username || (role === 'admin' ? 'Admin' : 'User')} • {email}
                </Button>
                <Button
                  variant="contained"
                  onClick={() => { authService.logout(); navigate('/login'); }}
                  sx={{
                    borderRadius: '20px',
                    textTransform: 'none',
                    fontWeight: 600,
                    px: 2,
                    background: 'linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)'
                  }}
                >
                  Logout
                </Button>
              </>
            ) : (
              <Button
                variant="outlined"
                onClick={() => navigate('/login')}
                sx={{
                  borderRadius: '20px',
                  textTransform: 'none',
                  fontWeight: 600,
                  borderColor: '#3b82f6',
                  color: '#3b82f6',
                  '&:hover': {
                    borderColor: '#2563eb',
                    backgroundColor: '#eff6ff'
                  }
                }}
              >
                Login
              </Button>
            )}
          </Box>
        </Toolbar>
        </AppBar>
      )}

      {/* Sidebar - only show for non-auth pages */}
      {!isAuthPage && (
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
      )}

      {/* Main Content */}
      <Box
        component="main"
        className="flex-1 p-6"
        sx={{
          width: { md: isAuthPage ? '100%' : `calc(100% - ${drawerWidth}px)` },
          mt: isAuthPage ? '0' : '80px'
        }}
      >
        <Container maxWidth="xl" className="animate-fadeIn">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/tickets" element={<Tickets />} />
            <Route path="/" element={
              <>
                {/* Welcome Header */}
                <Box sx={{ mb: 5, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
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
                      Welcome back, {isLoggedIn ? (username || (role === 'admin' ? 'Admin' : 'User')) : 'Guest'}! 👋
                    </Typography>
                    <Typography variant="h6" sx={{ color: '#64748b', fontWeight: 500 }}>
                      Here's what's happening with your tickets today
                    </Typography>
                  </Box>
                  
                  {/* Refresh Button */}
                  <Button
                    variant="outlined"
                    onClick={loadDashboardData}
                    disabled={isLoadingDashboard}
                    startIcon={isLoadingDashboard ? <CircularProgress size={16} /> : <RefreshIcon />}
                    sx={{
                      borderColor: '#3b82f6',
                      color: '#3b82f6',
                      '&:hover': {
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(59, 130, 246, 0.04)'
                      }
                    }}
                  >
                    {isLoadingDashboard ? 'Refreshing...' : 'Refresh'}
                  </Button>
                </Box>

                {/* Tabbed Interface */}
                <Box sx={{ width: '100%' }}>
                  <Tabs 
                    value={activeTab} 
                    onChange={handleTabChange}
                    sx={{
                      borderBottom: 1,
                      borderColor: 'divider',
                      mb: 3,
                      '& .MuiTab-root': {
                        textTransform: 'none',
                        fontWeight: 600,
                        fontSize: '1rem',
                        minHeight: 48,
                        px: 3
                      }
                    }}
                  >
                    <Tab 
                      label="Dashboard" 
                      icon={<DashboardIcon />} 
                      iconPosition="start"
                      sx={{ 
                        color: activeTab === 0 ? '#3b82f6' : '#64748b',
                        '&.Mui-selected': {
                          color: '#3b82f6'
                        }
                      }}
                    />
                    <Tab 
                      label="Hardware & Infrastructure" 
                      icon={<Computer />} 
                      iconPosition="start"
                      sx={{ 
                        color: activeTab === 1 ? '#3b82f6' : '#64748b',
                        '&.Mui-selected': {
                          color: '#3b82f6'
                        }
                      }}
                    />
                    <Tab 
                      label="Software & Digital Services" 
                      icon={<BugReport />} 
                      iconPosition="start"
                      sx={{ 
                        color: activeTab === 2 ? '#10b981' : '#64748b',
                        '&.Mui-selected': {
                          color: '#10b981'
                        }
                      }}
                    />
                    <Tab 
                      label="Access & Security" 
                      icon={<Security />} 
                      iconPosition="start"
                      sx={{ 
                        color: activeTab === 3 ? '#f59e0b' : '#64748b',
                        '&.Mui-selected': {
                          color: '#f59e0b'
                        }
                      }}
                    />
                  </Tabs>

                  {/* Tab Content */}
                  {activeTab === 0 && (
                    <>

                {/* Statistics Cards */}
                <Grid container spacing={4} sx={{ mb: 6 }}>
                  {isLoadingDashboard ? (
                    // Loading skeleton for stats cards
                    Array.from({ length: 4 }).map((_, index) => (
                      <Grid item xs={12} sm={6} lg={3} key={index}>
                        <Card 
                          className="glass-card"
                          sx={{
                            height: '100%',
                            animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite'
                          }}
                        >
                          <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
                              <Box 
                                sx={{
                                  width: 56,
                                  height: 56,
                                  borderRadius: '16px',
                                  bgcolor: '#e5e7eb'
                                }}
                              />
                              <Box sx={{ width: 40, height: 20, bgcolor: '#e5e7eb', borderRadius: 1 }} />
                            </Box>
                            <Box sx={{ flex: 1 }}>
                              <Box sx={{ width: 80, height: 40, bgcolor: '#e5e7eb', borderRadius: 1, mb: 1 }} />
                              <Box sx={{ width: 120, height: 20, bgcolor: '#e5e7eb', borderRadius: 1, mb: 2 }} />
                              <Box sx={{ width: '100%', height: 6, bgcolor: '#e5e7eb', borderRadius: 3 }} />
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))
                  ) : (
                    stats.map((stat, index) => (
                    <Grid item xs={12} sm={6} lg={3} key={index}>
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
                    ))
                  )}
                </Grid>

                {/* Ticket Classifications */}
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
                    Ticket Classifications
                  </Typography>
                  <TicketClassification />
                </Box>
                
                {/* AI Assistant */}
                <Grid container spacing={4}>
                  <Grid item xs={12} lg={6}>
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
                        
                        {/* Action Buttons */}
                        <Box sx={{ mb: 2, display: 'flex', flexDirection: 'column', gap: 1 }}>
                          {/* Resolved Today Button */}
                          <Button
                              fullWidth
                              variant="contained"
                              onClick={() => {
                                // Get the first open ticket ID for resolution
                                const openTicket = recentTickets.find(t => t.status.toLowerCase() === 'open');
                                if (openTicket) {
                                  handleResolveTicket(openTicket.id);
                                } else {
                                  const errorMessage = {
                                    text: "❌ No open tickets available to resolve.",
                                    sender: 'ai',
                                    timestamp: new Date().toISOString()
                                  };
                                  setMessages(prev => [...prev, errorMessage]);
                                }
                              }}
                              sx={{
                                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                                color: 'white',
                                fontWeight: 600,
                                textTransform: 'none',
                                borderRadius: '12px',
                                py: 1.5,
                                '&:hover': {
                                  background: 'linear-gradient(135deg, #059669 0%, #047857 100%)'
                                }
                              }}
                              startIcon={<CheckCircle sx={{ fontSize: 20 }} />}
                            >
                              Mark Issue as Resolved Today
                            </Button>

                          {/* Satisfaction Buttons */}
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Button
                              variant="contained"
                              onClick={async () => {
                                try {
                                  const userEmail = authService.getEmail();
                                  if (!userEmail) {
                                    console.error('No user email found for satisfaction feedback');
                                    return;
                                  }
                                  
                                  // Get the first open ticket to resolve
                                  const openTicket = recentTickets.find(t => t.status.toLowerCase() === 'open');
                                  if (openTicket) {
                                    // Resolve the ticket
                                    await apiService.resolveTicket(openTicket.id, userEmail);
                                    
                                    // Reload dashboard data to update stats
                                    await loadDashboardData();
                                    
                                    const satisfactionMessage = {
                                      text: `✅ Thank you! Your satisfaction has been recorded and ticket ${openTicket.ticket_number} has been marked as resolved. The "Resolved Today" counter has been updated!`,
                                      sender: 'ai',
                                      timestamp: new Date().toISOString()
                                    };
                                    setMessages(prev => [...prev, satisfactionMessage]);
                                  } else {
                                    const satisfactionMessage = {
                                      text: "✅ Thank you! Your satisfaction has been recorded. This helps us improve our service.",
                                      sender: 'ai',
                                      timestamp: new Date().toISOString()
                                    };
                                    setMessages(prev => [...prev, satisfactionMessage]);
                                  }
                                } catch (error) {
                                  console.error('Error resolving ticket:', error);
                                  const errorMessage = {
                                    text: "✅ Thank you! Your satisfaction has been recorded. This helps us improve our service.",
                                    sender: 'ai',
                                    timestamp: new Date().toISOString()
                                  };
                                  setMessages(prev => [...prev, errorMessage]);
                                }
                              }}
                              sx={{
                                flex: 1,
                                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                                color: 'white',
                                fontWeight: 600,
                                textTransform: 'none',
                                borderRadius: '12px',
                                py: 1,
                                '&:hover': {
                                  background: 'linear-gradient(135deg, #059669 0%, #047857 100%)'
                                }
                              }}
                              startIcon={<CheckCircle sx={{ fontSize: 16 }} />}
                            >
                              Satisfied
                            </Button>
                            <Button
                              variant="outlined"
                              onClick={() => {
                                const dissatisfactionMessage = {
                                  text: "❌ We're sorry to hear that. Your feedback has been recorded and will help us improve our service. Please provide more details about your issue so we can assist you better.",
                                  sender: 'ai',
                                  timestamp: new Date().toISOString()
                                };
                                setMessages(prev => [...prev, dissatisfactionMessage]);
                                console.log('User not satisfied with the response');
                              }}
                              sx={{
                                flex: 1,
                                borderColor: '#ef4444',
                                color: '#ef4444',
                                fontWeight: 600,
                                textTransform: 'none',
                                borderRadius: '12px',
                                py: 1,
                                '&:hover': {
                                  borderColor: '#dc2626',
                                  backgroundColor: 'rgba(239, 68, 68, 0.1)'
                                }
                              }}
                              startIcon={<ErrorIcon sx={{ fontSize: 16 }} />}
                            >
                              Not Satisfied
                            </Button>
                          </Box>
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
                  )}

                  {activeTab === 1 && (
                    <ClassificationOne onCategoryResponse={handleCategoryResponse} />
                  )}

                  {activeTab === 2 && (
                    <ClassificationTwo onCategoryResponse={handleCategoryResponse} />
                  )}

                  {activeTab === 3 && (
                    <ClassificationThree onCategoryResponse={handleCategoryResponse} />
                  )}
                </Box>
              </>
            } />
            {/* Role based dashboards */}
            <Route path="/admin" element={<ProtectedRoute requireRole="admin"><AdminDashboard /></ProtectedRoute>} />
            <Route path="/home" element={<ProtectedRoute><UserDashboard /></ProtectedRoute>} />
            
            {/* Classification Dashboard Routes */}
            <Route path="/category1" element={<ClassificationOne />} />
            <Route path="/category2" element={<ClassificationTwo />} />
            <Route path="/category3" element={<ClassificationThree />} />
            
            {/* AI Chat Route */}
            <Route path="/chat" element={<AIChatPage />} />
            
            {/* Other routes can be added here */}
            <Route path="*" element={<Typography variant="h4">Page Not Found</Typography>} />
          </Routes>
        </Container>
      </Box>
    </Box>
  );
}

export default App;
