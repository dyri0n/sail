<script lang="ts">
  import { enhance } from '$app/forms';
  import { onMount } from 'svelte';
  import type { PageData } from './$types';
  
  // Tipos de datos recibidos del servidor
  interface LogEntry {
    id: string;
    timestamp: string;
    nivel: 'INFO' | 'WARN' | 'ERROR' | 'SUCCESS' | 'DEBUG' | 'AUDIT';
    modulo: string;
    mensaje: string;
    usuario: string;
    ip?: string;
    detalles?: Record<string, any>;
  }

  interface LogStats {
    total: number;
    errores: number;
    auditoria: number;
    ultimo: string;
  }

  interface FilterValues {
    niveles: string[];
    modulos: string[];
    usuarios: string[];
  }

  // Recibimos los datos del servidor
  let { data } = $props() satisfies { data: PageData };
  
  // Estados para filtros locales
  let filtros = $state({
    nivel: 'todos',
    modulo: 'todos',
    usuario: 'todos',
    fechaInicio: '',
    fechaFin: '',
    busqueda: ''
  });
  
  // Estados para UI
  let autoRefresh = $state(true);
  let isWsConnected = $state(false);
  let logsDetallado = $state<LogEntry | null>(null);
  let exportStatus = $state<{
    loading: boolean;
    success?: boolean;
    message?: string;
    fileName?: string;
  }>({ loading: false });
  
  // Variables para WebSocket (simuladas)
  let wsConnection: any = null;
  
  // Función para formatear fecha
  function formatearFecha(timestamp: string) {
    const fecha = new Date(timestamp);
    return fecha.toLocaleString('es-CL');
  }
  
  // Función para obtener color según nivel (Solo estilos de texto/fondo)
  function getNivelColor(nivel: string) {
    switch(nivel) {
      case 'INFO': return 'bg-blue-900/30 text-blue-400 border border-blue-600/20';
      case 'WARN': return 'bg-yellow-900/30 text-yellow-400 border border-yellow-600/20';
      case 'ERROR': return 'bg-red-900/30 text-red-400 border border-red-600/20';
      case 'SUCCESS': return 'bg-green-900/30 text-green-400 border border-green-600/20';
      case 'DEBUG': return 'bg-purple-900/30 text-purple-400 border border-purple-600/20';
      case 'AUDIT': return 'bg-gray-900/30 text-gray-400 border border-gray-600/20';
      default: return 'bg-gray-900/30 text-gray-400 border border-gray-600/20';
    }
  }
  
  // Función para filtrar logs localmente
  function filtrarLogs() {
    return data.logs.filter((log: LogEntry) => {
      // Filtro por nivel
      if (filtros.nivel !== 'todos' && log.nivel !== filtros.nivel) return false;
      
      // Filtro por módulo
      if (filtros.modulo !== 'todos' && log.modulo !== filtros.modulo) return false;
      
      // Filtro por usuario
      if (filtros.usuario !== 'todos' && log.usuario !== filtros.usuario) return false;
      
      // Filtro por fecha
      if (filtros.fechaInicio && log.timestamp < filtros.fechaInicio) return false;
      if (filtros.fechaFin && log.timestamp > filtros.fechaFin) return false;
      
      // Filtro por búsqueda
      if (filtros.busqueda) {
        const busquedaLower = filtros.busqueda.toLowerCase();
        return (
          log.mensaje.toLowerCase().includes(busquedaLower) ||
          log.usuario.toLowerCase().includes(busquedaLower) ||
          (log.ip && log.ip.includes(busquedaLower)) ||
          log.modulo.toLowerCase().includes(busquedaLower)
        );
      }
      
      return true;
    });
  }
  
  // Función para limpiar filtros
  function limpiarFiltros() {
    filtros = {
      nivel: 'todos',
      modulo: 'todos',
      usuario: 'todos',
      fechaInicio: '',
      fechaFin: '',
      busqueda: ''
    };
  }
  
  // Función para mostrar detalles del log
  function mostrarDetalles(log: LogEntry) {
    logsDetallado = log;
  }
  
  // Función para descargar CSV localmente
  function exportarCSVLocal() {
    const logsFiltrados = filtrarLogs();
    const headers = ['Timestamp', 'Nivel', 'Módulo', 'Usuario', 'IP', 'Mensaje'];
    const csvRows = [];
    
    csvRows.push(headers.join(','));
    
    logsFiltrados.forEach((log: LogEntry) => {
      const row = [
        log.timestamp,
        log.nivel,
        log.modulo,
        log.usuario,
        log.ip || 'N/A',
        `"${log.mensaje.replace(/"/g, '""')}"`
      ];
      csvRows.push(row.join(','));
    });
    
    const csvString = csvRows.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `logs_auditoria_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }
  
  // Conectar WebSocket (simulación)
  function conectarWebSocket() {
    isWsConnected = false; 
  }
  
  // Calculamos logs filtrados reactivamente
  let logsFiltrados = $derived(filtrarLogs());
  
  onMount(() => {
    conectarWebSocket();
  });
</script>

<div class="min-h-full p-6">
  <div class="mb-8">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-white mb-2">Sistema de Logs y Auditoría</h1>
        <p class="text-gray-400">
          Monitoreo centralizado de eventos del sistema, accesos y acciones de usuarios (RF-07)
        </p>
      </div>
      
      <div class="flex items-center space-x-3">
        <div class={`px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1.5 ${isWsConnected ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
          {#if isWsConnected}
            <span>En tiempo real</span>
          {:else}
            <span>Sin conexión en tiempo real</span>
          {/if}
        </div>
        
        <form method="POST" action="?/exportCSV" use:enhance>
          <input type="hidden" name="nivel" value={filtros.nivel} />
          <input type="hidden" name="modulo" value={filtros.modulo} />
          <input type="hidden" name="usuario" value={filtros.usuario} />
          
          <button 
            type="submit"
            class="px-4 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-xl font-medium flex items-center transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={exportStatus.loading}
          >
            {#if exportStatus.loading}
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Exportando...
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Exportar CSV
            {/if}
          </button>
        </form>
        
        <button 
          on:click={exportarCSVLocal}
          class="px-4 py-2.5 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white rounded-xl font-medium flex items-center transition-all shadow-lg hover:shadow-xl"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Exportar Local
        </button>
      </div>
    </div>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
    <div class="bg-gradient-to-br from-gray-900/80 to-gray-800/80 rounded-2xl border border-gray-700 p-6 flex flex-col justify-center">
      <p class="text-gray-400 text-sm">Total Logs</p>
      <p class="text-3xl font-bold text-white mt-1">{data.stats.total}</p>
    </div>

    <div class="bg-gradient-to-br from-gray-900/80 to-gray-800/80 rounded-2xl border border-gray-700 p-6 flex flex-col justify-center">
      <p class="text-gray-400 text-sm">Errores Críticos</p>
      <p class="text-3xl font-bold text-white mt-1">{data.stats.errores}</p>
    </div>

    <div class="bg-gradient-to-br from-gray-900/80 to-gray-800/80 rounded-2xl border border-gray-700 p-6 flex flex-col justify-center">
      <p class="text-gray-400 text-sm">Eventos de Auditoría</p>
      <p class="text-3xl font-bold text-white mt-1">{data.stats.auditoria}</p>
    </div>

    <div class="bg-gradient-to-br from-gray-900/80 to-gray-800/80 rounded-2xl border border-gray-700 p-6 flex flex-col justify-between">
      <div class="flex justify-between items-start">
          <div>
              <p class="text-gray-400 text-sm">Último Evento</p>
              <p class="text-lg font-bold text-white mt-1 truncate">
              {data.stats.ultimo ? formatearFecha(data.stats.ultimo).substring(0, 10) : 'N/A'}
              </p>
          </div>
          <div class="flex items-center space-x-2">
              <label class="relative inline-flex items-center cursor-pointer">
              <input 
                  type="checkbox" 
                  bind:checked={autoRefresh}
                  class="sr-only peer"
                  aria-label="Auto-refresh de logs"
              />
              <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
              </label>
              <span class="text-xs text-gray-400">Auto</span>
          </div>
      </div>
    </div>
  </div>

  <div class="bg-gradient-to-br from-gray-900/80 to-gray-800/80 rounded-2xl border border-gray-700 p-6 mb-6">
    <div class="grid grid-cols-1 md:grid-cols-6 gap-4">
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-300 mb-2">Buscar en logs</label>
        <div class="relative">
          <input
            type="text"
            bind:value={filtros.busqueda}
            placeholder="Texto en mensaje, usuario, IP..."
            class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
          />
          <svg class="absolute right-3 top-3 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">Nivel</label>
        <select 
          bind:value={filtros.nivel}
          class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
        >
          {#each data.filters.niveles as nivel}
            <option value={nivel}>{nivel === 'todos' ? 'Todos los niveles' : nivel}</option>
          {/each}
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">Módulo</label>
        <select 
          bind:value={filtros.modulo}
          class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
        >
          {#each data.filters.modulos as modulo}
            <option value={modulo}>{modulo === 'todos' ? 'Todos los módulos' : modulo}</option>
          {/each}
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">Usuario</label>
        <select 
          bind:value={filtros.usuario}
          class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
        >
          {#each data.filters.usuarios as usuario}
            <option value={usuario}>{usuario === 'todos' ? 'Todos los usuarios' : usuario}</option>
          {/each}
        </select>
      </div>

      <div class="md:col-span-2 flex items-end space-x-2">
        <button
          on:click={limpiarFiltros}
          class="px-4 py-3 bg-gray-800 hover:bg-gray-700 text-white rounded-xl font-medium flex-1 transition-colors"
        >
          Limpiar Filtros
        </button>
      </div>
    </div>
  </div>

  <div class="bg-gradient-to-br from-gray-900/80 to-gray-800/80 rounded-2xl border border-gray-700 overflow-hidden mb-6">
    <div class="p-6 border-b border-gray-700 bg-gradient-to-r from-gray-900 to-gray-800">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="font-bold text-xl text-white">Eventos del Sistema</h3>
          <p class="text-sm text-gray-400 mt-1">
            Mostrando {logsFiltrados.length} de {data.logs.length} logs • 
            Última actualización: {new Date(data.metadata.lastUpdated).toLocaleTimeString('es-CL')}
          </p>
        </div>
        
        <form method="POST" action="?/clearLogs" use:enhance>
          <button 
            type="submit"
            class="px-4 py-2 bg-gradient-to-r from-red-600/20 to-red-700/20 hover:from-red-700/30 hover:to-red-800/30 text-red-400 rounded-xl font-medium flex items-center transition-colors border border-red-600/20"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Limpiar Logs Antiguos
          </button>
        </form>
      </div>
    </div>
    
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="border-b border-gray-700 bg-gradient-to-r from-gray-900 to-gray-800">
            <th class="py-4 px-6 text-left text-sm font-medium text-gray-300">Timestamp</th>
            <th class="py-4 px-6 text-left text-sm font-medium text-gray-300">Nivel</th>
            <th class="py-4 px-6 text-left text-sm font-medium text-gray-300">Módulo</th>
            <th class="py-4 px-6 text-left text-sm font-medium text-gray-300">Usuario</th>
            <th class="py-4 px-6 text-left text-sm font-medium text-gray-300">Mensaje</th>
            <th class="py-4 px-6 text-left text-sm font-medium text-gray-300">Acciones</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-800">
          {#each logsFiltrados as log}
            <tr class="hover:bg-gray-800/50 transition-colors">
              <td class="py-4 px-6">
                <div class="text-sm text-gray-300 whitespace-nowrap">{formatearFecha(log.timestamp)}</div>
              </td>
              <td class="py-4 px-6">
                <span class={`inline-flex px-3 py-1 rounded-full text-xs font-medium ${getNivelColor(log.nivel)}`}>
                  {log.nivel}
                </span>
              </td>
              <td class="py-4 px-6">
                <span class="text-sm text-gray-300 font-mono">{log.modulo}</span>
              </td>
              <td class="py-4 px-6">
                <div class="text-sm text-gray-300">{log.usuario}</div>
                {#if log.ip}
                  <div class="text-xs text-gray-500 font-mono">{log.ip}</div>
                {/if}
              </td>
              <td class="py-4 px-6">
                <div class="text-sm text-gray-300 max-w-md truncate">{log.mensaje}</div>
              </td>
              <td class="py-4 px-6">
                <button
                  on:click={() => mostrarDetalles(log)}
                  class="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-white rounded-lg text-sm font-medium transition-colors"
                >
                  Detalles
                </button>
              </td>
            </tr>
          {:else}
            <tr>
              <td colspan="6" class="py-8 px-6 text-center text-gray-500">
                No se encontraron logs con los filtros aplicados
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>

  {#if logsDetallado}
    <div class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div class="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl border border-gray-700 w-full max-w-2xl shadow-2xl">
        <div class="p-6 border-b border-gray-700">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-xl font-bold text-white">Detalles del Evento</h2>
              <p class="text-sm text-gray-400">ID: {logsDetallado.id}</p>
            </div>
            <button
              on:click={() => logsDetallado = null}
              class="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <div class="p-6 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-400 mb-1">Timestamp</p>
              <p class="text-white font-mono">{formatearFecha(logsDetallado.timestamp)}</p>
            </div>
            <div>
              <p class="text-sm text-gray-400 mb-1">Nivel</p>
              <span class={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getNivelColor(logsDetallado.nivel)}`}>
                {logsDetallado.nivel}
              </span>
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-400 mb-1">Módulo</p>
              <p class="text-white font-mono">{logsDetallado.modulo}</p>
            </div>
            <div>
              <p class="text-sm text-gray-400 mb-1">Usuario</p>
              <p class="text-white">{logsDetallado.usuario}</p>
            </div>
          </div>
          
          {#if logsDetallado.ip}
            <div>
              <p class="text-sm text-gray-400 mb-1">Dirección IP</p>
              <p class="text-white font-mono">{logsDetallado.ip}</p>
            </div>
          {/if}
          
          <div>
            <p class="text-sm text-gray-400 mb-1">Mensaje</p>
            <div class="bg-gray-800/50 rounded-xl p-4">
              <p class="text-white whitespace-pre-wrap">{logsDetallado.mensaje}</p>
            </div>
          </div>
          
          {#if logsDetallado.detalles && Object.keys(logsDetallado.detalles).length > 0}
            <div>
              <p class="text-sm text-gray-400 mb-1">Detalles Adicionales</p>
              <div class="bg-gray-800/50 rounded-xl p-4">
                <pre class="text-gray-300 text-sm font-mono overflow-auto max-h-48">{JSON.stringify(logsDetallado.detalles, null, 2)}</pre>
              </div>
            </div>
          {/if}
        </div>
        
        <div class="p-6 border-t border-gray-700 flex justify-end">
          <button
            on:click={() => logsDetallado = null}
            class="px-5 py-2.5 bg-gray-800 hover:bg-gray-700 text-white rounded-xl font-medium transition-colors"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  /* Estilos para scrollbar personalizada */
  .overflow-x-auto::-webkit-scrollbar {
    height: 6px;
  }
  
  .overflow-x-auto::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 3px;
  }
  
  .overflow-x-auto::-webkit-scrollbar-thumb {
    background: rgba(239, 68, 68, 0.3);
    border-radius: 3px;
  }
  
  .overflow-x-auto::-webkit-scrollbar-thumb:hover {
    background: rgba(239, 68, 68, 0.5);
  }
  
  /* Animación para modales */
  .backdrop-blur-sm {
    animation: fadeIn 0.2s ease-out;
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
</style>