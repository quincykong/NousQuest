import Cookies from 'js-cookie';
import { jwtDecode } from 'jwt-decode';

// Store the token in cookies
export const saveTokens = (access_token, refresh_token) => {
  Cookies.set('access_token', access_token, {
    secure: true, // Ensure cookies are sent over HTTPS
    sameSite: 'Strict', // Control cross-site request behavior
    path: '/',  // Available for the entire site
    expires: 1  // Token expiration in 1 day (set according to your JWT expiration)
  });

  // Save the refresh token
  Cookies.set('refresh_token', refresh_token, {
    secure: true,
    sameSite: 'Strict',
    path: '/',
    expires: 7  // Refresh token usually lasts longer, e.g., 7 days
  });
};

// Get the token from cookies
export const getAccessToken = () => {
  return Cookies.get('access_token');
};

// Store the refresh token in cookies
// export const saveRefreshToken = (refreshToken) => {
//   Cookies.set('refresh_token', refreshToken, {
//     secure: true,
//     sameSite: 'Strict',
//     path: '/',
//     expires: 7 // Set refresh token expiration
//   });
// };

// Get the refresh token from cookies
export const getRefreshToken = () => {
  return Cookies.get('refresh_token');
};

// Clear all tokens
export const clearTokens = () => {
  Cookies.remove('access_token', { path: '/' });
  Cookies.remove('refresh_token', { path: '/' });
};

// Function to decode the token and return its payload
export const decodeToken = () => {
  const token = getAccessToken();
  if (!token) {
    return null;
  }

  try {
    return jwtDecode(token);  // Use the decoded JWT
  } catch (error) {
    console.error("Invalid token or unable to decode", error);
    return null;
  }
};

// Function to check if the user has a specific permission
export const hasPermission = (resource, action) => {
  const decodedToken = decodeToken(getAccessToken());  // gets the token from the cookie
  if (!decodedToken || !decodedToken.permissions) {
    return false;
  }

  return decodedToken.permissions.some(permission =>
    permission.resource === resource && permission.action === action
  );
};

export const ensureValidToken = async () => {
  const token = getAccessToken();  // Fetch the access token from cookies
  console.log(`token: ${token}`)
  if (!token) {
    // No token found, require login
    return { token: null, message: 'No token found. Please log in.' };
  }

  // Decode the JWT
  const parsedToken = JSON.parse(atob(token.split('.')[1]));  // Decode JWT payload
  const currentTime = Math.floor(Date.now() / 1000);  // Current time in seconds
  const isExpired = parsedToken.exp <= currentTime;
  console.log(`isExpired:${isExpired}`)
  if (isExpired) {
    // Token expired, attempt to refresh using the refresh token
    const refreshToken = getRefreshToken();  // Fetch the refresh token from cookies
    console.log(`Token expired. Getting a new refreshToken:${refreshToken}`)
    if (!refreshToken) {
      // Refresh token not in cookie, require login
      clearTokens();  // Clear expired tokens
      return { token: null, message: 'Session expired. Please log in again.' };
    }

    // Attempt to refresh the access token
    try {
      const response = await fetch('/api/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        // Save the new access token and refresh token in cookies
        saveTokens(data.access_token, data.refresh_token);  // You need to make sure saveTokens handles both tokens
        return { token: data.access_token, message: '' };  // Return new token
      } else if (response.status === 401) {
        // Refresh token expired or invalid, require login
        clearTokens();  // Clear all tokens
        return { token: null, message: 'Session expired. Please log in again.' };
      } else {
        // Other error occurred during token refresh
        return { token: null, message: 'Failed to refresh token. Please log in again.' };
      }
    } catch (error) {
      // Handle network errors or unexpected exceptions
      return { token: null, message: `Error refreshing token: ${error.message}` };
    }
  }

  // Token is valid and not expired
  return { token, message: '' };
};