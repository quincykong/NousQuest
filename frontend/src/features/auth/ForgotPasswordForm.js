import React, { useState, useRef } from 'react';
import { Box, Button, TextField, Typography, Link, IconButton, InputAdornment } from '@mui/material';
import { Clear as ClearIcon } from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import BaseTemplate from '../../components/BaseTemplate';
import { triggerToast } from '../../components/ToastProvider';
import { useRoutes } from '../../contexts/RoutesContext';

const ForgotPasswordForm = () => {
  const theme = useTheme();
  const [email, setEmail] = useState('');
  const routes = useRoutes();

  const emailRef = useRef(null);

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleResetPassword();
    }
  };

  const handleClear = (setter, ref) => () => {
    setter(''); // Clear the input field
    ref.current.focus(); // Set focus back to the input field
  };

  const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  };

  const handleResetPassword = async () => {
    if (email) {
      if (!validateEmail(email)) {
        triggerToast({ type: 'warning', content: 'Please enter a valid email address.' });
        return;
      }
      try{
        const response = await fetch(routes.api.resetPassword, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
        })
          .then(response => {
            if (response.ok) {
              triggerToast({ type: 'info', content: 'Reset link sent to your email' });
            } else {
              triggerToast({ type: 'critical', content: 'Failed to send reset link' });
            }
          })
          .catch(error => {
            triggerToast({ type: 'critical', content: 'An error occurred' });
          });
        } catch (error) {
          triggerToast({type: 'critial', content: 'Error login API: '+ error + '.'})
        }
    } else {
      triggerToast({ type: 'warning', content: 'Please enter your email address' });
    }
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
            maxWidth: '600px',
            padding: '32px',
            backgroundColor: theme.palette.background.paper,
            boxShadow: theme.shadows[3],
            borderRadius: '8px',
          }}
        >
          <Typography variant="h5" sx={{ marginBottom: '16px', textAlign: 'center' }}>
            Reset Password
          </Typography>

          <TextField
            fullWidth
            label="Email Address"
            variant="outlined"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            sx={{ marginBottom: '16px' }}
            onKeyPress={handleKeyPress}
            inputRef={emailRef} // Attach ref to TextField
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={handleClear(setEmail, emailRef)} edge="end">
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
            onClick={handleResetPassword}
            sx={{ marginBottom: '16px' }}
          >
            Reset Password
          </Button>

          <Link
            href={routes.home}
            underline="hover"
            sx={{ display: 'block', textAlign: 'center' }}
          >
            Back to Login
          </Link>
        </Box>
      </Box>
    </BaseTemplate>
  );
};

export default ForgotPasswordForm;
