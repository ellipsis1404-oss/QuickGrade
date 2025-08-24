// frontend/src/api/config.js
import axios from 'axios';

// This is now the ONLY place where the API URL is defined.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/';

// Create a pre-configured axios instance.
// All requests made with 'apiClient' will automatically use the correct base URL.
const apiClient = axios.create({
    baseURL: API_BASE_URL
});

export default apiClient;