// usePermission.js
import { useContext } from 'react';
import { AuthContext } from '../context/AuthProvider';

const usePermission = (resource, action) => {
  const { authorizations } = useContext(AuthContext);
  console.log(`usePermission: ${JSON.stringify(authorizations, null, 2)}`);
  return authorizations[resource]?.[action] || false;
};

export default usePermission;