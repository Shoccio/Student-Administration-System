import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/';

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('supabase_token') || sessionStorage.getItem('supabase_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Add response interceptor to handle auth errors
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Don't redirect on login endpoint - let the component handle it
            if (error.config?.url !== '/auth/login') {
                // Token expired or invalid - redirect to login
                localStorage.removeItem('supabase_token');
                localStorage.removeItem('user_profile');
                sessionStorage.removeItem('supabase_token');
                sessionStorage.removeItem('user_profile');
                window.location.href = '/';
            }
        }
        return Promise.reject(error);
    }
);

export default apiClient;
