import React, { createContext, useContext } from 'react';

const routes = {
  frontendlog: '/frontendlog',
  home: '/home',
  login: '/login',
  forgotPassword: '/forgot-password',
  api: {
    frontendlog: 'api/frontendlog',
    home: 'api/home',
    login: '/api/login',
    resetPassword: '/api/reset-password',
  },
};

const RoutesContext = createContext();

export const RoutesProvider = ({ children }) => {
  return (
    <RoutesContext.Provider value={routes}>
      {children}
    </RoutesContext.Provider>
  );
};

export const useRoutes = () => useContext(RoutesContext);
