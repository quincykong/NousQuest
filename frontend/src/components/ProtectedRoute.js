import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthProvider';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, authorizationsLoaded } = useAuth();

  if (!authorizationsLoaded) {
    return <div>Loading...</div>; // Or a spinner/loading indicator
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
