// src/hooks.server.ts
import { redirect } from '@sveltejs/kit';
import type { Handle } from '@sveltejs/kit';

// Rutas accesibles sin necesidad de haber iniciado sesión
const publicRoutes = ['/', '/login', '/about'];

export const handle: Handle = async ({ event, resolve }) => {
  const session = event.cookies.get('session');
  const pathname = event.url.pathname;

  console.log(`[HOOK] Request for: ${pathname} | Cookie found: ${!!session}`);

  const isPublicRoute = publicRoutes.some(route =>
    pathname === route || (route !== '/' && pathname.startsWith(route + '/'))
  );

  let user = null;

  // Función auxiliar para limpiar cookies en múltiples paths
  const clearAllCookies = () => {
    const paths = ['/', '/dashboard/home', '/dashboard'];
    paths.forEach(p => {
      event.cookies.delete('session', { path: p });
      event.cookies.delete('access_token', { path: p });
    });
  };

  if (session) {
    try {
      const parsed = JSON.parse(session);
      if (parsed && typeof parsed === 'object' && parsed.loggedIn === true) {
        user = parsed;
        event.locals.user = user;

        // Si el cookie se encontró pero estamos moviéndonos, 
        // nos aseguramos de que los cookies de subpath no interfieran.
        // Solo dejamos el del root.
        if (pathname === '/dashboard/home') {
          // Intentamos borrar el de este path específico para que no "gane" al del root
          event.cookies.delete('session', { path: '/dashboard/home' });
        }
      } else {
        throw new Error('Sesión inválida (sin flag loggedIn)');
      }
    } catch (error: any) {
      console.error(`[HOOK] Error parseando sesión: ${error.message}. Limpiando...`);
      clearAllCookies();
    }
  }

  // 1. Redirección para usuarios NO autenticados
  if (!user && !isPublicRoute) {
    console.log(`[HOOK] !!! BLOQUEADO: ${pathname} !!! Redirigiendo a /login`);
    clearAllCookies(); // Asegurarnos de limpiar todo antes de redirigir
    throw redirect(303, '/login');
  }

  // 2. Redirección para usuarios SÍ autenticados
  if (user) {
    // Solo redirigir fuera del login si es una petición de navegación (GET)
    // Esto permite que el los POST actions (como el logout) funcionen
    if (pathname === '/login' && event.request.method === 'GET') {
      console.log('[HOOK] Usuario ya autenticado. Redirigiendo al dashboard.');
      throw redirect(303, '/dashboard/home');
    }


    if (pathname.startsWith('/dashboard/usuarios') && user.rol !== 'ADMIN') {
      console.warn(`[HOOK] RBAC: Usuario ${user.email} bloqueado en /usuarios`);
      throw redirect(303, '/dashboard/home');
    }
  }

  return resolve(event);
};
