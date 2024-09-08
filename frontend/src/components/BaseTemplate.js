import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import MyAppBar from './MyAppBar';
import NavDrawer from './NavDrawer';
import { ToastProvider } from './ToastProvider';

const drawerWidth = 240;

const BaseTemplate = ({ children, showNav = false }) => {
  const [drawerOpen, setDrawerOpen] = useState(showNav);
  const theme = useTheme();
  const isSmallScreen = useMediaQuery((theme) => theme.breakpoints.down('sm'));

  const handleMenuClick = () => {
    setDrawerOpen(!drawerOpen);
  };

  return (
    <ToastProvider>
      <Box sx={{ display: 'flex', height: '100vh' }}>
        <MyAppBar onMenuClick={handleMenuClick} />
        {showNav && (
          <NavDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} />
        )}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            width: '100%', 
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'left',
          }}
        >
          <Toolbar /> {/* Push content below the AppBar */}
          <Box
            sx={{
              width: '100%',
              flexGrow: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'left',
            }}
          >
            {children}
          </Box>
        </Box>
      </Box>
    </ToastProvider>
  );
};

export default BaseTemplate;
