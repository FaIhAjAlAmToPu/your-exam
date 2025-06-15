import axios from 'axios';
import { ROUTES } from "./routes";

export interface LoginResponse {
    access_token: string;
    token_type: string;
    csrf_token: string;
}

export interface UserCredentials {
    email: string;
    password: string;
}

export interface UserCreate {
    username: string;
    email: string;
    password: string;
}



const api = axios.create({
    baseURL: ROUTES.API.BASE_URL,
    withCredentials: true,
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    const csrfToken = localStorage.getItem('csrf_token');
    if (csrfToken && ['POST', 'PUT', 'DELETE'].includes(config.method?.toUpperCase() || '')) {
        config.headers['X-CSRF-Token'] = csrfToken;
    }
    return config;
});

export default api;