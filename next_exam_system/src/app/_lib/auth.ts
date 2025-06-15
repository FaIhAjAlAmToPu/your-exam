import { LoginResponse, UserCredentials } from './api';
import api from "./api";
import { ROUTES } from "./routes";
export const login = async (credentials: UserCredentials): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>(ROUTES.API.LOGIN, {
        username: credentials.email,
        password: credentials.password,
    });
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('csrf_token', response.data.csrf_token);
    return response.data;
};

export const register = async (credentials: UserCredentials): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>(ROUTES.API.SIGNUP, credentials);
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('csrf_token', response.data.csrf_token);
    return response.data;
};

export const refreshToken = async (): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>(ROUTES.API.TOKEN_REFRESH);
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('csrf_token', response.data.csrf_token);
    return response.data;
};

export const logout = async (): Promise<void> => {
    await api.post('/auth/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('csrf_token');
};