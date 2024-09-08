import React, { Suspense } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import LoginForm from './components/LoginForm';
import ForgotPasswordForm from './components/ForgotPasswordForm';
import { RoutesProvider } from './components/RoutesContext';
import { AuthProvider } from './components/AuthProvider';
import ProtectedRoute from './components/ProtectedRoute';

const TestPage = React.lazy(() => import('./TestPage'));

function App() {
  const [themeMode, setThemeMode] = React.useState('light');

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
            <CssBaseline />
            <Routes>
              <Route path="/" element={<LoginForm />} />
              <Route path="/forgot-password" element={<ForgotPasswordForm />} />
              <Route path="/home" element={
                  <ProtectedRoute>
                    <Suspense fallback={<div>Loading...</div>}>
                      <TestPage />
                    </Suspense>
                  </ProtectedRoute>
                }
              />
              {/* Add other routes here as needed */}
            </Routes>
          </RoutesProvider>
        </AuthProvider>
      </Router>
    </ThemeProvider>
  );
}

export default App;
