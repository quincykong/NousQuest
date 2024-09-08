import React, { useState } from 'react';
import { Box, Button, Checkbox, IconButton, InputAdornment, TextField } from '@mui/material';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import SearchIcon from '@mui/icons-material/Search';
import SortByAlphaIcon from '@mui/icons-material/SortByAlpha';
import BaseTemplate from './BaseTemplate';
import DataList from './DataList';
import TileBlock from './TileBlock';

const StudentGroupList = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGroups, setSelectedGroups] = useState([]);
  
  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
    // Add logic to filter the student group list based on search term
  };

  return (
    <BaseTemplate showNav={true}>
      {/* First Column: Student Group List */}
      <Box sx={{ display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Button variant="contained" color="primary">
            Create Group
          </Button>

          <TextField
            placeholder="Search"
            value={searchTerm}
            onChange={handleSearch}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setSearchTerm('')}>
                    <ArrowDropDownIcon />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
        </Box>

        {/* Data List */}
        <DataList selectedGroups={selectedGroups} setSelectedGroups={setSelectedGroups} />
      </Box>

      {/* Second Column: Tiles */}
      <Box sx={{ display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
        <TileBlock title="Students" content="Student 1, Student 2..." />
        <TileBlock title="Tags" content="Tag 1, Tag 2..." />
      </Box>
    </BaseTemplate>
  );
};

export default StudentGroupList;
