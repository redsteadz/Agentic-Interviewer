import axios from 'axios';
import { getRefreshToken, isAccessTokenExpired, setAuthUser } from './auth';
import { API_BASE_URL } from './constants';
import Cookies from 'js-cookie';

const useAxios = () => {
    const accessToken = Cookies.get('access_token');
    const refreshToken = Cookies.get('refresh_token');

    const axiosInstance = axios.create({
        baseURL: API_BASE_URL,
        headers: { Authorization: `Bearer ${accessToken}` },
    });

    axiosInstance.interceptors.request.use(async (req) => {
        try {
            if (!isAccessTokenExpired(accessToken)) return req;

            const response = await getRefreshToken(refreshToken);

            setAuthUser(response.access, response.refresh);

            req.headers.Authorization = `Bearer ${response.access}`;
            return req;
        } catch (error) {
            console.error('Token refresh failed:', error);
            // Clear tokens and redirect to login
            Cookies.remove('access_token');
            Cookies.remove('refresh_token');
            window.location.href = '/login';
            return req;
        }
    });

    // Response interceptor to handle errors
    axiosInstance.interceptors.response.use(
        (response) => response,
        (error) => {
            console.error('API Error:', error);
            if (error.response?.status === 401) {
                // Unauthorized - clear tokens and redirect
                Cookies.remove('access_token');
                Cookies.remove('refresh_token');
                window.location.href = '/login';
            }
            return Promise.reject(error);
        }
    );

    return axiosInstance;
};

export default useAxios;
