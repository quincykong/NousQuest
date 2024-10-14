import React, { useCallback, useState } from 'react';
import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';
import Switch from '@mui/material/Switch';
import TileBlock from './components/TileBlock';
// import DataList from './components/DataList';
import AssignmentBlock from './components/AssignmentBlock';
import ToastProvider, { triggerToast } from './components/ToastProvider';
import FooterActions from './components/FooterActions'

const TestPage = () => {
  // State to manage the list of items in the AssignmentBlock
  const [assignedItems, setAssignedItems] = useState([
    { id: 1, name: 'Student 1' },
    { id: 2, name: 'Student 2' },
    { id: 3, name: 'Student 3' }
  ]);

  const [availableItems, setAvailableItems] = useState([
    { id: 4, name: 'Student 4' },
    { id: 5, name: 'Student 5' }
  ]);

  const handleAssign = useCallback((newAssigned) => {
    setAssignedItems(newAssigned);
    triggerToast({ type: 'info', content: 'Items assigned successfully' });
  }, []);

  const handleRemove = useCallback((newAvailable) => {
    setAvailableItems(newAvailable);
    triggerToast({ type: 'warning', content: 'Items removed from assignment' });
  }, []);

  // DataList columns and rows
  const columns = [
    { id: 'status', label: 'Status', sortable: true },
    { id: 'signalName', label: 'Signal Name', sortable: true },
    { id: 'severity', label: 'Severity', sortable: true },
    { id: 'stage', label: 'Stage', sortable: false },
    { id: 'lapsedTime', label: 'Lapsed Time', sortable: true, type: 'time' },
    { id: 'teamLead', label: 'Team Lead', sortable: false }
  ];

  const rows = [
    { id: 1, status: 'Offline', signalName: 'Astrid: NE shared managed-features', severity: 'Medium', stage: 'Triaged', lapsedTime: '10:12', teamLead: 'Chase Nguyen' },
    { id: 2, status: 'Offline', signalName: 'Cosmo: prod shared vm', severity: 'Huge', stage: 'Triaged', lapsedTime: '12:45', teamLead: 'Brie Furman' },
    { id: 3, status: 'Offline', signalName: 'Phoenix: prod shared lyra-managed-features', severity: 'Minor', stage: 'Triaged', lapsedTime: '13:06', teamLead: 'Jeremy Lake' },
    { id: 4, status: 'Offline', signalName: 'Sirius: prod shared ares-managed-vm', severity: 'Negligible', stage: 'Triaged', lapsedTime: '13:18', teamLead: 'Angelica Howards' }
  ];

  const pageInfo = { currentPage: 1, rowsPerPage: 4, totalRows: 100 };

  const handleRowClick = useCallback((row) => {
    triggerToast({ type: 'info', content: `Row clicked: ${row.signalName}` });
  }, []);

  const handleAddClick = useCallback(() => {
    triggerToast({ type: 'info', content: 'Add record clicked' });
  }, []);

  const handleDelete = () => {
    triggerToast({ type: 'critical', content: 'Record deleted' });
    // Handle delete operation here
  };

  const handleCancel = () => {
    triggerToast({ type: 'warning', content: 'Operation canceled' });
    // Handle cancel operation here
  };

  const handleSave = () => {
    triggerToast({ type: 'info', content: 'Record saved' });
    // Handle save operation here
  };

  return (
    <div>
      <ToastProvider />
      <Grid container spacing={3}>
        {/* Left Column */}
        <Grid item xs={12} md={8}>
          <TileBlock
            title="Data List Section"
            collapsible={true}
            initialCollapsed={false}
            inheritTheme={true}
          >
            {/* <DataList
              columns={columns}
              rows={rows}
              pageInfo={pageInfo}
              onRowClick={handleRowClick}
              onAddClick={handleAddClick}
            /> */}
          </TileBlock>
          <TileBlock
            title="Assignment Block Section"
            collapsible={true}
            initialCollapsed={false}
            inheritTheme={true}
          >
            <AssignmentBlock
              assignedItems={assignedItems}
              availableItems={availableItems}
              onAssign={handleAssign}
              onRemove={handleRemove}
              removableItems={[1, 2, 3]} // Only these items are removable
              leftLimit={5}
              leftTitle="Enrolled Students"
              rightTitle="Available Students"
            />
          </TileBlock>
        </Grid>

        {/* Right Column */}
        <Grid item xs={12} md={4}>
          <TileBlock
            title="Properties"
            collapsible={true}
            initialCollapsed={false}
          >
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Switch
                  defaultChecked
                  color="primary"
                />
                <TextField
                  fullWidth
                  label="Invitation Key"
                  variant="outlined"
                />
              </Grid>
            </Grid>
          </TileBlock>
          <TileBlock
            title="Log"
            collapsible={true}
            initialCollapsed={false}
          >
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Created at"
                  variant="outlined"
                  disabled
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Created by"
                  variant="outlined"
                  disabled
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Updated at"
                  variant="outlined"
                  disabled
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Updated by"
                  variant="outlined"
                  disabled
                />
              </Grid>
            </Grid>
          </TileBlock>
        </Grid>
      </Grid>
      {/* Footer Actions */}
      <FooterActions
        canDelete={true}
        canEdit={true}
        onDelete={handleDelete}
        onCancel={handleCancel}
        onSave={handleSave}
      />
    </div>
  );
};

export default TestPage;
