<script lang="ts">
  const appName = "Luckia Analytics";
</script>

<svelte:head>
  <title>Luckia Analytics | Plataforma de Datos</title>
  <meta name="description" content="Plataforma de análisis y visualización de datos para Luckia Casino" />
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex flex-col justify-center items-center px-4">
  
  <main class="max-w-2xl text-center space-y-8">
    
    <!-- Logo o nombre de la plataforma -->
    <div class="mb-8">
      <div class="inline-flex items-center space-x-3">
        <div class="w-12 h-12 bg-gradient-to-r from-red-600 to-red-700 rounded-lg flex items-center justify-center shadow-lg">
          <span class="text-white font-bold text-xl">LA</span>
        </div>
        <h1 class="text-3xl font-bold text-white">Luckia Analytics</h1>
      </div>
    </div>

    <!-- Badge simple -->
    <div class="inline-block py-2 px-4 rounded-full bg-gradient-to-r from-red-700 to-red-800 text-white text-sm font-semibold shadow-md">
      Plataforma de Análisis Interno
    </div>

    <!-- Título principal -->
    <h1 class="text-4xl md:text-5xl font-bold text-white tracking-tight">
      Plataforma de <span class="text-red-500">Análisis</span> y <span class="text-red-500">Visualización</span>
    </h1>

    <!-- Descripción -->
    <p class="text-xl text-gray-300 max-w-xl mx-auto">
      Sistema interno para análisis de datos, reportes y dashboards operacionales de Luckia Casino.
    </p>

    <!-- Botones principales -->
    <div class="flex flex-col sm:flex-row gap-4 justify-center pt-8">
      <a 
        href="/login" 
        class="px-10 py-4 rounded-lg bg-gradient-to-r from-red-600 to-red-700 text-white font-medium hover:from-red-700 hover:to-red-800 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 flex items-center justify-center group"
        aria-label="Ir a la página de inicio de sesión"
      >
        <svg class="w-5 h-5 mr-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
        </svg>
        Iniciar Sesión
      </a>
      
      <a 
        href="/about" 
        class="px-10 py-4 rounded-lg bg-gray-800 text-gray-200 border border-gray-700 font-medium hover:bg-gray-700 hover:text-white transition-all duration-300 shadow-md hover:shadow-lg flex items-center justify-center"
      >
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        Saber Más
      </a>
    </div>

    <!-- Información adicional pequeña -->
    <div class="pt-12 border-t border-gray-700 mt-12">
      <p class="text-gray-400 text-sm">
        Acceso restringido al personal autorizado de Luckia Casino
      </p>
      <p class="text-gray-500 text-xs mt-2">
        v1.0 • Sistema Interno de Análisis
      </p>
    </div>

  </main>
</div>

<style>
  /* Estilos adicionales minimalistas */
  :global(body) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
  
  /* Animación sutil para los botones */
  a {
    transition: all 0.2s ease;
  }
</style>