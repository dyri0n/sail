<script lang="ts">
    import { fade, fly } from 'svelte/transition';
    
    // Recibimos los datos del server
    export let data;
  
    let searchTerm = '';
    let statusFilter = 'Todos';
  
    // Lógica simple de filtrado en cliente
    $: filteredHistory = data.history.filter(item => {
      const matchesSearch = item.detalles.toLowerCase().includes(searchTerm.toLowerCase()) || 
                            item.usuario.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = statusFilter === 'Todos' || item.estado === statusFilter;
      return matchesSearch && matchesStatus;
    });
  </script>
  
  <div class="flex flex-col gap-6 h-full lg:h-[calc(100vh-6rem)] w-full">
    
    <div class="shrink-0 flex flex-col gap-4">
      <div class="flex items-center gap-4">
        <a href="/dashboard/etl" class="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white transition-colors border border-gray-700 group">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 transform group-hover:-translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </a>
        <div>
          <h1 class="text-2xl font-bold text-white">Historial de Ejecuciones</h1>
          <p class="text-sm text-gray-400">Registro completo de actividades del motor ETL</p>
        </div>
      </div>
  
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-gray-800/50 border border-gray-700 p-4 rounded-xl flex items-center justify-between">
          <div>
            <p class="text-xs text-gray-400 uppercase">Total Ejecuciones</p>
            <p class="text-2xl font-bold text-white">{data.stats.total}</p>
          </div>
          <div class="h-10 w-10 bg-blue-900/20 rounded-lg flex items-center justify-center text-blue-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
        </div>
        
        <div class="bg-gray-800/50 border border-gray-700 p-4 rounded-xl flex items-center justify-between">
          <div>
            <p class="text-xs text-gray-400 uppercase">Tasa de Éxito</p>
            <p class="text-2xl font-bold text-green-400">{data.stats.tasaExito}</p>
          </div>
          <div class="h-10 w-10 bg-green-900/20 rounded-lg flex items-center justify-center text-green-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
  
        <div class="bg-gray-800/50 border border-gray-700 p-4 rounded-xl flex items-center justify-between">
          <div>
            <p class="text-xs text-gray-400 uppercase">Duración Promedio</p>
            <p class="text-2xl font-bold text-yellow-400">{data.stats.promedioDuracion}</p>
          </div>
          <div class="h-10 w-10 bg-yellow-900/20 rounded-lg flex items-center justify-center text-yellow-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  
    <div class="flex-1 bg-gray-900/50 border border-gray-700 rounded-2xl overflow-hidden flex flex-col shadow-xl backdrop-blur-sm min-h-0">
      
      <div class="p-4 border-b border-gray-700 flex flex-col sm:flex-row gap-4 justify-between items-center bg-gray-800/40">
        
        <div class="relative w-full sm:w-64">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-4 w-4 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input 
            type="text"
            bind:value={searchTerm}
            placeholder="Buscar por usuario o detalle..." 
            class="pl-10 pr-4 py-2 w-full bg-gray-900 border border-gray-700 rounded-lg text-sm text-white focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-colors placeholder-gray-500"
          />
        </div>
  
        <div class="flex bg-gray-900 rounded-lg p-1 border border-gray-700">
          {#each ['Todos', 'Exitoso', 'Fallido'] as status}
            <button 
              class={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${statusFilter === status ? 'bg-gray-700 text-white shadow' : 'text-gray-400 hover:text-white'}`}
              on:click={() => statusFilter = status}
            >
              {status}
            </button>
          {/each}
        </div>
      </div>
  
      <div class="flex-1 overflow-auto">
        <table class="w-full text-sm text-left text-gray-400">
          <thead class="text-xs text-gray-300 uppercase bg-gray-800/80 sticky top-0 backdrop-blur-md z-10">
            <tr>
              <th scope="col" class="px-6 py-4">Estado</th>
              <th scope="col" class="px-6 py-4">Fecha / Hora</th>
              <th scope="col" class="px-6 py-4">Duración</th>
              <th scope="col" class="px-6 py-4 hidden sm:table-cell">Registros</th>
              <th scope="col" class="px-6 py-4 hidden md:table-cell">Usuario</th>
              <th scope="col" class="px-6 py-4 hidden lg:table-cell">Detalles</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-800">
            {#each filteredHistory as item (item.id)}
              <tr in:fly={{ y: 20, duration: 300 }} class="hover:bg-gray-800/40 transition-colors group">
                <td class="px-6 py-4">
                  <div class="flex items-center">
                    {#if item.estado === 'Exitoso'}
                      <div class="h-2 w-2 rounded-full bg-green-500 mr-2 shadow-[0_0_8px_rgba(34,197,94,0.6)]"></div>
                      <span class="text-green-400 font-medium">Exitoso</span>
                    {:else}
                      <div class="h-2 w-2 rounded-full bg-red-500 mr-2 shadow-[0_0_8px_rgba(239,68,68,0.6)]"></div>
                      <span class="text-red-400 font-medium">Fallido</span>
                    {/if}
                  </div>
                </td>
                <td class="px-6 py-4 font-mono text-white">
                  {item.fecha}
                </td>
                <td class="px-6 py-4">
                  {item.duracion}
                </td>
                <td class="px-6 py-4 hidden sm:table-cell">
                  {item.registros} filas
                </td>
                <td class="px-6 py-4 hidden md:table-cell">
                  <span class="px-2 py-1 rounded-md bg-gray-800 text-gray-300 border border-gray-700 text-xs">
                    {item.usuario}
                  </span>
                </td>
                <td class="px-6 py-4 hidden lg:table-cell text-gray-500 group-hover:text-gray-300 transition-colors">
                  {item.detalles}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
        
        {#if filteredHistory.length === 0}
          <div class="flex flex-col items-center justify-center h-64 text-gray-500">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mb-3 opacity-20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>No se encontraron registros</p>
          </div>
        {/if}
      </div>
  
      <div class="px-6 py-3 border-t border-gray-700 bg-gray-800/40 flex items-center justify-between shrink-0">
        <span class="text-xs text-gray-500">Mostrando {filteredHistory.length} resultados</span>
        <div class="flex gap-2">
          <button class="px-3 py-1 text-xs rounded border border-gray-700 text-gray-400 hover:bg-gray-700 disabled:opacity-50" disabled>Anterior</button>
          <button class="px-3 py-1 text-xs rounded border border-gray-700 text-gray-400 hover:bg-gray-700 disabled:opacity-50" disabled>Siguiente</button>
        </div>
      </div>
    </div>
  </div>
  
  <style>
    /* Scrollbar sutil para la tabla */
    .overflow-auto::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    .overflow-auto::-webkit-scrollbar-track {
      background: transparent;
    }
    .overflow-auto::-webkit-scrollbar-thumb {
      background: rgba(75, 85, 99, 0.4);
      border-radius: 3px;
    }
    .overflow-auto::-webkit-scrollbar-thumb:hover {
      background: rgba(75, 85, 99, 0.6);
    }
  </style>