import React, { useState } from 'react';
import { Box, Card, CardContent, TextField, Button, Typography, Alert, MenuItem, InputAdornment } from '@mui/material';
import { Email, Lock, AdminPanelSettings } from '@mui/icons-material';
import authService from '../services/authService';
import { useNavigate } from 'react-router-dom';

const Signup = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('end_user');
  const [error, setError] = useState('');
  const [ok, setOk] = useState('');
  const [loading, setLoading] = useState(false);

  const onSubmit = async () => {
    setError(''); setOk(''); setLoading(true);
    try {
      await authService.signup({ email, password, role });
      setOk('Account created. You can login now.');
      setTimeout(() => navigate('/login'), 800);
    } catch (e) {
      setError('Email already registered');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', background: 'linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%)' }}>
      <Card sx={{ width: 420 }}>
        <CardContent>
          <Typography variant="h5" sx={{ mb: 2, fontWeight: 700 }}>Create account</Typography>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          {ok && <Alert severity="success" sx={{ mb: 2 }}>{ok}</Alert>}
          <TextField fullWidth label="Email" value={email} onChange={(e)=>setEmail(e.target.value)} sx={{ mb: 2 }} InputProps={{ startAdornment:(<InputAdornment position="start"><Email/></InputAdornment>) }} />
          <TextField fullWidth label="Password" type="password" value={password} onChange={(e)=>setPassword(e.target.value)} sx={{ mb: 2 }} InputProps={{ startAdornment:(<InputAdornment position="start"><Lock/></InputAdornment>) }} />
          <TextField select fullWidth label="Role" value={role} onChange={(e)=>setRole(e.target.value)} sx={{ mb: 2 }} InputProps={{ startAdornment:(<InputAdornment position="start"><AdminPanelSettings/></InputAdornment>) }}>
            <MenuItem value="end_user">User</MenuItem>
            <MenuItem value="admin">Admin</MenuItem>
          </TextField>
          <Button fullWidth variant="contained" onClick={onSubmit} disabled={loading || !email || !password}>Sign up</Button>
          <Button fullWidth sx={{ mt: 1 }} onClick={() => navigate('/login')}>Back to login</Button>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Signup;


