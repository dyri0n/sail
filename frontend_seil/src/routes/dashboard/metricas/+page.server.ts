import type { PageServerLoad } from './$types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const load: PageServerLoad = async ({ cookies }) => {
    const token = cookies.get('access_token');

    if (!token) {
        return {
            error: 'No autorizado',
            metrics: null
        };
    }

    try {
        // Obtener todas las métricas del dashboard
        console.log('[Metrics] Fetching dashboard metrics with token:', token ? 'present' : 'missing');

        const response = await fetch(`${API_BASE_URL}/metrics/dashboard`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        console.log('[Metrics] Response status:', response.status, response.statusText);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('[Metrics] Error response:', errorText);
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const metrics = await response.json();
        console.log('[Metrics] Successfully fetched metrics');

        return {
            metrics,
            error: null
        };
    } catch (error) {
        console.error('Error al obtener métricas:', error);
        return {
            error: error instanceof Error ? error.message : 'Error desconocido',
            metrics: null
        };
    }
};
