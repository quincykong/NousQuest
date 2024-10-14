import React, { Suspense } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import LoginForm from './features/auth/LoginForm';
import ForgotPasswordForm from './features/auth/ForgotPasswordForm';
import { RoutesProvider } from './contexts/RoutesContext';
import { AuthProvider } from './contexts/AuthProvider';
import ProtectedRoute from './components/ProtectedRoute';
import StudentGroupList from './features/group/StudentGroupList';
import Debug from './components/debug';

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
              <Route path="/login" element={<LoginForm />} />
              <Route path="/forgot-password" element={<ForgotPasswordForm />} />
              <Route path="/home" element={
                  <ProtectedRoute>
                    <Suspense fallback={<div>Loading...</div>}>
                      <TestPage />
                    </Suspense>
                  </ProtectedRoute>
                }
              />
              <Route path="/student" element={<StudentGroupList />} />
              <Route path="/debug" element={<Debug />} />
              {/* Add other routes here as needed */}
            </Routes>
          </RoutesProvider>
        </AuthProvider>
      </Router>
    </ThemeProvider>
  );
}

export default App;
