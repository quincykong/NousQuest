import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { isTokenValid } from '../utils/jwtUtils';

const TokenValidation = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const isValid = isTokenValid();
    console.log(`isValid token: ${isValid}`)
    if (isValid) {
      // If token is valid, redirect to the home screen
      navigate("/home");
    } else {
      // If token is invalid or expired, redirect to login page
      navigate("/login");
    }
  }, [navigate]);

  return null; // This component doesn't render anything
};

export default TokenValidation;
