// src/routes/dashboard/+layout.server.ts
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
  // Obtener datos del usuario desde locals (establecido en hooks.server.ts)
  const user = locals.user;
  
  // Si no hay usuario, devolver un usuario por defecto para evitar errores
  return {
    user: user ? {
      nombre: user.nombre || 'Usuario',
      email: user.email || '',
      rol: user.rol || 'Usuario',
      id: user.id || ''
    } : {
      nombre: 'Usuario',
      email: '',
      rol: 'Invitado',
      id: ''
    }
  };
};

