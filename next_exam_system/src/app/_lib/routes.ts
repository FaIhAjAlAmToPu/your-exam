const BASE_API_URL = process.env.BACKEND_API_URL;

export const ROUTES = {
    SIGNUP: '/signup',
    LOGIN: '/login',
    DASHBOARD: '/dashboard',
    HOME: '/',
    CREATE_EXAM: '/exam/create',
    EXAM_CENTER: '/exam/center',
    API: {
        BASE_URL: BASE_API_URL,
        SIGNUP: `${BASE_API_URL}/auth/register`,
        LOGIN: `${BASE_API_URL}/auth/login`,
        TOKEN_REFRESH: `${BASE_API_URL}/auth/refresh`,
        GENERATE_EXAM: `${BASE_API_URL}/exam/generate`
    },
} as const;
