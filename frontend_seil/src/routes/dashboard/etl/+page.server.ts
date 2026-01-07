import type { PageServerLoad } from './$types';
import { getHistory } from '$lib/services/etl.service';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ cookies, locals }) => {
    // 1. Obtener token desde las cookies
    const token = cookies.get('access_token');

    if (!token) {
        // Si no hay sesión, redirigir al login
        throw redirect(302, '/login');
    }

    // Obtener rol del usuario desde locals (establecido en hooks.server.ts)
    const userRole = locals.user?.rol || 'USER';

    try {
        // 2. Llamar al backend para obtener el historial
        const historialData = await getHistory(token);

        return {
            historial: historialData.history || [],
            logs: historialData.recent_logs || [],
            user: {
                nombre: cookies.get('user_nombre') || 'Administrador',
                rol: userRole
            },
            // Pasar el token al cliente para que pueda hacer requests
            token: token
        };
    } catch (error) {
        console.error('Error cargando datos ETL:', error);

        // En caso de error, devolver datos vacíos
        return {
            historial: [],
            logs: [],
            user: { nombre: 'Administrador', rol: userRole },
            error: 'No se pudo cargar el historial de ejecuciones',
            token: token  // Pasar el token incluso si falla
        };
    }
};