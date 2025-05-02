import api from './api';

export const authService = {
  login: async (login, password) => {
    try {
      const response = await api.post('/api/login', { login, password });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  register: async (userData) => {
    try {
      const response = await api.post('/api/register', userData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  logout: async () => {
    try {
      const response = await api.post('/api/logout');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getMe: async () => {
    try {
      const response = await api.get('/api/me');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getRecoveryHint: async (username) => {
    try {
      const response = await api.get(`/auth/recovery-hint?username=${username}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  recoverPassword: async (username, recoveryWord, newPassword) => {
    try {
      const response = await api.post('/api/recover-password', {
        username,
        recovery_word: recoveryWord,
        new_password: newPassword
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};