import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
    // Si llegamos aquí, hooks.server.ts ya verificó que locals.user existe
    const user = locals.user;

    return {
        user: {
            nombre: locals.user?.nombre || locals.user?.email || 'Usuario',
            rol: locals.user?.rol || 'Analista',
            notificaciones: 0,
            proyectosRecientes: []
        }
    };
};

