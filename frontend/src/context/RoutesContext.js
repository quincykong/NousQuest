import React, { createContext, useContext } from 'react';
import routes from './Routes';

const RoutesContext = createContext();

export const RoutesProvider = ({ children }) => {
  return (
    <RoutesContext.Provider value={routes}>
      {children}
    </RoutesContext.Provider>
  );
};

export const useRoutes = () => useContext(RoutesContext);
