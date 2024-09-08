import React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import CancelIcon from '@mui/icons-material/Cancel';
import SaveIcon from '@mui/icons-material/Save';
import CloseIcon from '@mui/icons-material/Close';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme } from '@mui/material/styles';

const FooterActions = ({ canDelete, canEdit, onDelete, onCancel, onSave }) => {
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Box
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        width: '100%',
        backgroundColor: 'white',
        zIndex: 100,
        boxShadow: '0px -1px 10px rgba(0, 0, 0, 0.1)',
        padding: '8px 16px',
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'flex-end',
        alignItems: 'center',
        gap: '16px',
      }}
    >
      {canDelete && (
        <Button
          variant="contained"
          color="error"
          startIcon={<DeleteForeverIcon />}
          onClick={onDelete}
          sx={{
            minWidth: isSmallScreen ? 'auto' : '120px',
            padding: isSmallScreen ? '6px' : '8px 16px',
          }}
        >
          {!isSmallScreen && 'Delete'}
        </Button>
      )}
      {/* Add a dump space between Delete and Cancel buttons */}
      {canDelete && <Box sx={{ width: '65%' }} />}
      {canEdit && (
        <Button
          variant="outlined"
          color="primary"
          startIcon={<CancelIcon />}
          onClick={onCancel}
          sx={{
            minWidth: isSmallScreen ? 'auto' : '120px',
            padding: isSmallScreen ? '6px' : '8px 16px',
          }}
        >
          {!isSmallScreen && 'Cancel'}
        </Button>
      )}
      <Button
        variant="contained"
        color="primary"
        startIcon={canEdit ? <SaveIcon /> : <CloseIcon />}
        onClick={onSave}
        sx={{
          minWidth: isSmallScreen ? 'auto' : '120px',
          padding: isSmallScreen ? '6px' : '8px 16px',
        }}
      >
        {!isSmallScreen && (canEdit ? 'Save' : 'Close')}
      </Button>
    </Box>
  );
};

export default FooterActions;
