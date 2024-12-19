// apiUtils.js
// import { getRefreshToken, saveTokens, clearTokens } from '../utils/jwtUtils';
// import routes from '../contexts/Routes';

// Helper function for making authorized fetch requests
export const fetchWithAuth = async (url, options = {}) => {

  try {
    // Set default options for fetch
    const defaultOptions = {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    };
    // Merge default options with the custom options provided
    const finalOptions = { ...defaultOptions, ...options };
    let response = await fetch(url, finalOptions);

    // If the request was successful, return the response
    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      // Handle other types of errors
      const errorData = await response.json();
      throw new Error(errorData.error || 'Unexpected error');
    }
  } catch (error) {
    // Handle network errors or unexpected issues
    throw error;
  }
};
