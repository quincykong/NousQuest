import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  
  if (!token) {
    return <Navigate to="/" replace />;
  }

  // You can also decode and verify the token here if needed
  
  return children;
};

export default ProtectedRoute;
