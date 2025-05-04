import api from './api';

export const adminService = {
  getAllUsersWorkData: async () => {
    try {
      const response = await api.get('/api/admin/work-data');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  updateUserAdminData: async (userId, userData) => {
    try {
      const response = await api.put(`/api/admin/users/${userId}`, userData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getDepartments: async () => {
    try {
      const response = await api.get('/api/departments');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};