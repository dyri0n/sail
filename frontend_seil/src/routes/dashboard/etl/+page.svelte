<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { triggerETL, getExecutionStatus } from '$lib/services/etl.service';
  import type { ETLExecution, LogEntry } from '$lib/services/etl.service';
  import { invalidateAll } from '$app/navigation';
  import { browser } from '$app/environment';

  // Interfaz para los datos recibidos del servidor
  interface EtlData {
    historial: ETLExecution[];
    logs: LogEntry[];
    user?: {
      nombre: string;
      rol?: string;
    };
    error?: string;
    token?: string;  // Token pasado desde el servidor
  }

  // Tipar la prop data
  export let data: EtlData;

  let isRunning = false;
  let progress = 0;
  let currentExecutionId: string | null = null;
  let errorMessage = '';
  let pollInterval: any = null;

  async function runEtl() {
    // Usar el token que viene del servidor
    const token = data.token;
    
    if (!token) {
      errorMessage = 'No tienes una sesión activa. Por favor, inicia sesión nuevamente.';
      return;
    }

    isRunning = true;
    progress = 10;
    errorMessage = '';

    try {
      // 1. Disparar el DAG en Airflow vía backend
      const response = await triggerETL('99_maestro_poblado_completo_dwh', token);
      currentExecutionId = response.execution_id;
      
      console.log('ETL iniciado:', response);
      
      // 2. Iniciar polling del estado
      startPolling();

      // 3. Simular progreso visual básico
      const progressInterval = setInterval(() => {
        if (progress < 90) {
          progress += Math.random() * 10;
        }
      }, 1000);

      // Detener progreso visual después de 30s
      setTimeout(() => clearInterval(progressInterval), 30000);

    } catch (error: any) {
      console.error('Error ejecutando ETL:', error);
      errorMessage = error.message || 'Error al iniciar el proceso ETL. Verifica que el backend esté activo.';
      isRunning = false;
      progress = 0;
    }
  }

  function startPolling() {
    if (!currentExecutionId || !data.token) return;

    // Consultar el estado cada 3 segundos
    pollInterval = setInterval(async () => {
      if (!currentExecutionId || !data.token) return;

      try {
        const status = await getExecutionStatus(currentExecutionId, data.token);
        
        console.log('Estado actual:', status.state);
        
        // Actualizar progreso según el estado
        if (status.state === 'running' || status.state === 'queued') {
          progress = Math.min(progress + 5, 95);
        } else if (status.state === 'success') {
          progress = 100;
          stopPolling();
          
          // Recargar la página para mostrar el nuevo historial
          await invalidateAll();
          
          setTimeout(() => {
            isRunning = false;
            progress = 0;
            currentExecutionId = null;
          }, 2000);
          
        } else if (status.state === 'failed') {
          errorMessage = 'La ejecución falló. Revisa los logs para más detalles.';
          stopPolling();
          isRunning = false;
          progress = 0;
          currentExecutionId = null;
        }
      } catch (error) {
        console.error('Error chequeando estado:', error);
        // No detener el polling por un error temporal
      }
    }, 3000);
  }

  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval);
      pollInterval = null;
    }
  }

  onDestroy(() => {
    stopPolling();
  });

  // Formatear fecha UTC del backend a hora de Chile 
  function formatDate(isoDate: string): string {
    try {
      // El backend envía fechas en UTC sin 'Z', agregarlo si falta
      let isoString = isoDate;
      if (!isoString.endsWith('Z') && !isoString.includes('+') && !isoString.includes('-', 10)) {
        isoString = isoDate + 'Z';
      }
      
      return new Date(isoString).toLocaleString('es-CL', {
        timeZone: 'America/Santiago',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      });
    } catch {
      return isoDate;
    }
  }

  // Mapear estados del backend a estados del frontend
  function mapState(state: string): 'Exitoso' | 'Fallido' {
    if (state === 'success') return 'Exitoso';
    if (state === 'failed' || state === 'failed') return 'Fallido';
    return 'Fallido'; // Por defecto
  }

  // Calcular duración
  function calculateDuration(start?: string, end?: string): string {
    if (!start || !end) return 'N/A';
    
    try {
      const startDate = new Date(start);
      const endDate = new Date(end);
      const diffMs = endDate.getTime() - startDate.getTime();
      
      if (diffMs < 0) return 'N/A';
      
      const minutes = Math.floor(diffMs / 60000);
      const seconds = Math.floor((diffMs % 60000) / 1000);
      
      return `${minutes}m ${seconds}s`;
    } catch {
      return 'N/A';
    }
  }

  // Mostrar error inicial si existe
  onMount(() => {
    if (data.error) {
      errorMessage = data.error;
    }
  });
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

      {#if errorMessage}
        <p class="mt-4 lg:mt-6 text-xs lg:text-sm text-red-400 bg-red-900/20 p-3 rounded-lg border border-red-600/30 flex items-center justify-center">
          <svg class="w-4 h-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {errorMessage}
        </p>
      {/if}

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
          {#each data.historial.slice(0, 5) as item, i}
            <div class="group relative p-3 lg:p-4 rounded-xl border border-gray-700 hover:border-red-500/50 bg-gray-800/30 hover:bg-gray-800/80 transition-all duration-200">
              <div class="flex items-center">
                <div class={`h-10 w-10 lg:h-12 lg:w-12 rounded-xl flex items-center justify-center mr-3 lg:mr-4 shrink-0
                  ${mapState(item.state) === 'Exitoso' 
                    ? 'bg-green-900/20 text-green-400 border border-green-600/20' 
                    : 'bg-red-900/20 text-red-400 border border-red-600/20'
                  }`}>
                  {#if mapState(item.state) === 'Exitoso'}
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
                  <p class="text-xs lg:text-sm font-medium text-white truncate">{formatDate(item.start_date || item.execution_date)}</p>
                  <div class="flex justify-between items-center mt-1">
                    <span class={`text-[10px] lg:text-xs font-medium px-2 py-0.5 lg:py-1 rounded-full ${mapState(item.state) === 'Exitoso' ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
                      {mapState(item.state)}
                    </span>
                    <span class="text-[10px] lg:text-xs text-gray-400 font-mono">{calculateDuration(item.start_date, item.end_date)}</span>
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

  <!-- Sección de Logs - Solo visible para ADMIN -->
  {#if data.user?.rol === 'ADMIN'}
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
              log.level === 'INFO' ? 'text-blue-400' : 
              log.level === 'WARN' ? 'text-yellow-400' : 
              log.level === 'SUCCESS' ? 'text-green-400' : 
              log.level === 'ERROR' ? 'text-red-400' : 'text-gray-300'
            }`}>
              <span class="font-bold">{log.level}:</span> {log.message}
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
  {/if}
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