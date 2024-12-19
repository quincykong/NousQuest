// authorizationService.js
import { fetchWithAuth } from '../utils/apiUtils';

export const fetchAuthorizations = async () => {
  try {
    const response = await fetchWithAuth('/api/authorizations');
    return response.data;
  } catch (error) {
    throw new Error('Failed to fetch authorizations');
  }
};
