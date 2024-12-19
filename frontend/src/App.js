import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { RoutesProvider } from './contexts/RoutesContext';
import { AuthProvider } from './contexts/AuthProvider';
// Custom functions
import LoginForm from './features/auth/LoginForm';
import ForgotPasswordForm from './features/auth/ForgotPasswordForm';
import HomePage from './pages/HomePage';
import StudentGroupList from './features/group/StudentGroupList';
import StudentGroupForm from './features/group/StudentGroupForm';
// import Debug from './components/debug';

// const TestPage = React.lazy(() => import('./TestPage'));

function App() {
  const [themeMode, setThemeMode] = useState('light');

  const toggleTheme = () => {
    setThemeMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  const theme = createTheme({
    palette: {
      mode: themeMode,
    },
  });

  return (
    <ThemeProvider theme={theme}>
      <Router>
        <AuthProvider>
          <RoutesProvider>
            {/* <TokenValidation /> */}
            <Routes>
              <Route path="/home" element={<HomePage />} />
              <Route path="/login" element={<LoginForm />} />
              <Route path="/forgot-password" element={<ForgotPasswordForm />} />
              <Route path="/student-group" element={<StudentGroupList />} />
              <Route path="/student-group/new" element={<StudentGroupForm />} />
              <Route path="/student-group/:id" element={<StudentGroupForm />} />
              {/* Add other routes here as needed */}
            </Routes>
          </RoutesProvider>
        </AuthProvider>
      </Router>
    </ThemeProvider>
  );
}

export default App;