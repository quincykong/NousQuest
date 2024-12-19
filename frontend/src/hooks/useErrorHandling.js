import { useNavigate } from 'react-router-dom';
import { triggerToast } from '../components/ToastProvider';  // Assuming triggerToast is globally available

const useErrorHandling = () => {
  const navigate = useNavigate();

  const handleError = (error) => {
    // Network error handling
    if (error.message === 'Failed to fetch') {
      triggerToast({ type: 'warning', content: 'Network error. Please check your internet connection.' });
    }
    // Authentication error (401)
    else if (error.status === 401) {
      triggerToast({ type: 'warning', content: 'Your session has expired. Redirecting to login...' });
      // Automatically redirect to the login page
      navigate('/login');
    }
    // Authorization error (403)
    else if (error.status === 403) {
      triggerToast({ type: 'error', content: 'You do not have permission to perform this action.' });
    }
    // Server error (500)
    else if (error.status === 500) {
      triggerToast({ type: 'critical', content: 'Server error. Please try again later.' });
    }
    // General error handling
    else {
      triggerToast({ type: 'error', content: error.message || 'An unexpected error occurred.' });
    }
  };

  return {
    handleError,
  };
};

export default useErrorHandling;
