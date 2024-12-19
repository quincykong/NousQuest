import { React, useEffect, useContext } from 'react';
import { Navigate } from 'react-router-dom'; // Use Navigate instead of Redirect in React Router v6
import { Box, Typography, CircularProgress } from '@mui/material';
import { AuthContext } from '../contexts/AuthProvider';
import BaseTemplate from '../components/BaseTemplate'; // Assuming you are using BaseTemplate

const HomePage = () => {
  const { isAuthenticated, authorizationsLoaded } = useContext(AuthContext);

  // useEffect(() => {
  //   console.log('HomePage: authorizationsLoaded is:', authorizationsLoaded);
  // }, [authorizationsLoaded]);

  // If the user is not authenticated, redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  // Show a loading indicator while waiting for authorizations to load
  if (!authorizationsLoaded) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  // If authenticated and authorizations are loaded, render the home page
  return (
    <BaseTemplate showNav={true}>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Welcome to the Home Page!
        </Typography>
        <Typography variant="body1">
          This is a temporary home page. Feel free to explore the navigation on the left.
        </Typography>
      </Box>
    </BaseTemplate>
  );
};

export default HomePage;
