import React from 'react';
import { ToastContainer, toast } from 'react-toastify';
import axios from 'axios';
import 'react-toastify/dist/ReactToastify.css';

export const ToastProvider = ({ children, logToBackend = false }) => {
  return (
    <>
      <ToastContainer position="top-right" closeOnClick pauseOnHover />
      {children}
    </>
  );
};

// Function to send the error log to the backend
const logErrorToBackend = async (message) => {
  //const routes = useRoutes();
  try {
    const clientInfo = {
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      timestamp: new Date().toISOString()
    };
    //await axios.post(routes.api.frontendlog, {
      await axios.post('http://localhost:5000/api/frontendlog', {
      message,
      clientInfo
    });
  } catch (error) {
    console.error("Server is unavailable:", error);
  }
};

export const triggerToast = (message, isDarkMode = false, logToBackend = false) => {

  const lightColors = {
    critical: { background: '#f8d7da', text: '#721c24' },
    warning: { background: '#fff3cd', text: '#856404' },
    info: { background: '#d4edda', text: '#155724' },
  };

  const darkColors = {
    critical: { background: '#721c24', text: '#f8d7da' },
    warning: { background: '#856404', text: '#fff3cd' },
    info: { background: '#155724', text: '#d4edda' },
  };

  const colors = isDarkMode ? darkColors : lightColors;

  const options = {
    autoClose: 3000, // Automatically dismiss after n seconds
    closeButton: true,
    onClick: () => {
      navigator.clipboard.writeText(message.content); // Copy to clipboard
      toast.info('Message copied to clipboard', { autoClose: 1000 });
    }
  };

  // Log to backend if critical and logToBackend flag is true
  if (logToBackend) {
    logErrorToBackend(message.content);
  }

  switch (message.type) {
    case 'critical':
      toast.error(message.content, { ...options, style: { backgroundColor: colors.critical.background, color: colors.critical.text } });
      break;
    case 'warning':
      toast.warn(message.content, { ...options, style: { backgroundColor: colors.warning.background, color: colors.warning.text } });
      break;
    case 'info':
      toast.info(message.content, { ...options, style: { backgroundColor: colors.info.background, color: colors.info.text } });
      break;
    default:
      toast(message.content, options);
      break;
  }
};

export default ToastProvider;