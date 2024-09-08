import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';

const MyAppBar = ({ onMenuClick }) => (
  <AppBar    
    position="fixed"
    sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
    }}
  >
    <Toolbar>
      <Typography variant="h6">
        My Application
      </Typography>
    </Toolbar>
  </AppBar>
);

export default MyAppBar;
