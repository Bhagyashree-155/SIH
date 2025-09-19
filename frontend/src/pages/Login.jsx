import React, { useState } from 'react';
import { Box, Card, CardContent, TextField, Button, Typography, Alert, InputAdornment, IconButton } from '@mui/material';
import { Visibility, VisibilityOff, Lock, Email } from '@mui/icons-material';
import authService from '../services/authService';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [show, setShow] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const onSubmit = async () => {
    setError('');
    setLoading(true);
    try {
      await authService.login({ email, password });
      navigate('/');
    } catch (e) {
      setError('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', background: 'linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%)' }}>
      <Card sx={{ width: 420 }}>
        <CardContent>
          <Typography variant="h5" sx={{ mb: 2, fontWeight: 700 }}>Login</Typography>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <TextField
            fullWidth
            label="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            sx={{ mb: 2 }}
            InputProps={{ startAdornment: (<InputAdornment position="start"><Email /></InputAdornment>) }}
          />
          <TextField
            fullWidth
            label="Password"
            type={show ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            sx={{ mb: 2 }}
            InputProps={{
              startAdornment: (<InputAdornment position="start"><Lock /></InputAdornment>),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setShow(!show)}>{show ? <VisibilityOff /> : <Visibility />}</IconButton>
                </InputAdornment>
              )
            }}
          />
          <Button fullWidth variant="contained" onClick={onSubmit} disabled={loading || !email || !password}>Login</Button>
          <Button fullWidth sx={{ mt: 1 }} onClick={() => navigate('/signup')}>Create account</Button>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Login;


