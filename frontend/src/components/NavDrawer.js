import React, { useState } from 'react';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import HomeIcon from '@mui/icons-material/Home';
import InfoIcon from '@mui/icons-material/Info';
import ContactMailIcon from '@mui/icons-material/ContactMail';
import GroupIcon from '@mui/icons-material/Group';
import SchoolIcon from '@mui/icons-material/School';
import useMediaQuery from '@mui/material/useMediaQuery';
import MenuIcon from '@mui/icons-material/Menu';
import IconButton from '@mui/material/IconButton';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthProvider'; // assuming you have a useAuth hook to handle JWT and roles

const drawerWidth = 230;

const NavDrawer = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const isSmallScreen = useMediaQuery((theme) => theme.breakpoints.down('sm'));

  // Get user roles from useAuth hook
  const { userRoles } = useAuth(); // This should return an array of roles for the logged-in user

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const hasPermission = (role) => {
    // return userRoles.includes(role); // Check if user has the required role
    //alert(`role:${role}`)
    return userRoles && userRoles.includes(role); // Check if userRoles is defined
  };

  const drawerContent = (
    <List>
      {[
        { text: 'Home', icon: <HomeIcon />, link: '/' },
      ].map((item, index) => (
        <ListItem component={Link} to={item.link} key={index}>
          <ListItemIcon>{item.icon}</ListItemIcon>
          <ListItemText primary={item.text} />
        </ListItem>
      ))}

      {/* Conditionally show Student Management section */}
      {hasPermission('instructor') && (
        <>
          <ListItem>
            <ListItemIcon>
              <SchoolIcon />
            </ListItemIcon>
            <ListItemText primary="Student Management" />
          </ListItem>

          {/* Conditionally show Student Group sub-item */}
          {hasPermission('instructor') && (
            <ListItem component={Link} to="/student-group">
              <ListItemIcon>
                <GroupIcon />
              </ListItemIcon>
              <ListItemText primary="Student Group" />
            </ListItem>
          )}
        </>
      )}
    </List>
  );

  return (
    <>
      <Toolbar>
        {isSmallScreen && (
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
        )}
      </Toolbar>
      <Drawer
        variant={isSmallScreen ? 'temporary' : 'permanent'}
        open={!isSmallScreen || mobileOpen}
        onClose={handleDrawerToggle}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: {
            width: drawerWidth,
            boxSizing: 'border-box',
            marginTop: isSmallScreen ? 0 : '64px',
          },
        }}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile.
        }}
      >
        {drawerContent}
      </Drawer>
    </>
  );
};

export default NavDrawer;
