import React, { useState, useRef } from 'react';
import { Box, Button, TextField, Typography, Link, IconButton, InputAdornment } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';
import { Clear as ClearIcon } from '@mui/icons-material';
import BaseTemplate from './BaseTemplate';
import { triggerToast } from './ToastProvider';
import { useRoutes } from './RoutesContext';
import { useAuth } from './AuthProvider';

const LoginForm = () => {
  const theme = useTheme();
  const { mode } = theme.palette;
  const [userId, setUserId] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const routes = useRoutes();
  const { login } = useAuth();

  // Refs to focus on TextFields
  const userIdRef = useRef(null);
  const passwordRef = useRef(null);

  const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  };

  const handleLogin = async () => {
    // Basic validation
    if (!userId || !password) {
      triggerToast({ type: 'warning', content: 'All fields are required.' }, (mode === 'dark'), false);
      return;
    }
    if (!validateEmail(userId)) {
      triggerToast({ type: 'warning', content: 'Please enter a valid email address.' }, (mode === 'dark'), false);
      return;
    }
    // Submit form
    try {
      const response = await fetch(routes.api.login, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ userId, password }),
      });
    
      const data = await response.json();

      // Check if the response is not OK (status 200-299)
      if (!response.ok) {
        triggerToast({ type: 'critical', content: `${data.message}`, logToBackend: true}, (mode === 'dark'), true);
      } else {
        localStorage.setItem('token', data.access_token);
        login();
        handleHomeNavigation();
        triggerToast({ type: 'info', content: `${data.message}`}, (mode === 'dark'), false);
      }
    } catch (error) {
      triggerToast({ type: 'critical', content: `Login API error: ${error}`,}, (mode === 'dark'), true);
    }
  };
  
  const handleHomeNavigation = () => {
    navigate(routes.home);
  }

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleLogin(); // Trigger login on Enter key press
    }
  };

  const handleForgotPassword = () => {
    // Navigate to the ForgotPasswordForm
    navigate(routes.forgotPassword);
  };

  const handleClear = (setter, ref) => () => {
    setter(''); // Clear the input field
    ref.current.focus();
  };

  return (
    <BaseTemplate>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: 'calc(100vh - 120px)',
        }}
      >
        <Box
          sx={{
            width: '100%',
            maxWidth: '400px',
            padding: '32px',
            backgroundColor: theme.palette.background.paper,
            boxShadow: theme.shadows[3],
            borderRadius: '8px',
          }}
        >
          <Typography variant="h5" sx={{ marginBottom: '16px', textAlign: 'center' }}>
            Login
          </Typography>

          <TextField
            fullWidth
            label="Your ID"
            variant="outlined"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            sx={{ marginBottom: '16px' }}
            inputRef={userIdRef}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={handleClear(setUserId, userIdRef)} edge="end">
                    <ClearIcon />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          <TextField
            fullWidth
            label="Password"
            type="password"
            variant="outlined"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            sx={{ marginBottom: '16px' }}
            onKeyPress={handleKeyPress} // Add onKeyPress event
            inputRef={passwordRef}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={handleClear(setPassword, passwordRef)} edge="end">
                    <ClearIcon />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          <Button
            fullWidth
            variant="contained"
            color="primary"
            onClick={handleLogin}
            sx={{ marginBottom: '16px' }}
          >
            Login
          </Button>

          <Link
            href="#"
            onClick={handleForgotPassword}
            underline="hover"
            sx={{ display: 'block', textAlign: 'center' }}
          >
            Forgot Password?
          </Link>
        </Box>
      </Box>
    </BaseTemplate>
  );
};

export default LoginForm;
