<script lang="ts">
  // Definir interfaces para los datos
  interface HistorialItem {
    id?: number; // Agregado opcional según tu server.ts
    fecha: string;
    estado: 'Exitoso' | 'Fallido';
    duracion: string;
  }

  interface LogItem {
    timestamp: string;
    nivel: 'INFO' | 'WARN' | 'SUCCESS' | 'ERROR';
    mensaje: string;
  }

  interface EtlData {
    historial: HistorialItem[];
    logs: LogItem[];
    user?: {
      nombre: string;
    };
  }

  // Tipar la prop data
  export let data: EtlData;

  let isRunning = false;
  let progress = 0;

  function runEtl() {
    isRunning = true;
    progress = 0;
    
    // Simulación de progreso
    const interval = setInterval(() => {
      progress += Math.random() * 15;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        setTimeout(() => {
          isRunning = false;
          progress = 0;
        }, 1000);
      }
    }, 300);
  }
</script>

<div class="flex flex-col gap-4 lg:gap-6 w-full min-h-full">
  
  <div class="bg-gradient-to-r from-gray-900/80 to-gray-800/80 rounded-2xl border border-gray-700 p-4 lg:p-6 shrink-0">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl lg:text-3xl font-bold text-white mb-1 lg:mb-2">Proceso ETL</h1>
        <p class="text-gray-300 text-sm lg:text-base">Extracción, Transformación y Carga de datos del casino</p>
      </div>
      <div class="text-left sm:text-right bg-gray-800/50 p-2 rounded-lg sm:bg-transparent sm:p-0">
        <p class="text-xs text-gray-400 uppercase tracking-wider">Usuario activo</p>
        <p class="text-base lg:text-lg font-medium text-white">{data.user?.nombre || 'Administrador'}</p>
      </div>
    </div>
  </div>

  <div class="flex flex-col lg:flex-row gap-4 lg:gap-6">
    
    <div class="bg-gradient-to-br from-gray-900/90 to-gray-800/90 rounded-2xl border border-gray-700 flex-1 flex flex-col items-center justify-center text-center shadow-xl p-6 lg:p-8 min-h-[400px] lg:min-h-[500px]">
      
      <div class="h-16 w-16 lg:h-20 lg:w-20 bg-gradient-to-br from-red-600/20 to-red-700/20 rounded-2xl flex items-center justify-center mb-4 lg:mb-6 border border-red-600/20 shrink-0">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 lg:h-10 lg:w-10 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
        </svg>
      </div>
      
      <h2 class="text-xl lg:text-2xl font-bold text-white mb-2 lg:mb-3">Ejecución del ETL</h2>
      
      <p class="text-gray-400 mb-6 lg:mb-8 max-w-md text-sm lg:text-lg">
        Inicia el proceso de Extracción, Transformación y Carga de datos operacionales.
      </p>
      
      {#if isRunning}
        <div class="w-full max-w-sm mb-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div class="flex justify-between text-sm text-gray-300 mb-2">
            <span>Progreso</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div class="h-2 bg-gray-700 rounded-full overflow-hidden">
            <div 
              class="h-full bg-gradient-to-r from-red-600 to-red-500 transition-all duration-300"
              style={`width: ${progress}%`}
              role="progressbar"
              aria-valuenow={progress}
              aria-valuemin="0"
              aria-valuemax="100"
            ></div>
          </div>
        </div>
      {/if}
      
      <button 
        on:click={runEtl}
        disabled={isRunning}
        class="group relative inline-flex items-center justify-center px-8 py-3 lg:px-10 lg:py-4 text-base lg:text-lg font-semibold text-white transition-all duration-300 rounded-xl w-full sm:w-auto
          {isRunning 
            ? 'bg-gray-700 cursor-not-allowed' 
            : 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 shadow-xl hover:shadow-2xl hover:-translate-y-1'
          }"
      >
        {#if isRunning}
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 lg:h-6 lg:w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Ejecutando...
        {:else}
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 lg:h-6 lg:w-6 mr-2 lg:mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Iniciar Proceso
        {/if}
      </button>

      {#if isRunning}
        <p class="mt-4 lg:mt-6 text-xs lg:text-sm text-red-400 animate-pulse flex items-center justify-center">
          <svg class="w-3 h-3 lg:w-4 lg:h-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Procesando datos...
        </p>
      {/if}
    </div>

    <div class="w-full lg:w-80 xl:w-96 bg-gradient-to-br from-gray-900/90 to-gray-800/90 rounded-2xl border border-gray-700 flex flex-col h-64 lg:h-full shadow-xl overflow-hidden shrink-0">
      <div class="p-4 lg:p-6 border-b border-gray-700 bg-gradient-to-r from-gray-900 to-gray-800 shrink-0">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-bold text-lg lg:text-xl text-white">Historial</h3>
            <p class="text-xs lg:text-sm text-gray-400 mt-1">Últimas 5 ejecuciones</p>
          </div>
          <div class="h-8 w-8 lg:h-10 lg:w-10 bg-gradient-to-br from-red-600/20 to-red-700/20 rounded-lg flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 lg:h-5 lg:w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>
      
      <div class="flex-1 overflow-y-auto p-3 lg:p-4 space-y-3">
        {#if data.historial.length === 0}
          <div class="text-center py-8 text-gray-400">
            <p class="text-sm">No hay ejecuciones registradas</p>
          </div>
        {:else}
          {#each data.historial as item, i}
            <div class="group relative p-3 lg:p-4 rounded-xl border border-gray-700 hover:border-red-500/50 bg-gray-800/30 hover:bg-gray-800/80 transition-all duration-200">
              <div class="flex items-center">
                <div class={`h-10 w-10 lg:h-12 lg:w-12 rounded-xl flex items-center justify-center mr-3 lg:mr-4 shrink-0
                  ${item.estado === 'Exitoso' 
                    ? 'bg-green-900/20 text-green-400 border border-green-600/20' 
                    : 'bg-red-900/20 text-red-400 border border-red-600/20'
                  }`}>
                  {#if item.estado === 'Exitoso'}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 lg:h-6 lg:w-6" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                  {:else}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 lg:h-6 lg:w-6" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                  {/if}
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-xs lg:text-sm font-medium text-white truncate">{item.fecha}</p>
                  <div class="flex justify-between items-center mt-1">
                    <span class={`text-[10px] lg:text-xs font-medium px-2 py-0.5 lg:py-1 rounded-full ${item.estado === 'Exitoso' ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
                      {item.estado}
                    </span>
                    <span class="text-[10px] lg:text-xs text-gray-400 font-mono">{item.duracion}</span>
                  </div>
                </div>
              </div>
            </div>
          {/each}
        {/if}
      </div>
      
      <div class="p-3 lg:p-4 border-t border-gray-700 bg-gradient-to-r from-gray-900 to-gray-800 shrink-0">
        <a href="/dashboard/etl/history" class="w-full flex items-center justify-center text-xs lg:text-sm text-gray-300 hover:text-white font-medium transition-colors group">
          <span>Ver historial completo</span>
          <svg class="w-4 h-4 ml-2 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
          </svg>
        </a>
      </div>
    </div>
  </div>

  <div class="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl border border-gray-700 shadow-xl overflow-hidden flex flex-col shrink-0 h-48 lg:h-56 xl:h-64">
    <div class="bg-gradient-to-r from-gray-900 to-gray-800 px-4 lg:px-6 py-3 border-b border-gray-700 flex justify-between items-center shrink-0">
      <div class="flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 lg:h-5 lg:w-5 text-red-400 mr-2 lg:mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
        <span class="text-gray-300 text-xs lg:text-sm font-mono font-medium">Terminal / Logs del Sistema</span>
      </div>
      <div class="flex items-center space-x-1">
        <div class="w-2.5 h-2.5 lg:w-3 lg:h-3 rounded-full bg-red-500"></div>
        <div class="w-2.5 h-2.5 lg:w-3 lg:h-3 rounded-full bg-yellow-500 ml-1"></div>
        <div class="w-2.5 h-2.5 lg:w-3 lg:h-3 rounded-full bg-green-500 ml-1"></div>
      </div>
    </div>
    
    <div class="p-4 lg:p-6 overflow-y-auto font-mono text-xs lg:text-sm space-y-1.5 lg:space-y-2 flex-1 bg-gray-950/30">
      {#if data.logs.length === 0}
        <div class="text-center py-6 text-gray-500">
          <p>Los logs aparecerán aquí durante la ejecución</p>
        </div>
      {:else}
        {#each data.logs as log}
          <div class="flex gap-2 lg:gap-4 hover:bg-gray-800/30 px-2 py-0.5 rounded transition-colors">
            <span class="text-gray-500 select-none shrink-0">[{log.timestamp}]</span>
            <span class={`break-all ${
              log.nivel === 'INFO' ? 'text-blue-400' : 
              log.nivel === 'WARN' ? 'text-yellow-400' : 
              log.nivel === 'SUCCESS' ? 'text-green-400' : 
              log.nivel === 'ERROR' ? 'text-red-400' : 'text-gray-300'
            }`}>
              <span class="font-bold">{log.nivel}:</span> {log.mensaje}
            </span>
          </div>
        {/each}
      {/if}
      
      {#if isRunning}
        <div class="flex gap-2 lg:gap-4 px-2 py-0.5">
          <span class="text-gray-500 select-none shrink-0">[AHORA]</span>
          <span class="text-green-400 animate-pulse">
            <span class="font-bold">PROCESS:</span> Extrayendo datos de máquinas tragaperras...
          </span>
        </div>
      {/if}
    </div>
    
    <div class="px-4 lg:px-6 py-2 border-t border-gray-700 bg-gradient-to-r from-gray-900 to-gray-800 text-[10px] lg:text-xs text-gray-400 flex justify-between shrink-0">
      <span>Luckia Analytics • Sistema de Logs ETL</span>
      <span>Total logs: {data.logs.length}</span>
    </div>
  </div>
</div>

<style>
  /* Estilo para scrollbar personalizada */
  .overflow-y-auto::-webkit-scrollbar {
    width: 6px;
  }
  
  .overflow-y-auto::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 3px;
  }
  
  .overflow-y-auto::-webkit-scrollbar-thumb {
    background: rgba(239, 68, 68, 0.3);
    border-radius: 3px;
  }
  
  .overflow-y-auto::-webkit-scrollbar-thumb:hover {
    background: rgba(239, 68, 68, 0.5);
  }
  
  @keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
  
  .animate-pulse {
    animation: blink 1.5s ease-in-out infinite;
  }
</style>