import { apiRequest } from '../api/client';
import type {
    UserStatsResponse,
    UserListResponse,
    UserCreateRequest,
    UserUpdateRequest,
    PasswordResetRequest
} from '../types/api';

export const adminService = {
    async getUserStats(token?: string): Promise<UserStatsResponse> {
        return await apiRequest<UserStatsResponse>('/api/v1/admin/users/stats', {}, token);
    },

    async getUsers(token?: string): Promise<UserListResponse> {
        return await apiRequest<UserListResponse>('/api/v1/admin/users', {}, token);
    },

    async createUser(data: UserCreateRequest, token?: string): Promise<{ message: string }> {
        return await apiRequest<{ message: string }>('/api/v1/admin/users', {
            method: 'POST',
            body: data,
        }, token);
    },

    async updateUser(userId: string, data: UserUpdateRequest, token?: string): Promise<{ message: string }> {
        return await apiRequest<{ message: string }>(`/api/v1/admin/users/${userId}`, {
            method: 'PUT',
            body: data,
        }, token);
    },

    async deactivateUser(userId: string, token?: string): Promise<{ message: string }> {
        return await apiRequest<{ message: string }>(`/api/v1/admin/users/${userId}`, {
            method: 'DELETE',
        }, token);
    },

    async resetPassword(userId: string, data: PasswordResetRequest, token?: string): Promise<{ message: string }> {
        return await apiRequest<{ message: string }>(`/api/v1/admin/users/${userId}/reset-password`, {
            method: 'POST',
            body: data,
        }, token);
    }
};
