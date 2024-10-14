// hooks/usePermissions.js
import { useState, useEffect } from 'react';
import { getAccessToken, hasPermission } from '../utils/jwtUtils';

const usePermissions  = (resourceName) => {
  const [permissions, setPermissions] = useState({
    canCreate: false,
    canUpdate: false,
    canDelete: false,
  });

  useEffect(() => {
    const token = getAccessToken();
    if (token) {
      setPermissions({
        canCreate: hasPermission(resourceName, 'create'),
        canUpdate: hasPermission(resourceName, 'update'),
        canDelete: hasPermission(resourceName, 'delete'),
      });
    }
  }, [resourceName]);

  return permissions;
};

export default usePermissions;
