// AuthProvider.js
import React, { createContext, useState, useEffect, useContext } from 'react';
import { fetchWithAuth } from '../utils/apiUtils';
import { useNavigate } from 'react-router-dom';
import useErrorHandling from '../hooks/useErrorHandling';
import { fetchAuthorizations } from '../services/authorizationService';
 
export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authorizations, setAuthorizations] = useState({});
  const [loading, setLoading] = useState(true); 
  const [authorizationsLoaded, setAuthorizationsLoaded] = useState(false);
  const { handleError } = useErrorHandling();
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Attempt to fetch authorizations to confirm authentication
        const data = await fetchWithAuth('/api/authorizations');
        setIsAuthenticated(true);
        setAuthorizations(data);
        setAuthorizationsLoaded(true);
        // console.log('Authorizations Data:', data);
      } catch (error) {
        setIsAuthenticated(false);
        clearTokens();
        setAuthorizationsLoaded(false);
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };

    checkAuth(); // Run on component mount
  }, [navigate]);

  const login = async (userId, password) => {
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Send cookies with request
        body: JSON.stringify({ userId, password }),
      });

      if (response.ok) {
        // Fetch authorizations and update state
        await fetchAuthorizations();
        return true;
      } else {       
        handleError({ status: response.status, message: response.message });
        setIsAuthenticated(false);
      }
    } catch (error) {
      handleError(error);
      setIsAuthenticated(false);
    }
  };

  const clearTokens = async() => {
    try {
      const response = await fetch('/api/logout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Send cookies with request
        body: JSON.stringify({ userId, password }),
      });
    } catch (error) {
      console.error("Error clearing tokens:", error);
    }
  }

  const logout = async () => {
    await clearTokens();
    setIsAuthenticated(false);
    setAuthorizations({});
    navigate('/login'); // Navigate to login page
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, authorizations, authorizationsLoaded, login, logout }}>
      {!loading && children} {/* Don't render children until loading is done */}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);