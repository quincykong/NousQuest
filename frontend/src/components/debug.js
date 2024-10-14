import React, { useState, useEffect, useMemo } from 'react';
import BaseTemplate from './BaseTemplate';
import Box from '@mui/material/Box';
import { DataGrid, GridRowsProp, GridColDef } from '@mui/x-data-grid';

const debug = () => {

  const rows = [
    { id: 1, col1: 'Hello', col2: 'World' },
    { id: 2, col1: 'DataGridPro', col2: 'is Awesome' },
    { id: 3, col1: 'MUI', col2: 'is Amazing' },
  ];
  
  const columns = [
    { field: 'col1', headerName: 'Column 1', width: 150 },
    { field: 'col2', headerName: 'Column 2', width: 150 },
  ];

  return (
    <BaseTemplate showNav={true}>
      <Box sx={{ height: 400, width: 1 }}>
        <div style={{ height: 300, width: '100%' }}>
          <DataGrid rows={rows} columns={columns} />
        </div>
      </Box>
    </BaseTemplate>
  );
};

export default debug;
