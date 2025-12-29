<!-- src/routes/login/+page.svelte -->
<script lang="ts">
    import { enhance } from '$app/forms';
    import { goto } from '$app/navigation';
    
    // Recibir datos del servidor
    let { data } = $props();
    
    // Estados para el formulario
    let email = $state('');
    let password = $state('');
    let rememberMe = $state(false);
    let isLoading = $state(false);
    let errorMessage = $state('');
    let successMessage = $state('');
    
    // Función para resetear el formulario
    function resetForm() {
      email = '';
      password = '';
      rememberMe = false;
      errorMessage = '';
      successMessage = '';
    }
    
    // Función para cerrar sesión
    async function handleLogout() {
      isLoading = true;
      try {
        const response = await fetch('/login?/logout', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        });
        // La redirección se manejará automáticamente
        window.location.href = '/login';
      } catch (error) {
        console.error('Error al cerrar sesión:', error);
        isLoading = false;
      }
    }
  </script>
  
  <div class="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Logo y título -->
      <div class="text-center mb-10">
        <div class="inline-flex items-center justify-center mb-6">
          <div class="w-16 h-16 bg-gradient-to-br from-red-600 to-red-700 rounded-2xl flex items-center justify-center shadow-2xl">
            <span class="text-2xl font-bold text-white">LA</span>
          </div>
        </div>
        <h1 class="text-4xl font-bold text-white mb-2">Luckia Analytics</h1>
        <p class="text-gray-400">Sistema interno de análisis de datos</p>
        <div class="mt-4 inline-flex items-center px-4 py-2 rounded-full bg-red-900/30 text-red-400 text-sm font-medium">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          Acceso Restringido - Personal Autorizado
        </div>
      </div>

      <!-- Aviso si hay sesión activa -->
      {#if data.hasSession && data.user}
        <div class="mb-6 p-4 rounded-xl bg-yellow-900/30 border border-yellow-700/50 text-yellow-400">
          <div class="flex items-center justify-between flex-wrap gap-3">
            <div class="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.998-.833-2.732 0L4.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <span class="text-sm">Ya hay una sesión activa como: <strong>{data.user.nombre}</strong> ({data.user.email})</span>
            </div>
            <form method="POST" action="?/logout" use:enhance>
              <button
                type="submit"
                class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
                disabled={isLoading}
              >
                Cerrar Sesión
              </button>
            </form>
          </div>
        </div>
      {/if}

      <!-- Tarjeta del formulario -->
      <div class="bg-gradient-to-br from-gray-900/90 to-gray-800/90 rounded-2xl border border-gray-700 shadow-2xl overflow-hidden">
        <div class="p-8">
          <h2 class="text-2xl font-bold text-white mb-1">Iniciar Sesión</h2>
          <p class="text-gray-400 mb-8">Ingrese sus credenciales para acceder al sistema</p>
          
          <!-- Mensaje de éxito -->
          {#if successMessage}
            <div class="mb-6 p-4 rounded-xl bg-green-900/30 border border-green-700/50 text-green-400">
              <div class="flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{successMessage}</span>
              </div>
            </div>
          {/if}
          
          <!-- Mensaje de error -->
          {#if errorMessage}
            <div class="mb-6 p-4 rounded-xl bg-red-900/30 border border-red-700/50 text-red-400">
              <div class="flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.998-.833-2.732 0L4.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                <span>{errorMessage}</span>
              </div>
            </div>
          {/if}
          
          <!-- Formulario -->
          <form 
            method="POST" 
            action="?/login" 
            use:enhance={({ formData }) => {
              isLoading = true;
              errorMessage = '';
              successMessage = '';
              return async ({ result, update }) => {
                // CASO REDIRECT (Aquí estaba el problema)
                if (result.type === 'redirect') {
                  successMessage = '✅ Iniciando sesión...';
                  // No pongas isLoading = false aquí, deja que siga "cargando" mientras cambia de página
                  
                  // IMPORTANTE: Ejecutar la navegación explícitamente
                  await goto(result.location); 
                  return;
                }
                
                if (result.type === 'failure' || result.type === 'error') {
                  const data = result.type === 'failure' ? result.data : null;
                  errorMessage = (data as any)?.message || '❌ Error al iniciar sesión. Verifique sus credenciales.';
                  successMessage = '';
                } else if (result.type === 'success') {
                  // Tu lógica existente para success...
                  const data = result.data as any;
                  if (data?.success === false) {
                    errorMessage = data.message || '❌ Error al iniciar sesión.';
                    successMessage = '';
                  } else {
                    successMessage = '✅ Sesión iniciada correctamente';
                    errorMessage = '';
                  }
                }
                
                await update();
                isLoading = false;
              };
            }}
            class="space-y-6"
          >
            <div>
              <label for="email" class="block text-sm font-medium text-gray-300 mb-2">
                Correo Electrónico
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                  </svg>
                </div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  bind:value={email}
                  class="w-full bg-gray-800 border border-gray-700 rounded-xl pl-10 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-colors"
                  placeholder="usuario@luckia.cl"
                  required
                  aria-label="Correo electrónico"
                  disabled={isLoading}
                />
              </div>
            </div>
            
            <div>
              <label for="password" class="block text-sm font-medium text-gray-300 mb-2">
                Contraseña
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <input
                  id="password"
                  name="password"
                  type="password"
                  bind:value={password}
                  class="w-full bg-gray-800 border border-gray-700 rounded-xl pl-10 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-colors"
                  placeholder="••••••••"
                  required
                  aria-label="Contraseña"
                  disabled={isLoading}
                />
              </div>
            </div>
            
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  bind:checked={rememberMe}
                  class="h-4 w-4 text-red-600 bg-gray-800 border-gray-700 rounded focus:ring-red-500 focus:ring-offset-gray-900"
                  aria-label="Recordar mis datos"
                  disabled={isLoading}
                />
                <label for="remember-me" class="ml-2 block text-sm text-gray-300">
                  Recordar mis datos
                </label>
              </div>
              
              <a 
                href="/forgot-password" 
                class="text-sm text-red-400 hover:text-red-300 transition-colors"
                aria-label="¿Olvidó su contraseña?"
              >
                ¿Olvidó su contraseña?
              </a>
            </div>
            
            <div class="space-y-4">
              <button
                type="submit"
                class="w-full py-3.5 px-4 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl hover:-translate-y-0.5 flex items-center justify-center disabled:opacity-70 disabled:cursor-not-allowed"
                disabled={isLoading}
                aria-label={isLoading ? 'Iniciando sesión...' : 'Iniciar sesión'}
              >
                {#if isLoading}
                  <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Iniciando sesión...
                {:else}
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                  </svg>
                  Iniciar Sesión
                {/if}
              </button>
              
              <button
                type="button"
                onclick={resetForm}
                class="w-full py-3 px-4 bg-gray-800 hover:bg-gray-700 text-gray-300 font-medium rounded-xl transition-colors border border-gray-700"
                disabled={isLoading}
                aria-label="Limpiar formulario"
              >
                Limpiar Formulario
              </button>
              
              <!-- Link de vuelta a inicio -->
              <a
                href="/"
                class="w-full py-3 px-4 bg-transparent hover:bg-gray-800/50 text-gray-400 font-medium rounded-xl transition-colors border border-gray-700 flex items-center justify-center"
                aria-label="Volver a la página de inicio"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Volver al inicio
              </a>
            </div>
          </form>
        </div>
        
        <!-- Pie de la tarjeta -->
        <div class="px-8 py-6 bg-gradient-to-r from-gray-900 to-gray-800 border-t border-gray-700">
          <div class="text-center">
            <p class="text-sm text-gray-400">
              ¿Necesita acceso al sistema?
              <a href="/contact-admin" class="text-red-400 hover:text-red-300 font-medium ml-1 transition-colors">
                Contacte al administrador
              </a>
            </p>
          </div>
        </div>
      </div>
      
      <!-- Footer -->
      <div class="mt-10 text-center">
        <p class="text-gray-500 text-sm">
          Luckia Analytics • Sistema interno v1.0
        </p>
        <p class="text-gray-600 text-xs mt-2">
          © {new Date().getFullYear()} Luckia Casino. Todos los derechos reservados.
        </p>
      </div>
    </div>
  </div>
  
  <style>
    /* Animación de fade in para la página */
    @keyframes fadeIn {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    
    div:first-child {
      animation: fadeIn 0.5s ease-out;
    }
    
    /* Estilos para los inputs con estado de foco mejorado */
    input:focus {
      box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
    }
    
    /* Efecto de transición para la tarjeta */
    .bg-gradient-to-br {
      transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .bg-gradient-to-br:hover {
      transform: translateY(-2px);
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
  </style>