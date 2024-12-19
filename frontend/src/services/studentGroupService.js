// services/studentGroupService.js
// import { ensureValidToken } from '../utils/jwtUtils';
import { triggerToast } from '../components/ToastProvider';
//import { routes } from '../components/RoutesContext';
import routes from '../context/Routes';
import { fetchWithAuth } from '../utils/apiUtils';

// Build the query string based on the parameters provided
const buildQueryString = (baseUrl, params) => {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      query.append(key, value);
    }
  }
  return `${baseUrl}?${query.toString()}`;
};

// Call backend to fetch UserGroups
export const fetchUserGroups = async (page, perPage, searchTerm, selectedTags = []) => {
  try {
    const adjustedPage = page + 1;
    const tagsQuery = selectedTags.join(',');

    // Build complete query string using helper function
    const url = buildQueryString(routes.api.studentgroup, {
      page: adjustedPage,
      per_page: perPage,
      search: searchTerm,
      tags: tagsQuery,
    });

    // Make the API call using the generic fetchWithAuth function
    const data = await fetchWithAuth(url);
    return {
      rows: data.rows || [],
      totalRows: data.pageInfo?.totalRows || 0,
    };
  } catch (error) {
    triggerToast({ type: 'critical', content: `fetchUserGroups error: ${error.message}` });
    return { rows: [], totalRows: 0 };
  }
};

// Call backend to fetch UserGroup by ID
export const fetchUserGroupById = async (groupId, includeStudents = false, includeTags = false) => {
  try {
    // Build the query string with optional parameters
    const url = buildQueryString(`${routes.api.studentgroup}/${groupId}`, {
      include_students: includeStudents,
      include_tags: includeTags,
    });

    const groupData = await fetchWithAuth(url);
    if (groupData) {
      const formattedGroupData = {
        title: groupData.title,
        description: groupData.description,
        studentcount: groupData.studentcount,
        status: groupData.status,
        log: {
          created_at: groupData.created_at,
          created_by: groupData.created_by,
          updated_at: groupData.updated_at,
          updated_by: groupData.updated_by
        },
        studentsInGroup: groupData.studentsInGroup.map(student => ({
          id: student.id,
          name: student.name,
          locked: student.locked
        })),
        tags: groupData.tags.map(tag => tag.name)
      };
      return formattedGroupData;
    } else {
      console.error('Unexpected response format:', groupData);
      return null;
    }
  } catch (error) {
    console.error('Failed to fetch user group:', error);
    throw error;
  }
};

// Mass enabled/disabled delete from list function
export const performMassAction = async (action, selectedIds) => {
  try {
    let url = '';
    let method = 'PUT';
    let requestBody = {};

    if (action === 'enable' || action === 'disable') {
      const status = action === 'enable' ? 1 : 0;
      url = routes.api.massUpdateGroups;
      requestBody = { groupIds: selectedIds, status: status };
    } else if (action === 'delete') {
      url = routes.api.massDeleteGroups;
      method = 'POST';
      requestBody = { groupIds: selectedIds };
    }

    const response = await fetchWithAuth(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Unexpected error');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    triggerToast({ type: 'critical', content: `Failed to ${action}: ${error.message}`, logToBackend: true });
    throw error;
  }
};

// Function to update a UserGroup
export const updateUserGroup = async (groupId, updatedGroupData) => {
  try {
    const url = `${routes.api.studentgroup}/${groupId}`;
    const response = await fetchWithAuth(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updatedGroupData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to update user group');
    }

    const data = await response.json();
    triggerToast({ type: 'success', content: 'User group updated successfully!' });
    return data;
  } catch (error) {
    triggerToast({ type: 'critical', content: `Update failed: ${error.message}`, logToBackend: true });
    throw error;
  }
};

// Function to create a new UserGroup
export const createUserGroup = async (newGroupData) => {
  try {
    const url = routes.api.studentgroup;
    const response = await fetchWithAuth(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(newGroupData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to create user group');
    }

    const data = await response.json();
    triggerToast({ type: 'success', content: 'User group created successfully!' });
    return data;
  } catch (error) {
    triggerToast({ type: 'critical', content: `Creation failed: ${error.message}`, logToBackend: true });
    throw error;
  }
};

// Function to delete a UserGroup
export const deleteUserGroup = async (groupId) => {
  try {
    const url = `${routes.api.studentgroup}/${groupId}`;
    const response = await fetchWithAuth(url, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to delete user group');
    }

    triggerToast({ type: 'success', content: 'User group deleted successfully!' });
    return true;
  } catch (error) {
    triggerToast({ type: 'critical', content: `Deletion failed: ${error.message}`, logToBackend: true });
    throw error;
  }
};