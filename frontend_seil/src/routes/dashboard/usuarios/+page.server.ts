import { redirect, fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { adminService } from '$lib/services/admin.service';

export const load: PageServerLoad = async ({ cookies }) => {
    const accessToken = cookies.get('access_token')!;

    try {
        const stats = await adminService.getUserStats(accessToken);
        const usersResponse = await adminService.getUsers(accessToken);

        return {
            stats,
            users: usersResponse.users
        };
    } catch (error: any) {
        console.error('Error loading users:', error);
        // If unauthorized, redirect to login
        if (error.message?.includes('401') || error.message?.includes('unauthorized')) {
            cookies.delete('session', { path: '/' });
            cookies.delete('access_token', { path: '/' });
            throw redirect(303, '/login');
        }
        return {
            stats: { total_users: 0, active_users: 0, admin_users: 0, last_access: null },
            users: [],
            error: error.message || 'Error al cargar usuarios'
        };
    }
};

export const actions: Actions = {
    createUser: async ({ request, cookies }) => {
        const accessToken = cookies.get('access_token');
        if (!accessToken) throw redirect(303, '/login');

        const formData = await request.formData();
        const data = {
            name: formData.get('name') as string,
            email: formData.get('email') as string,
            username: formData.get('username') as string,
            role: formData.get('role') as string,
            department: formData.get('department') as string || null
        };

        try {
            await adminService.createUser(data, accessToken);
            return { success: true, message: 'Usuario creado correctamente' };
        } catch (error: any) {
            return fail(400, { success: false, message: error.message });
        }
    },

    updateUser: async ({ request, cookies }) => {
        const accessToken = cookies.get('access_token');
        if (!accessToken) throw redirect(303, '/login');

        const formData = await request.formData();
        const userId = formData.get('id') as string;

        const data = {
            name: formData.get('name') as string,
            email: formData.get('email') as string,
            role: formData.get('role') as string,
            department: formData.get('department') as string,
            is_active: formData.get('is_active') === 'true'
        };

        try {
            await adminService.updateUser(userId, data, accessToken);
            return { success: true, message: 'Usuario actualizado correctamente' };
        } catch (error: any) {
            return fail(400, { success: false, message: error.message });
        }
    },

    deactivateUser: async ({ request, cookies }) => {
        const accessToken = cookies.get('access_token');
        if (!accessToken) throw redirect(303, '/login');

        const formData = await request.formData();
        const userId = formData.get('id') as string;

        try {
            await adminService.deactivateUser(userId, accessToken);
            return { success: true, message: 'Usuario desactivado correctamente' };
        } catch (error: any) {
            return fail(400, { success: false, message: error.message });
        }
    },

    resetPassword: async ({ request, cookies }) => {
        const accessToken = cookies.get('access_token');
        if (!accessToken) throw redirect(303, '/login');

        const formData = await request.formData();
        const userId = formData.get('id') as string;
        const newPassword = formData.get('new_password') as string;

        try {
            await adminService.resetPassword(userId, { new_password: newPassword }, accessToken);
            return { success: true, message: 'Contraseña restablecida correctamente' };
        } catch (error: any) {
            return fail(400, { success: false, message: error.message });
        }
    }
};
