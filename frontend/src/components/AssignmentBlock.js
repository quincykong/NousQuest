import React, { useState, useEffect, useCallback } from 'react';
import { Box, Button, List, ListItem, ListItemText, TextField, Paper, IconButton, InputAdornment, CircularProgress, Dialog, DialogTitle, DialogActions, Typography } from '@mui/material';
import KeyboardDoubleArrowLeftIcon from '@mui/icons-material/KeyboardDoubleArrowLeft';
import KeyboardDoubleArrowRightIcon from '@mui/icons-material/KeyboardDoubleArrowRight';
import ClearIcon from '@mui/icons-material/Clear';
import { useTheme } from '@mui/material/styles';
import { toast } from 'react-toastify';

const AssignmentBlock = ({
  assignedItems,
  availableItems,
  onAssign,
  onRemove,
  removableItems,
  leftLimit = 0,  // upper limit on left-hand side list with default 0 (unlimited)
  leftTitle,
  rightTitle
}) => {
  const [assigned, setAssigned] = useState(assignedItems);
  const [available, setAvailable] = useState(availableItems);
  const [assignedFilter, setAssignedFilter] = useState('');
  const [availableFilter, setAvailableFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [moveDirection, setMoveDirection] = useState(null);
  const theme = useTheme();

  useEffect(() => {
    // Simulate data fetching
    setTimeout(() => setLoading(false), 1000);
  }, []);

  const handleMoveRight = useCallback(() => {
    const newAvailable = [...available, ...assigned.filter(item => removableItems.includes(item.id))];
    const newAssigned = assigned.filter(item => !removableItems.includes(item.id));
    setAssigned(newAssigned);
    setAvailable(newAvailable);
    onRemove(newAssigned);
    onAssign(newAvailable);
  }, [assigned, available, onRemove, onAssign, removableItems]);

  const handleMoveLeft = useCallback(() => {
    const totalItemsToMove = available.length;
    const remainingSpace = leftLimit - assigned.length;

    if (leftLimit && totalItemsToMove > remainingSpace) {
      toast.error("Insufficient availability items to move all");
      return;
    }

    const newAssigned = [...assigned, ...available];
    setAssigned(newAssigned);
    setAvailable([]);
    onAssign(newAssigned);
    onRemove([]);
  }, [available, assigned, leftLimit, onAssign, onRemove]);

  const handleMoveItem = useCallback((item, direction) => {
    if (direction === 'right') {
      if (removableItems.includes(item.id)) {
        const updatedAssigned = assigned.filter(i => i.id !== item.id);
        const updatedAvailable = [...available, item];
        setAssigned(updatedAssigned);
        setAvailable(updatedAvailable);
        onRemove(updatedAssigned);
        onAssign(updatedAvailable);
      }
    } else {
      if (leftLimit && assigned.length >= leftLimit) {
        toast.error("Cannot add more items, limit reached");
        return;
      }

      const updatedAvailable = available.filter(i => i.id !== item.id);
      const updatedAssigned = [...assigned, item];
      setAvailable(updatedAvailable);
      setAssigned(updatedAssigned);
      onAssign(updatedAssigned);
      onRemove(updatedAvailable);
    }
  }, [assigned, available, removableItems, onAssign, onRemove, leftLimit]);

  const handleMove = useCallback((direction) => {
    if (direction === 'left') {
      handleMoveLeft();
    } else if (direction === 'right') {
      handleMoveRight();
    }
  }, [handleMoveLeft, handleMoveRight]);

  const handleKeyDown = useCallback((e, item, direction) => {
    if (e.key === 'Enter') {
      handleMoveItem(item, direction);
    }
  }, [handleMoveItem]);

  const filterItems = useCallback((items, filter) => items.filter(item => item.name.toLowerCase().includes(filter.toLowerCase())), []);

  const handleConfirmMoveAll = useCallback((direction) => {
    if (direction === 'left') {
      const totalItemsToMove = available.length;
      const remainingSpace = leftLimit - assigned.length;

      if (leftLimit && totalItemsToMove > remainingSpace) {
        toast.error("Insufficient availability items to move all");
        return;
      }
    }
    setConfirmOpen(true);
    setMoveDirection(direction);
  }, [available.length, leftLimit, assigned.length]);

  const handleConfirmClose = useCallback(() => {
    setConfirmOpen(false);
  }, []);

  if (loading) {
    return <CircularProgress />;
  }

  return (
    <Box display="flex" alignItems="stretch"> {/* Aligning the boxes horizontally and stretching their heights */}
      <Dialog
        open={confirmOpen}
        onClose={handleConfirmClose}
        aria-labelledby="confirm-move-dialog-title"
        sx={{ '& .MuiDialog-paper': { width: '400px', maxWidth: 'none' } }} // Customize the width here
      >
        <DialogTitle id="confirm-move-dialog-title">{"Move all items?"}</DialogTitle>
        <DialogActions>
          <Button onClick={() => { handleMove(moveDirection); handleConfirmClose(); }} color="primary">
            Yes
          </Button>
          <Button onClick={handleConfirmClose} color="primary" autoFocus>
            No
          </Button>
        </DialogActions>
      </Dialog>
      <Paper style={{ padding: 16, width: '40%', marginRight: 16, display: 'flex', flexDirection: 'column', flex: 1 }}>
        <Typography variant="h6" gutterBottom>
          {leftTitle}: {assigned.length}{leftLimit ? ` of ${leftLimit}` : ''} {/* Show count and limit */}
        </Typography>
        <TextField
          fullWidth
          label="Filter"
          variant="outlined"
          value={assignedFilter}
          onChange={e => setAssignedFilter(e.target.value)}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={() => setAssignedFilter('')}
                  edge="end"
                >
                  <ClearIcon />
                </IconButton>
              </InputAdornment>
            )
          }}
        />
        <List style={{ overflow: 'auto', flex: 1 }}>
          {filterItems(assigned, assignedFilter).map(item => (
            <ListItem
              key={item.id}
              button={removableItems.includes(item.id) ? "true" : undefined}
              disabled={!removableItems.includes(item.id)}
              onClick={() => handleMoveItem(item, 'right')}
              onKeyDown={(e) => handleKeyDown(e, item, 'right')}
              style={{
                cursor: removableItems.includes(item.id) ? 'pointer' : 'not-allowed',
              }}
            >
              <ListItemText primary={item.name} />
            </ListItem>
          ))}
        </List>
      </Paper>
      <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center"> {/* Centering the buttons */}
        <Button variant="contained" onClick={() => handleConfirmMoveAll('left')} style={{ marginBottom: 8 }}>
          <KeyboardDoubleArrowLeftIcon />
        </Button>
        <Button variant="contained" onClick={() => handleConfirmMoveAll('right')}>
          <KeyboardDoubleArrowRightIcon />
        </Button>
      </Box>
      <Paper style={{ padding: 16, width: '40%', marginLeft: 16, display: 'flex', flexDirection: 'column', flex: 1 }}>
        <Typography variant="h6" gutterBottom>
          {rightTitle}: {available.length} {/* Show count */}
        </Typography>
        <TextField
          fullWidth
          label="Filter"
          variant="outlined"
          value={availableFilter}
          onChange={e => setAvailableFilter(e.target.value)}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={() => setAvailableFilter('')}
                  edge="end"
                >
                  <ClearIcon />
                </IconButton>
              </InputAdornment>
            )
          }}
        />
        <List style={{ overflow: 'auto', flex: 1 }}>
          {filterItems(available, availableFilter).map(item => (
            <ListItem 
                key={item.id} 
                button={"true"}
                onClick={() => handleMoveItem(item, 'left')}
                onKeyDown={(e) => handleKeyDown(e, item, 'left')}
                style={{
                  cursor: 'pointer',
                }}
            >
              <ListItemText primary={item.name} />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
};

export default AssignmentBlock;
