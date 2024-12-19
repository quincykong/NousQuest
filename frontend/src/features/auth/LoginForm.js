import React, { useState, useRef, useEffect } from 'react';
import { Box, Button, TextField, Typography, Link, IconButton, InputAdornment } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';
import { Clear as ClearIcon } from '@mui/icons-material';
import BaseTemplate from '../../components/BaseTemplate';
import { triggerToast } from '../../components/ToastProvider';
import { useRoutes } from '../../contexts/RoutesContext';
import { useAuth } from '../../contexts/AuthProvider';

const LoginForm = () => {
  const theme = useTheme();
  const { mode } = theme.palette;
  const [userId, setUserId] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false); // Added loading state
  const navigate = useNavigate();
  const routes = useRoutes();
  const { login } = useAuth();

  // Refs to focus on TextFields
  const userIdRef = useRef(null);
  const passwordRef = useRef(null);

  useEffect(() => {
    if (userIdRef.current) {
      userIdRef.current.focus();  // Automatically focus the User ID field
    }
  }, []);

  const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  };

  const handleLogin = async () => {
    if (loading) return; // Prevent multiple submissions
    // Basic validation
    if (!userId || !password) {
      triggerToast({ type: 'warning', content: 'All fields are required.' }, (mode === 'dark'), false);
      return;
    }
    if (!validateEmail(userId)) {
      triggerToast({ type: 'warning', content: 'Please enter a valid email address.' }, (mode === 'dark'), false);
      return;
    }

    // call the login function form AuthProvider
    try {
      setLoading(true);
      const success = await login(userId, password);      
      if (success) {
        triggerToast({ type: 'success', content: `Welcome back!` }, (mode === 'dark'), false);
        navigate(routes.defaultHOME);
      } else {
        triggerToast({ type: 'warning', content: 'Invalid credentials. Please try again.' }, (mode === 'dark'), false);
      }
      } catch (error) {
        triggerToast({ type: 'critical', content: `Login API error: ${error.message}` }, (mode === 'dark'), true);
      } finally {
        setLoading(false);  // Reset loading state
      }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleLogin(); // trigger login on Enter key press
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
                  <IconButton onClick={handleClear(setUserId, userIdRef)} edge="end" tabIndex={-1} disableRipple>
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
                  <IconButton onClick={handleClear(setPassword, passwordRef)} edge="end" tabIndex={-1} disableRipple>
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
            disabled={loading} // Disable the button while loading
            sx={{ marginBottom: '16px' }}
          >
            {loading ? 'Logging in...' : 'Login'}
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
