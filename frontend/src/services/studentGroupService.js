// services/studentGroupService.js
// import { ensureValidToken } from '../utils/jwtUtils';
import { triggerToast } from '../components/ToastProvider';
//import { routes } from '../components/RoutesContext';
import routes from '../contexts/Routes';
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
    //console.log(`url: ${url}`)
    //console.log(`data: ${data}`)
    return {
      rows: data.rows || [],
      totalRows: data.pageInfo?.totalRows || 0,
    };
  } catch (error) {
    triggerToast({ type: 'critical', content: `fetchUserGroups error: ${error.message}` });
    return { rows: [], totalRows: 0 };
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

    const response = await fetch(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
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
