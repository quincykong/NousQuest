import React, { createContext, useState, useContext } from 'react';

// Create a context for authentication
const AuthContext = createContext();

// AuthProvider component to wrap your app
export const AuthProvider = ({ children }) => {
  //const [isAuthenticated, setIsAuthenticated] = useState(false); // Replace with real authentication logic
  const [userRoles, setUserRoles] = useState([]);

  const login = () => {
    //setIsAuthenticated(true);  // Logic for logging in
    const rolesFromBackend = ['instructor']; // This should come from your backend during login
    setUserRoles(rolesFromBackend);
  };

  const logout = () => {
    //setIsAuthenticated(false); // Logic for logging out
    setUserRoles([]);
  };

  return (
    <AuthContext.Provider value={{ userRoles, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the AuthContext
export const useAuth = () => useContext(AuthContext);
