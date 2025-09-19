import React, { useState } from 'react';
import { Box, Card, CardContent, TextField, Button, Typography, Alert, MenuItem, InputAdornment, IconButton } from '@mui/material';
import { Email, Lock, AdminPanelSettings, Person, Visibility, VisibilityOff, FlightTakeoff } from '@mui/icons-material';
import authService from '../services/authService';
import { useNavigate } from 'react-router-dom';

const Signup = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('end_user');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [show, setShow] = useState(false);

  const onSubmit = async () => {
    setError(''); setLoading(true);
    try {
      await authService.signup({ username, email, password, role });
      // Auto-login then go to dashboard
      await authService.login({ email, password });
      navigate('/');
    } catch (e) {
      setError('Username or email already registered');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      minHeight: '100vh',
      backgroundImage: 'url("https://blog.vsoftconsulting.com/hs-fs/hubfs/Grid-system_1196-x-2100.jpg?width=1110&name=Grid-system_1196-x-2100.jpg")',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat'
    }}>
      {/* Left side - Promotional banner */}
      <Box sx={{ 
        flex: 1, 
        display: { xs: 'none', md: 'flex' },
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        color: 'white',
        p: 4,
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.4)',
          zIndex: 1
        }
      }}>
        <Typography variant="h2" sx={{ 
          fontWeight: 700, 
          mb: 2,
          textAlign: 'center',
          background: 'linear-gradient(45deg, #ffffff 30%, #e0e7ff 90%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          position: 'relative',
          zIndex: 2
        }}>
          POWERGRID
        </Typography>
        <Typography variant="h5" sx={{ 
          textAlign: 'center',
          opacity: 0.9,
          maxWidth: 400,
          lineHeight: 1.6,
          position: 'relative',
          zIndex: 2
        }}>
          AI-powered ticketing system that transforms IT support into intelligent, automated solutions
        </Typography>
      </Box>

      {/* Right side - Signup form */}
      <Box sx={{ 
        flex: { xs: 1, md: 0.6 },
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 3,
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)'
      }}>
        <Card sx={{ 
          width: '100%', 
          maxWidth: 400,
          boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
          borderRadius: 3,
          border: '1px solid rgba(255,255,255,0.2)'
        }}>
          <CardContent sx={{ p: 4 }}>
            {/* Header with airplane icon */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Box>
                <Typography variant="h4" sx={{ 
                  fontWeight: 700, 
                  color: '#1e40af',
                  mb: 0.5
                }}>
                  Create Account
                </Typography>
                <Typography variant="body2" sx={{ color: '#64748b' }}>
                  Sign up with your details
                </Typography>
              </Box>
              <FlightTakeoff sx={{ 
                color: '#3b82f6', 
                fontSize: 32,
                transform: 'rotate(45deg)'
              }} />
            </Box>

            {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

            <TextField
              fullWidth
              label="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              sx={{ mb: 3 }}
              InputProps={{ 
                startAdornment: (<InputAdornment position="start"><Person sx={{ color: '#9ca3af' }} /></InputAdornment>) 
              }}
            />

            <TextField
              fullWidth
              label="Email Id"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              sx={{ mb: 3 }}
              InputProps={{ 
                startAdornment: (<InputAdornment position="start"><Email sx={{ color: '#9ca3af' }} /></InputAdornment>) 
              }}
            />

            <TextField
              fullWidth
              label="Password"
              type={show ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              sx={{ mb: 3 }}
              InputProps={{
                startAdornment: (<InputAdornment position="start"><Lock sx={{ color: '#9ca3af' }} /></InputAdornment>),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShow(!show)} size="small">
                      {show ? <VisibilityOff sx={{ color: '#9ca3af' }} /> : <Visibility sx={{ color: '#9ca3af' }} />}
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />

            <TextField
              select
              fullWidth
              label="Role"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              sx={{ mb: 3 }}
              InputProps={{ 
                startAdornment: (<InputAdornment position="start"><AdminPanelSettings sx={{ color: '#9ca3af' }} /></InputAdornment>) 
              }}
            >
              <MenuItem value="end_user">User</MenuItem>
              <MenuItem value="admin">Admin</MenuItem>
            </TextField>

            <Button 
              fullWidth 
              variant="contained" 
              onClick={onSubmit} 
              disabled={loading || !username || !email || !password}
              sx={{
                py: 1.5,
                mb: 2,
                background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                borderRadius: 2,
                textTransform: 'uppercase',
                fontWeight: 600,
                fontSize: '0.9rem',
                '&:hover': {
                  background: 'linear-gradient(135deg, #2563eb 0%, #1e40af 100%)',
                }
              }}
            >
              {loading ? 'Creating Account...' : 'SIGN UP'}
            </Button>

            <Typography variant="body2" sx={{ textAlign: 'center', color: '#64748b' }}>
              Already have an account?{' '}
              <Button 
                variant="text" 
                onClick={() => navigate('/login')}
                sx={{ 
                  color: '#3b82f6', 
                  textTransform: 'none',
                  fontWeight: 600,
                  p: 0,
                  minWidth: 'auto'
                }}
              >
                Login
              </Button>
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default Signup;


