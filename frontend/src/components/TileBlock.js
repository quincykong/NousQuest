import React, { useState } from 'react';
import { Box, Typography, IconButton, Divider, Collapse, useMediaQuery } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import { useTheme } from '@mui/material/styles';

const TileBlock = ({
  title,
  children,
  icon,
  collapsible = true,
  initialCollapsed = false,
  backgroundColor,
  textColor,
  inheritTheme = true
}) => {
  const [collapsed, setCollapsed] = useState(initialCollapsed);
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  const handleToggleCollapse = () => {
    if (collapsible) {
      setCollapsed(!collapsed);
    }
  };

  const tileStyles = {
    backgroundColor: backgroundColor || (inheritTheme ? 'inherit' : theme.palette.background.default),
    color: textColor || (inheritTheme ? 'inherit' : theme.palette.text.primary),
    padding: isSmallScreen ? '8px' : '16px',
    borderRadius: '8px',
    boxShadow: theme.shadows[1],
    marginBottom: '16px',
    border: `1px solid ${theme.palette.mode === 'dark' ? theme.palette.grey[700] : theme.palette.grey[300]}`, // Conditional border color
  };

  const titleBarStyles = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    cursor: collapsible ? 'pointer' : 'default',
  };

  const titleWithIconStyles = {
    display: 'flex',
    alignItems: 'center',
  };

  return (
    <Box style={tileStyles}>
      <Box
        style={titleBarStyles}
        onClick={handleToggleCollapse}
        aria-expanded={!collapsed}
        aria-controls="tile-content"
        role="button"
        tabIndex={0}
      >
        <Box style={titleWithIconStyles}>
          {icon && <Box mr={1}>{icon}</Box>} {/* Display icon if provided */}
          <Typography variant="h6" component="div">{title}</Typography>
        </Box>
        {collapsible && (
          <IconButton
            onClick={handleToggleCollapse}
            aria-label={collapsed ? 'Expand' : 'Collapse'}
            size="small"
          >
            {collapsed ? <ExpandMoreIcon /> : <ExpandLessIcon />}
          </IconButton>
        )}
      </Box>
      <Divider />
      <Collapse in={!collapsed}>
        <Box id="tile-content" mt={2}>
          {children}
        </Box>
      </Collapse>
    </Box>
  );
};

//export default React.memo(TileBlock);
export default TileBlock;