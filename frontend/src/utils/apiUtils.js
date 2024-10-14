// apiUtils.js
import { triggerToast } from '../components/ToastProvider';
import { getRefreshToken, saveTokens, clearTokens } from '../utils/jwtUtils';
import routes from '../contexts/Routes';
import { useNavigate } from 'react-router-dom';

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
    //console.log(finalOptions)
    //console.log(url)
    // Make the API call
    let response = await fetch(url, finalOptions);

    // Handle response when it's unauthorized or token expired
    if (response.status === 401) {
        clearTokens();
        window.location.href = routes.login; // Redirect to login
        return;
    } 
    // If the request was successful, return the response
    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      // Handle other types of errors
      const errorData = await response.json();
      triggerToast({ type: 'critical', content: errorData.error || 'Unexpected error' });
      throw new Error(errorData.error || 'Unexpected error');
    }
  } catch (error) {
    // Handle network errors or unexpected issues
    triggerToast({ type: 'critical', content: `Network error: ${error.message}` });
    throw error;
  }
};
