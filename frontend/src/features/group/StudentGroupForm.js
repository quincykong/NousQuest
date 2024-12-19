import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { Box, Grid2, TextField, Typography, Container, Paper, Switch, FormControlLabel } from '@mui/material';
import AssignmentBlock from '../../components/AssignmentBlock';
import TileBlock from '../../components/TileBlock';
import FooterActions from '../../components/FooterActions';
import { fetchUserGroupById, updateUserGroup, createUserGroup, deleteUserGroup } from '../../services/studentGroupService';
import BaseTemplate from '../../components/BaseTemplate';
import usePermissions from '../../hooks/usePermissions';
import HashtagInput from '../../components/HashtagInput';

const StudentGroupForm = () => {
  const { id } = useParams(); // Get the ID from the route parameters
  const navigate = useNavigate();
  
  const RESOURCE_NAME = 'usergroup';
  const { canCreate, canUpdate, canDelete } = usePermissions(RESOURCE_NAME); // Permissions
  const [groupData, setGroupData] = useState(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState('');
  const [studentsInGroup, setStudentsInGroup] = useState([]);
  const [studentsNotInGroup, setStudentsNotInGroup] = useState([]);
  const [status, setStatus] = useState(false);
  const [log, setLog] = useState({ created_at: '', created_by: '', updated_at: '', updated_by: '' });
  const isReadOnly = !canUpdate; // Determine if the form is in view-only mode

  // Fetch data for the form (edit mode)
  useEffect(() => {
    if (id) {
      fetchUserGroupById(id, true, true)
        .then((data) => {
          setGroupData(data);
        })
        .catch((error) => console.error('Failed to fetch group data:', error));
    }
  }, [id]);

  useEffect(() => {
    if (groupData) {
      setTitle(groupData.title || '');
      setDescription(groupData.description || '');
      setTags(groupData.tags.join(', ') || ''); // Convert tags array to string
      setStudentsInGroup(groupData.studentsInGroup || []);
      setStatus(groupData.status === '1');
      setLog({
        created_at: groupData.log?.created_at || '',
        created_by: groupData.log?.created_by || '',
        updated_at: groupData.log?.updated_at || '',
        updated_by: groupData.log?.updated_by || ''
      })
      // console.log('Received groupData:', JSON.stringify(groupData, null, 2));
      // console.log(`groupData.title: ${groupData.title}`)
      // console.log(`groupData.created_at: ${groupData.log?.created_at}`)
      // console.log(`log.created_at: ${log.created_at}`)
      // console.log(`log: ${JSON.stringify(log, null, 2)}`)
    }
  }, [groupData]);

  // Effect to log the updated log state once it has been set
  // useEffect(() => {
  //   console.log('Updated log state:', log);
  // }, [log]);

  // Save function
  const handleSave = async () => {
    const updatedGroup = {
      title,
      description,
      tags: tags.split(',').map(tag => tag.trim()), // Convert string to array
      studentsInGroup,
      status: status ? '1' : '0',
    };

    try {
      if (id) {
        await updateUserGroup(id, updatedGroup);
      } else {
        await createUserGroup(updatedGroup);
      }
      navigate('/student-groups'); // Redirect back to the list after saving
    } catch (error) {
      console.error('Save operation failed', error);
    }
  };

  // Cancel function
  const handleCancel = () => {
    navigate('/student-groups'); // Navigate back to list without saving
  };

  // Delete function
  const handleDelete = async () => {
    try {
      if (id) {
        await deleteUserGroup(id);
        navigate('/student-groups'); // Redirect back to the list after deleting
      }
    } catch (error) {
      console.error('Delete operation failed', error);
    }
  };

  // Add and remove students
  const handleAddStudent = (student) => {
    setStudentsInGroup([...studentsInGroup, student]);
    setStudentsNotInGroup(studentsNotInGroup.filter(s => s !== student));
  };

  const handleRemoveStudent = (student) => {
    setStudentsInGroup(studentsInGroup.filter(s => s !== student));
    setStudentsNotInGroup([...studentsNotInGroup, student]);
  };

  return (
    <BaseTemplate showNav={false}>
      <Box sx={{ display: 'flex', flexDirection: 'row', flexGrow: 1 }}>
        <Box sx={{ flex: 2, marginRight: 2 }}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              {id ? 'Edit Student Group' : 'Create Student Group'}
            </Typography>
            <Box component="form" noValidate autoComplete="off">
              <Container maxWidth="md">
                <TextField
                  fullWidth
                  label="Group Title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  variant="outlined"
                  margin="normal"
                  disabled={isReadOnly}
                />
                <TextField
                  fullWidth
                  label="Description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  variant="outlined"
                  margin="normal"
                  disabled={isReadOnly}
                />
                <HashtagInput
                  initialHashtags={tags.split(',').map(tag => tag.trim())}  // Convert the comma-separated string to an array
                  readOnly={isReadOnly}  // Pass the readOnly flag based on form mode
                  onTagClick={(tag) => console.log(`Tag clicked: ${tag}`)}  // Optional: handle tag click in read-only mode
                  onChange={(newTags) => setTags(newTags.join(','))} // Convert the array back to a comma-separated string
                />
                {/* <TextField
                  fullWidth
                  label="Tags"
                  value={tags}
                  onChange={(e) => setTags(e.target.value)}
                  variant="outlined"
                  margin="normal"
                  helperText="Enter tags separated by commas"
                  disabled={isReadOnly}
                /> */}
              </Container>
              <Box mt={3}>
                <AssignmentBlock
                  assignedItems={studentsInGroup}
                  availableItems={studentsNotInGroup}
                  onAssign={handleAddStudent}
                  onRemove={handleRemoveStudent}
                  leftTitle="Students in Group"
                  rightTitle="Available Students"
                  disabled={isReadOnly} // Disable AssignmentBlock if form is read-only
                />
              </Box>
            </Box>
          </Paper>
        </Box>
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <TileBlock
            title="Properties"
            isCollapsed={false}
            onToggle={() => {}}
          >
            <FormControlLabel
              control={<Switch checked={status} onChange={(e) => setStatus(e.target.checked)} />}
              label="Enabled"
              disabled={isReadOnly}
            />
          </TileBlock>
          <TileBlock
            title="Changes"
            isCollapsed={false}
            onToggle={() => {}}
          >
            <Box>
              <Grid2 container spacing={2} direction='column' columns={12}>
                <Grid2 xs={6}>
                  <Typography align="left">Created by:</Typography>
                </Grid2>
                <Grid2 xs={6}>
                  <Typography align="left">{log.created_by}</Typography>
                </Grid2>
                <Grid2 xs={6}>
                  <Typography align="left">Created at:</Typography>
                </Grid2>
                <Grid2 xs={6}>
                  <Typography align="left">{log.created_at}</Typography>
                </Grid2>
                <Grid2 xs={6}>
                  <Typography align="left">Updated by:</Typography>
                </Grid2>
                <Grid2 xs={6}>
                  <Typography align="left">{log.updated_by}</Typography>
                </Grid2>
                <Grid2 xs={6}>
                  <Typography align="left">Updated at:</Typography>
                </Grid2>
                <Grid2 xs={6}>
                  <Typography align="left">{log.updated_at}</Typography>
                </Grid2>
              </Grid2>
            </Box>
          </TileBlock>
        </Box>
      </Box>
      <FooterActions
        canDelete={canDelete}
        canEdit={canUpdate}
        onSave={handleSave}
        onCancel={() => navigate('/student-groups')}
        onDelete={handleDelete}
        readOnly={isReadOnly}
      />
    </BaseTemplate>
  );
};

export default StudentGroupForm;
