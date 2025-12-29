// src/routes/login/+page.server.ts
import { redirect, fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { authService } from '$lib/services/auth.service';

// Cargar datos de la página de login
export const load: PageServerLoad = async () => {
  return {
    seo: {
      title: 'Login - Luckia Analytics',
      description: 'Sistema interno de análisis de datos del Casino Luckia'
    }
  };
};


export const actions: Actions = {
  login: async ({ request, cookies }) => {
    const formData = await request.formData();
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;
    const rememberMe = formData.get('remember-me') === 'on';

    console.log(`[LOGIN ACTION] Attempting login for: ${email}, rememberMe: ${rememberMe}`);

    if (!email || !password) {
      return fail(400, {
        success: false,
        message: 'Por favor, complete todos los campos'
      });
    }

    try {
      // En el backend, 'email' se usa como 'username' según LoginRequest
      const tokenResponse = await authService.login({
        email: email,
        password: password
      });

      const token = tokenResponse.access_token;

      // Intentar obtener información del usuario
      let userInfo;
      try {
        userInfo = await authService.getMe(token);
      } catch (e) {
        console.warn('Could not fetch user profile, using default:', e);
        userInfo = {
          name: email.split('@')[0],
          email: email,
          role: 'USER',
          id: 'unknown'
        };
      }

      // Crear sesión con datos reales
      const sessionData = {
        id: userInfo.id,
        email: userInfo.email || email,
        nombre: userInfo.name || userInfo.username || email.split('@')[0],
        rol: userInfo.role || 'Analista', // Fallback a Analista si no hay rol
        token: token,
        loggedIn: true,
        timestamp: Date.now()
      };

      // Establecer cookie de sesión
      cookies.set('session', JSON.stringify(sessionData), {
        path: '/',
        httpOnly: true,
        sameSite: 'strict',
        secure: process.env.NODE_ENV === 'production',
        maxAge: rememberMe ? 60 * 60 * 24 * 7 : 60 * 60 * 24 // 7 días o 1 día
      });

      // También establecemos el token por separado para facilitar su uso en hooks si es necesario
      cookies.set('access_token', token, {
        path: '/',
        httpOnly: true,
        sameSite: 'strict',
        secure: process.env.NODE_ENV === 'production',
        maxAge: rememberMe ? 60 * 60 * 24 * 7 : 60 * 60 * 24
      });

    } catch (error: any) {
      console.error('Login error:', error);
      return fail(401, {
        success: false,
        message: error.message || 'Error de autenticación'
      });
    }

    throw redirect(303, '/dashboard/home');
  },

  logout: async ({ cookies }) => {
    const session = cookies.get('session');
    if (session) {
      try {
        const data = JSON.parse(session);
        if (data.token) {
          await authService.logout(data.token);
        }
      } catch (e) {
        console.error('Logout error on API:', e);
      }
    }
    const paths = ['/', '/dashboard', '/dashboard/home'];
    paths.forEach(p => {
      cookies.delete('session', { path: p });
      cookies.delete('access_token', { path: p });
    });
    throw redirect(303, '/login');
  }
};


