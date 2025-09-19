/**
 * Service for ticket-related API calls
 */
import axios from 'axios';

// Base API URL - would typically come from environment variables
const API_BASE_URL = '/api/v1';
const API_URL = 'http://localhost:8000/api';

// Fallback data for development/testing
const fallbackClassifications = {
  categories: [
    { name: 'Hardware', count: 35, icon: 'Computer', color: '#3b82f6' },
    { name: 'Software', count: 42, icon: 'Code', color: '#10b981' },
    { name: 'Network', count: 28, icon: 'Wifi', color: '#f59e0b' },
    { name: 'Security', count: 15, icon: 'Security', color: '#ef4444' },
    { name: 'Account', count: 20, icon: 'Person', color: '#8b5cf6' },
  ],
  priorities: [
    { name: 'Low', count: 18, color: '#10b981' },
    { name: 'Medium', count: 27, color: '#f59e0b' },
    { name: 'High', count: 34, color: '#ef4444' },
    { name: 'Critical', count: 12, color: '#dc2626' },
  ],
  statuses: [
    { name: 'Open', count: 45, color: '#3b82f6' },
    { name: 'In Progress', count: 30, color: '#f59e0b' },
    { name: 'Resolved', count: 25, color: '#10b981' },
    { name: 'Closed', count: 15, color: '#6b7280' },
  ]
};

// Predefined categories for classification
const predefinedCategories = {
  categoryOne: 'Hardware',
  categoryTwo: 'Software',
  categoryThree: 'Network'
};

// Ticket service functions
const ticketService = {
  // Fetch ticket classifications
  getTicketClassifications: async () => {
    try {
      const response = await axios.get(`${API_URL}/classifications`);
      return response.data;
    } catch (error) {
      console.error('Error fetching ticket classifications:', error);
      // Return fallback data if API call fails
      return fallbackClassifications;
    }
  },
  
  // Alias for getTicketClassifications to maintain compatibility
  fetchTicketClassifications: async () => {
    try {
      const response = await axios.get(`${API_URL}/classifications`);
      return response.data;
    } catch (error) {
      console.error('Error fetching ticket classifications:', error);
      // Return fallback data if API call fails
      return fallbackClassifications;
    }
  },
  
  // Classify a message using the AI service
  classifyMessage: async (message) => {
    try {
      const response = await axios.post(`${API_URL}/classifications/classify-message`, { message });
      return response.data.category;
    } catch (error) {
      console.error('Error classifying message:', error);
      // Simple fallback classification logic
      if (message.toLowerCase().includes('hardware') || 
          message.toLowerCase().includes('computer') || 
          message.toLowerCase().includes('device')) {
        return predefinedCategories.categoryOne;
      } else if (message.toLowerCase().includes('software') || 
                message.toLowerCase().includes('program') || 
                message.toLowerCase().includes('application')) {
        return predefinedCategories.categoryTwo;
      } else {
        return predefinedCategories.categoryThree;
      }
    }
  },

  /**
   * Create a new ticket
   * @param {Object} ticketData - The ticket data
   * @returns {Promise<Object>} The created ticket
   */
  createTicket: async (ticketData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/tickets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(ticketData),
      });
      
      if (!response.ok) {
        throw new Error(`Error creating ticket: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to create ticket:', error);
      throw error;
    }
  },

  /**
   * Fetch tickets with optional filtering
   * @param {Object} filters - Optional filters
   * @param {number} page - Page number
   * @param {number} limit - Items per page
   * @returns {Promise<Object>} Paginated tickets
   */
  fetchTickets: async (filters = {}, page = 1, limit = 10) => {
    try {
      const queryParams = new URLSearchParams({
        page,
        limit,
        ...filters
      });
      
      const response = await fetch(`${API_BASE_URL}/tickets?${queryParams}`);
      
      if (!response.ok) {
        throw new Error(`Error fetching tickets: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch tickets:', error);
      throw error;
    }
  }
};

export default ticketService;