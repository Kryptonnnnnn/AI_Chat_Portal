import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const handleError = (error) => {
  if (error.response) {
    console.error('API Error:', error.response.data);
    throw error.response.data;
  } else if (error.request) {
    console.error('Network Error:', error.request);
    throw { error: 'Network error. Please check your connection.' };
  } else {
    console.error('Error:', error.message);
    throw { error: error.message };
  }
};

export const conversationAPI = {
  getAll: async (params = {}) => {
    try {
      const response = await api.get('/conversations/', { params });
      return response.data;
    } catch (error) {
      handleError(error);
    }
  },
  getTrending: async (days = 30) => {
    try {
      const response = await api.get(`/conversations/trending/?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },
  getById: async (id) => {
    try {
      const response = await api.get(`/conversations/${id}/`);
      return response.data;
    } catch (error) {
      handleError(error);
    }
  },
  sendMessage: async (message, conversationId = null) => {
    try {
      const response = await api.post('/conversations/chat/', {
        message,
        conversation_id: conversationId,
      });
      return response.data;
    } catch (error) {
      handleError(error);
    }
  },
  endConversation: async (id) => {
    try {
      const response = await api.post(`/conversations/${id}/end/`);
      return response.data;
    } catch (error) {
      handleError(error);
    }
  },
  queryConversations: async (query, filters = {}) => {
    try {
      const response = await api.post('/conversations/query/', {
        query,
        ...filters,
      });
      return response.data;
    } catch (error) {
      handleError(error);
    }
  },
  deleteConversation: async (id) => {
    try {
      const response = await api.delete(`/conversations/${id}/`);
      return response.data;
    } catch (error) {
      handleError(error);
    }
  },
};

export default api;