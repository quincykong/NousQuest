import { useEffect, useState, useRef } from 'react';
import { saveUserPreferences, getUserPreferences } from '../services/preferencesService';

const useUserPreferences = (resourceName, defaultPreferences) => {
  const [preferences, setPreferences] = useState(defaultPreferences);
  const isInitialLoadRef = useRef(true);  // Use ref to track the initial load

  useEffect(() => {
    if (isInitialLoadRef.current) {
      const savedPreferences = getUserPreferences(resourceName);

      // If saved preferences exist, merge them with default preferences
      if (savedPreferences) {
        setPreferences((prev) => ({ ...prev, ...savedPreferences }));
      }

      // Mark initial load as complete
      isInitialLoadRef.current = false;
    }
  }, [resourceName]);

  useEffect(() => {
    // Save preferences only after the initial load is complete
    if (!isInitialLoadRef.current) {
      saveUserPreferences(resourceName, preferences);
    }
  }, [preferences, resourceName]);

  return [preferences, setPreferences, isInitialLoadRef.current];
};

export default useUserPreferences;
