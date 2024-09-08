import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Toolbar from '@mui/material/Toolbar';

const drawerWidth = 240;
const ContentArea = () => (
  <Box
    component="main"
    sx={{ flexGrow: 1, bgcolor: 'background.default', p: 3, marginLeft: drawerWidth }}
  >
    <Toolbar />
    <Typography paragraph>
      This is the main content area.
    </Typography>
  </Box>
);

export default ContentArea;
