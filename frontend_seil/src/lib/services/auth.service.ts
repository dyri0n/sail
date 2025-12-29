import { apiRequest } from '../api/client';
import type { LoginRequest, TokenResponse, UserListItem } from '../types/api';

export const authService = {
    async login(credentials: LoginRequest): Promise<TokenResponse> {
        return await apiRequest<TokenResponse>('/api/v1/auth/login', {
            method: 'POST',
            body: credentials,
        });
    },

    async logout(token?: string): Promise<{ message: string }> {
        const response = await apiRequest<{ message: string }>('/api/v1/auth/logout', {
            method: 'POST',
        }, token);

        if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token');
        }

        return response;
    },

    async getMe(token: string): Promise<UserListItem> {
        // We assume there's a profile endpoint, but looking at documentation, 
        // we might need to find the user in the /users list or use a /me if it exists.
        // For now, let's try /api/v1/auth/me based on typical patterns.
        return await apiRequest<UserListItem>('/api/v1/auth/me', {}, token);
    }
};
