import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { DataGrid } from '@mui/x-data-grid';
import { Box, Button, Chip, IconButton, Menu, MenuItem, List, ListItem, ListItemText, Paper, Toolbar, TextField } from '@mui/material';
import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';  // For "Enabled"
import WarningAmberIcon from '@mui/icons-material/WarningAmber';  // For "Disabled"
import { exportToExcel } from '../../components/ExportToExcel';
import BaseTemplate from '../../components/BaseTemplate';
import TileBlock from '../../components/TileBlock';
import { triggerToast } from '../../components/ToastProvider';
import HashtagInput from '../../components/HashtagInput';
import usePermissions from '../../hooks/usePermissions';
import useUserPreferences from '../../hooks/useUserPreferences';
//import { saveUserPreferences, getUserPreferences } from '../../services/preferencesService';
import { fetchUserGroupById, fetchUserGroups, performMassAction } from '../../services/studentGroupService';
//import { fetchStudentsAndTags } from '../../services/StudentsAndTagsService';
import { debouncedSearch } from '../../utils/debounceUtils';
import routes from '../../context/Routes';

const StudentGroupList = () => {
  const RESOURCE_NAME = 'usergroup';
  const ROWS_PER_PAGE = 25;

  const navigate = useNavigate();
  
  // const [isLoading, setIsLoading] = useState(true);
  const { canCreate, canUpdate, canDelete } = usePermissions(RESOURCE_NAME);
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedGroups, setSelectedGroups] = useState([]); 
  const [rows, setRows] = useState([]); 
  const [rowCount, setRowCount] = useState(0);
  const [students, setStudents] = useState([]); 
  const [tags, setTags] = useState([]); 
  const [selectedTags, setSelectedTags] = useState([]); 
  const [isLoading, setIsLoading] = useState(false); // Added isLoading state here
  const defaultPreferences = {
    paginationModel: { page: 0, pageSize: ROWS_PER_PAGE },
    sortModel: [],
    columnVisibilityModel: {},
    filterModel: { items: [] },
    studentsTileOpen: false,
    tagsTileOpen: true,
    searchTerm: '',
  };
  const [preferences, setPreferences, isInitialLoad] = useUserPreferences(RESOURCE_NAME, defaultPreferences);
  const { paginationModel, sortModel, columnVisibilityModel, filterModel, studentsTileOpen, tagsTileOpen, searchTerm } = preferences;
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState(searchTerm);
  const debouncedSearchHandler = useMemo(() => debouncedSearch(setDebouncedSearchTerm, 300), []);

  // Debounce the search input
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);  // Set debounced value after 300ms
    }, 300);

    return () => {
      clearTimeout(handler);  // Cleanup timeout on every key press
    };
  }, [searchTerm]);

  // Fetch usergroup data
  useEffect(() => {
    if (isInitialLoad) return; // Prevent running on initial load
    setIsLoading(true);

    fetchUserGroups(paginationModel.page, paginationModel.pageSize, debouncedSearchTerm, selectedTags)
      .then(data => {
        setRows(data.rows);  // Update rows state with fetched data
        setRowCount(data.totalRows);  // Update row count with fetched data
      })
      .finally(() => setIsLoading(false));

  }, [debouncedSearchTerm, selectedTags, paginationModel, isInitialLoad]);

  // Define DataGrid Columns
  const columns = useMemo(() => [
    {
      field: 'title',
      headerName: 'Group Title',
      sortable: true,
      width: 200,
      renderCell: (params) => (
        <Button color="primary"
          onClick={() => 
            navigate(`/student-group/${params.row.id}`)
          }
        > 
          {params.value}
        </Button>
      ),
    },
    { field: 'description', headerName: 'Description', sortable: true, width: 400 },
    { field: 'studentcount', headerName: 'Student(s)', sortable: true, width: 50 },
    {
      field: 'status',
      headerName: 'Status',
      width: 150,
      sortable: true,
      renderCell: (params) => {
        const isEnabled = params.row.status === '1'; 
        return (
          <Chip
            icon={isEnabled ? <CheckCircleIcon /> : <WarningAmberIcon />}
            label={isEnabled ? 'Enabled' : 'Disabled'}
            color={isEnabled ? 'success' : 'warning'}
            variant="outlined"
            sx={{
              borderRadius: '16px',
              backgroundColor: isEnabled ? '#e8f5e9' : '#fff3e0',
              color: isEnabled ? '#4caf50' : '#ff9800',
              borderColor: isEnabled ? '#4caf50' : '#ff9800'
            }}
          />
        );
      }
    },
    { field: 'created_at', headerName: 'Created', sortable: true, width: 80 },
    { field: 'updated_at', headerName: 'Updated', sortable: true, width: 80 },
  ], []);

  // Handle the search input change
  const handleSearchChange = (event) => {
    const value = event.target.value;
    setPreferences(prev => ({ ...prev, searchTerm: value }));
    debouncedSearchHandler(value);
  };

  // Handle tag selection (add or remove) from/to search bar
  const handleTagClick = (tag) => {
    const updatedTags = selectedTags.includes(tag)
      ? selectedTags.filter(t => t !== tag)
      : [...selectedTags, tag];

    setSelectedTags(updatedTags);
    setPreferences(prev => ({ ...prev, selectedTags: updatedTags }));
  };

  // Handle tag removal directly from tag list under search bar
  const handleTagRemove = (tagToDelete) => {
    const updatedTags = selectedTags.filter(tag => tag !== tagToDelete);
    setSelectedTags(updatedTags);
    setPreferences(prev => ({ ...prev, selectedTags: updatedTags }));
  };

  // Fetch students and tags for the selected group
  const handleRowClick = (params) => {
    fetchUserGroupById(params.row.id, true, true)  // Set both includeStudents and includeTags to true
      .then((groupData) => {
        if (groupData) {
          setStudents(groupData.studentsInGroup); // Set students from the fetched group data
          setTags(groupData.tags); // Set tags from the fetched group data
        }
      })
      .catch((error) => {
        console.error("Failed to fetch group data:", error);
        triggerToast({ type: 'critical', content: `Failed to fetch group data: ${error.message}`, logToBackend: true });
      });
  };

  // Track the selected groups
  const handleSelectionModelChange = (selectionModel) => {
    setSelectedGroups(selectionModel);  
  };

  // Mass function menu and functions
  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleExportToExcel = () => {
    const columnOrder = ['title', 'description', 'studentcount', 'status', 'created_at', 'updated_at'];
    const headerTranslations = {
      title: 'Group Title',
      description: 'Description',
      studentcount: 'Student Count',
      status: 'Status',
      created_at: 'Created At',
      updated_at: 'Updated At',
    };
    const transformations = {
      status: value => (value === '1' ? 'Enabled' : 'Disabled'),
    };

    exportToExcel({
      rows,
      columnOrder,
      headerTranslations,
      transformations,
      filename: 'StudentGroups.xlsx',
    });
  };

  const handleMassAction = async (action) => {
    try {
      const data = await performMassAction(action, selectedGroups);
      triggerToast({ type: 'success', content: `${data.message}` });

      // Refresh Data
      fetchUserGroups(paginationModel.page, paginationModel.pageSize, debouncedSearchTerm, selectedTags).then(updatedData => {
        setRows(updatedData.rows);
        setRowCount(updatedData.totalRows);
      });
    } catch (error) {
      // Error handling is done within the service
    }
    handleMenuClose();
  };

  // User Preferences: Handle tile toggle for Students
  const handleStudentsTileToggle = (newState) => {
    setPreferences(prev => ({ ...prev, studentsTileOpen: newState }));
  };

  // User Preferences: Handle tile toggle for Tags
  const handleTagsTileToggle = (newState) => {
    setPreferences(prev => ({ ...prev, tagsTileOpen: newState }));
  };

  const listStyle = { display: 'flex', flexDirection: 'column', height: 'calc(100vh - 200px)', width: '100%' };
  // console.log(`canCreate: ${canCreate}`)
  // console.log(`canUpdate: ${canUpdate}`)
  // console.log(`canDelete: ${canDelete}`)
  return (
    <BaseTemplate showNav={true}>
      <Box sx={{ display: 'flex', flexDirection: 'row', flexGrow: 1 }}>
        <Box sx={{ flex: 2, marginRight: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            {canCreate ? (
              <Button variant="contained" color="primary">Create Group</Button>
            ) : (
              <Box sx={{ width: '128px', height: '36px' }} />
            )}
            <IconButton onClick={handleMenuClick}>
              <MoreHorizIcon />
            </IconButton>
            <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
              {canUpdate && <MenuItem onClick={() => handleMassAction('enable')}>Enable</MenuItem>}
              {canUpdate && <MenuItem onClick={() => handleMassAction('disable')}>Disable</MenuItem>}
              {canDelete && <MenuItem onClick={() => handleMassAction('delete')}>Delete</MenuItem>}
              <MenuItem onClick={() => handleMassAction('export')}>Export to Excel</MenuItem>
            </Menu>
          </Box>
          <Paper sx={listStyle}>
            <Toolbar>
              <TextField
                label="Search"
                variant="outlined"
                size="small"
                value={searchTerm}
                onChange={handleSearchChange}
                style={{ marginLeft: 16, flexGrow: 1 }}
              />
            </Toolbar>
            {selectedTags.length > 0 && (
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', marginLeft: 2, marginBottom: 1 }}>
                {selectedTags.map((tag, index) => (
                  <Chip key={index} label={tag} variant="outlined" onDelete={() => handleTagRemove(tag)} />
                ))}
              </Box>
            )}
            <DataGrid
              loading={isLoading}
              checkboxSelection
              columns={columns}
              columnVisibilityModel={columnVisibilityModel}
              onColumnVisibilityModelChange={(newModel) => {
                setPreferences(prev => ({ ...prev, columnVisibilityModel: newModel }));
              }}
              rows={rows}
              rowCount={rowCount}
              disableRowSelectionOnClick
              paginationMode="server"
              pageSizeOptions={[25, 50, 100]}
              paginationModel={paginationModel}
              onPaginationModelChange={(newPaginationModel) => {
                setPreferences(prev => ({
                  ...prev,
                  paginationModel: newPaginationModel
                }));
              }}
              sortModel={sortModel}
              onSortModelChange={(newSortModel) => {
                setPreferences(prev => ({ ...prev, sortModel: newSortModel }));
              }}
              onRowClick={handleRowClick}
              onRowSelectionModelChange={handleSelectionModelChange}
              filterModel={filterModel}
              onFilterModelChange={(newFilterModel) => {
                setPreferences(prev => ({ ...prev, filterModel: newFilterModel }));
              }}
              sx={{ border: 0, cursor: 'pointer' }}
            />
          </Paper>
        </Box>
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <TileBlock
            title={`Students:`}
            isCollapsed={studentsTileOpen}
            onToggle={handleStudentsTileToggle}
          >
            <List>
              {students.map((student, index) => (
                <ListItem key={index}>
                  <ListItemText primary={student} />
                </ListItem>
              ))}
            </List>
          </TileBlock>
          <TileBlock
            title="Tags"
            isCollapsed={tagsTileOpen}
            onToggle={handleTagsTileToggle}
          >
            <HashtagInput initialHashtags={tags} readOnly={true} onTagClick={handleTagClick} />
          </TileBlock>
        </Box>
      </Box>
    </BaseTemplate>
  );
};

export default StudentGroupList;
