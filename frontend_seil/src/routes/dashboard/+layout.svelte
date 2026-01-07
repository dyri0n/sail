<script lang="ts">
  import { page, navigating } from '$app/stores';
  import { enhance } from '$app/forms';
  import type { LayoutData } from './$types';

  
  // Usamos $props() en lugar de export let (Svelte 5 runes)
  let { data, children } = $props<{ data: LayoutData; children: any }>();
  let isSidebarOpen = $state(true);
  
  // Determinar el link activo basado en la URL actual
  let activeLink = $derived(() => {
    const pathname = String($page.url.pathname);
    
    // Verificar home primero porque es más específico
    if (pathname === '/dashboard/home' || pathname.startsWith('/dashboard/home/')) {
      return 'dashboard';
    } else if (pathname === '/dashboard/usuarios' || pathname.startsWith('/dashboard/usuarios/')) {
      return 'usuarios';
    } else if (pathname === '/dashboard/etl' || pathname.startsWith('/dashboard/etl/')) {
      return 'etl';
    } else if (pathname === '/dashboard/auditoria' || pathname.startsWith('/dashboard/auditoria/')) {
      return 'auditoria';
    }
    
    return 'dashboard'; // Por defecto
  });
</script>

<div class="flex h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white">
  <!-- Sidebar -->
  <aside class={`${isSidebarOpen ? 'w-64' : 'w-0'} bg-gray-900/80 border-r border-gray-700 transition-all duration-300 overflow-hidden shrink-0 backdrop-blur-sm`}>
    <div class="p-6 border-b border-gray-700">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 bg-gradient-to-br from-red-600 to-red-700 rounded-lg flex items-center justify-center shadow-lg" title="Logo Luckia Analytics" aria-label="Logo Luckia Analytics">
          <span class="text-white font-bold">LA</span>
        </div>
        <h2 class="text-xl font-bold truncate">Luckia Analytics</h2>
      </div>
    </div>
    
    <!-- Menú de navegación -->
    <nav class="mt-6 px-4 space-y-1">
      <a 
        href="/dashboard/home" 
        class={`flex items-center px-4 py-3 rounded-lg transition-all duration-200 whitespace-nowrap ${activeLink() === 'dashboard' ? 'bg-gradient-to-r from-red-600/20 to-red-700/20 text-red-400 border-l-4 border-red-500' : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'}`}
        aria-label="Ir al panel de inicio"
        title="Panel de inicio"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
        Inicio
      </a>
      
      <!-- Solo ADMIN: Gestión de Usuarios -->
      {#if data.user?.rol === 'ADMIN'}
      <a 
        href="/dashboard/usuarios" 
        class={`flex items-center px-4 py-3 rounded-lg transition-all duration-200 whitespace-nowrap ${activeLink() === 'usuarios' ? 'bg-gradient-to-r from-red-600/20 to-red-700/20 text-red-400 border-l-4 border-red-500' : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'}`}
        aria-label="Gestión de Usuarios"
        title="Gestión de Usuarios"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
        Gestión de Usuarios
      </a>
      {/if}
      
      <!-- Ambos roles: Archivos -->
      <a 
        href="/dashboard/directorios" 
        class={`flex items-center px-4 py-3 rounded-lg transition-all duration-200 whitespace-nowrap ${$page.url.pathname.includes('directorios') ? 'bg-gradient-to-r from-red-600/20 to-red-700/20 text-red-400 border-l-4 border-red-500' : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'}`}
        aria-label="Gestión de Archivos"
        title="Archivos"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
        </svg>
        Archivos
      </a>
      
      <!-- Ambos roles: Predicciones -->
      <a 
        href="/dashboard/predicciones" 
        class={`flex items-center px-4 py-3 rounded-lg transition-all duration-200 whitespace-nowrap ${$page.url.pathname.includes('predicciones') ? 'bg-gradient-to-r from-red-600/20 to-red-700/20 text-red-400 border-l-4 border-red-500' : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'}`}
        aria-label="Modelo Predictivo"
        title="Predicciones"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        Predicciones
      </a>
      
      <!-- Ambos roles: ETL -->
      <a 
        href="/dashboard/etl" 
        class={`flex items-center px-4 py-3 rounded-lg transition-all duration-200 whitespace-nowrap ${activeLink() === 'etl' ? 'bg-gradient-to-r from-red-600/20 to-red-700/20 text-red-400 border-l-4 border-red-500' : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'}`}
        aria-label="Ejecutar proceso ETL"
        title="Ejecutar ETL"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
        </svg>
        Ejecutar ETL
      </a>
      
      <!-- Solo ADMIN: Logs y Auditoría -->
      {#if data.user?.rol === 'ADMIN'}
      <a 
        href="/dashboard/auditoria" 
        class={`flex items-center px-4 py-3 rounded-lg transition-all duration-200 whitespace-nowrap ${activeLink() === 'auditoria' ? 'bg-gradient-to-r from-red-600/20 to-red-700/20 text-red-400 border-l-4 border-red-500' : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'}`}
        aria-label="Sistema de Logs y Auditoría"
        title="Logs y Auditoría"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Logs y Auditoría
      </a>
      {/if}
      
    </nav>
    
    <!-- Sección inferior del sidebar -->
    <div class="absolute bottom-0 w-full p-4 border-t border-gray-700 bg-gray-900/90">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 bg-gradient-to-br from-red-600 to-red-700 rounded-full flex items-center justify-center" title="Avatar de usuario" aria-label="Avatar de usuario">
            <span class="text-xs font-bold">
              {data.user?.nombre?.charAt(0) || 'U'}
            </span>
          </div>
          <div>
            <p class="text-sm font-medium truncate">
              {data.user?.nombre || 'Usuario'}
            </p>
            <p class="text-xs text-gray-500 truncate">Sistema Interno</p>
          </div>
        </div>
        <form method="POST" action="/login?/logout" use:enhance>

          <button
            type="submit"

            class="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded-lg transition-colors"
            aria-label="Cerrar sesión"
            title="Cerrar sesión"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  </aside>

  <!-- Contenido principal -->
  <div class="flex-1 flex flex-col overflow-hidden">
    <!-- Header -->
    <header class="h-16 bg-gray-900/70 border-b border-gray-700 flex items-center justify-between px-6 backdrop-blur-sm">
      <div class="flex items-center gap-4">
        <button 
          onclick={() => isSidebarOpen = !isSidebarOpen}
          class="p-2 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white focus:outline-none transition-colors"
          aria-label={isSidebarOpen ? "Ocultar menú lateral" : "Mostrar menú lateral"}
          title={isSidebarOpen ? "Ocultar menú" : "Mostrar menú"}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <div class="hidden md:block">
          <span class="text-gray-400">Panel de análisis •</span>
          <span class="ml-2 text-red-400 font-medium">Luckia Casino</span>
        </div>
      </div>
      
      <div class="flex items-center space-x-4">
        <!-- Notificaciones -->
        <button 
          class="relative p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
          aria-label="Notificaciones"
          title="Notificaciones"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <span class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" aria-label="Notificaciones no leídas" title="Notificaciones pendientes"></span>
        </button>
        
        <!-- Avatar de usuario -->
        <div 
          class="w-8 h-8 bg-gradient-to-br from-red-600 to-red-700 rounded-full flex items-center justify-center shadow-lg cursor-pointer hover:scale-105 transition-transform"
          title={`Perfil de ${data.user?.nombre || 'Usuario'}`}
          aria-label={`Perfil de ${data.user?.nombre || 'Usuario'}`}
          role="button"
          tabindex="0"
        >
          <span class="text-sm font-bold">
            {data.user?.nombre?.charAt(0) || 'U'}
          </span>
        </div>
      </div>
    </header>

    <!-- Contenido principal -->
    <main class="flex-1 overflow-x-hidden overflow-y-auto p-4 md:p-6">
      <div class="max-w-7xl mx-auto">
        {@render children()}
      </div>
    </main>
    
    <!-- Footer del contenido -->
    <footer class="py-4 px-6 border-t border-gray-700 text-center text-gray-500 text-sm bg-gray-900/50">
      <p>Luckia Analytics • Sistema interno de análisis de datos • v1.0</p>
      <p class="text-xs mt-1 text-gray-600">© {new Date().getFullYear()} Luckia Casino. Todos los derechos reservados.</p>
    </footer>
  </div>
</div>

<style>
  /* Personalización de scrollbar */
  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  
  ::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
  }
  
  ::-webkit-scrollbar-thumb {
    background: rgba(239, 68, 68, 0.5);
    border-radius: 4px;
  }
  
  ::-webkit-scrollbar-thumb:hover {
    background: rgba(239, 68, 68, 0.7);
  }
  
  /* Efectos de transición suaves */
  * {
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  
  /* Estilo para links activos */
  a.active {
    background: linear-gradient(90deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.2));
    color: rgb(248, 113, 113);
    border-left: 4px solid rgb(239, 68, 68);
  }
</style>