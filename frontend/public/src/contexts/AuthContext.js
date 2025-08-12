import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('auth_token'));
  const [loading, setLoading] = useState(true);

  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

  // Initialize auth state from localStorage
  useEffect(() => {
    const savedUser = localStorage.getItem('auth_user');
    const savedToken = localStorage.getItem('auth_token');
    
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erreur de connexion');
      }

      const data = await response.json();
      
      // Save to state and localStorage
      setToken(data.access_token);
      setUser({
        user_id: data.user_id,
        profile: data.user_profile
      });
      
      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('auth_user', JSON.stringify({
        user_id: data.user_id,
        profile: data.user_profile
      }));

      return { success: true, message: data.message };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, message: error.message };
    }
  };

  const register = async (userData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erreur d\'inscription');
      }

      const data = await response.json();
      
      // Auto-login after registration
      setToken(data.access_token);
      setUser({
        user_id: data.user_id,
        profile: {
          email: userData.email,
          first_name: userData.first_name,
          last_name: userData.last_name,
          phone: userData.phone
        }
      });
      
      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('auth_user', JSON.stringify({
        user_id: data.user_id,
        profile: {
          email: userData.email,
          first_name: userData.first_name,
          last_name: userData.last_name,
          phone: userData.phone
        }
      }));

      return { success: true, message: data.message, data };
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, message: error.message };
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await fetch(`${API_BASE_URL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear state and localStorage
      setToken(null);
      setUser(null);
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
    }
  };

  const getAuthHeaders = () => {
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  };

  const apiCall = async (endpoint, options = {}) => {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
    
    const headers = {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...options.headers,
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (response.status === 401) {
        // Token expired or invalid
        logout();
        throw new Error('Session expirée, veuillez vous reconnecter');
      }

      return response;
    } catch (error) {
      console.error('API call error:', error);
      throw error;
    }
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    getAuthHeaders,
    apiCall,
    isAuthenticated: !!token && !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};