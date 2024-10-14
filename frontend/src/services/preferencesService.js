// services/preferencesService.js

// Save preferences for a specific resource (like 'studentGroup' or 'quiz')
export const saveUserPreferences = (resource, preferences) => {
    const currentPrefs = JSON.parse(localStorage.getItem('userPreferences')) || {};
    currentPrefs[resource] = preferences;
    localStorage.setItem('userPreferences', JSON.stringify(currentPrefs));
  };
  
  // Get preferences for a specific resource
  export const getUserPreferences = (resource) => {
    const currentPrefs = JSON.parse(localStorage.getItem('userPreferences')) || {};
    console.log("Retrieved saved preferences:", currentPrefs);
    return currentPrefs[resource] || {};
  };
  
  // Remove preferences for a specific resource
  export const removeUserPreferences = (resource) => {
    const currentPrefs = JSON.parse(localStorage.getItem('userPreferences')) || {};
    delete currentPrefs[resource];
    localStorage.setItem('userPreferences', JSON.stringify(currentPrefs));
  };
  