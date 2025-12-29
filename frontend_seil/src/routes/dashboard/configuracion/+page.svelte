<script lang="ts">
    import { enhance } from '$app/forms';
    import { fade, slide } from 'svelte/transition';
  
    // Datos simulados basados en el mockup del informe (Pág 26)
    // En producción, esto vendría de `let { data } = $props();`
    let users = $state([
      { id: 1, usuario: 'jyampara', rol: 'Administrador', ultimoAcceso: '2025-10-18 15:30', estado: 'Activo' },
      { id: 2, usuario: 'tsilva', rol: 'Analista', ultimoAcceso: '2025-10-18 14:00', estado: 'Activo' },
      { id: 3, usuario: 'gerencia', rol: 'Visualizador', ultimoAcceso: '2025-10-17 11:00', estado: 'Inactivo' }
    ]);
  
    let isLoadingETL = $state(false);
    let isLoadingExport = $state(false);
    let exportFormat = $state('csv');
    let uploadMessage = $state('');
    
    // Gestión de archivos para el input
    let files: FileList | undefined = $state();
  
    // Simulación de carga ETL
    function handleETLSubmit() {
      isLoadingETL = true;
      uploadMessage = '';
      
      // Simular proceso
      setTimeout(() => {
        isLoadingETL = false;
        uploadMessage = '✅ Carga y transformación completada correctamente. Los datos han pasado al Staging.';
        files = undefined; // Limpiar input
      }, 2000);
    }
  
    // Simulación de exportación
    function handleExport() {
      isLoadingExport = true;
      setTimeout(() => {
        isLoadingExport = false;
        // Aquí iría la lógica real de descarga
        alert(`Exportando datos consolidados en formato .${exportFormat.toUpperCase()}`);
      }, 1500);
    }
  
    // Función dummy para revocar acceso
    function toggleUserStatus(id: number) {
      const userIndex = users.findIndex(u => u.id === id);
      if (userIndex !== -1) {
        users[userIndex].estado = users[userIndex].estado === 'Activo' ? 'Inactivo' : 'Activo';
      }
    }
  </script>
  
  <div class="space-y-6 animate-in fade-in zoom-in duration-500">
    
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-white">Administración del Sistema</h1>
        <p class="text-gray-400 mt-1">Gestión de ETL, exportación y control de acceso (AAA)</p>
      </div>
    </div>
  
    <div class="bg-gray-800/50 border border-gray-700 rounded-2xl p-6 shadow-lg backdrop-blur-sm">
      <div class="flex items-center mb-4">
        <div class="p-2 bg-blue-900/30 rounded-lg mr-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-white">Carga de Datos (ETL)</h2>
      </div>
      
      <p class="text-gray-400 text-sm mb-6">
        Suba los archivos Excel (planillas manuales) con registros de asistencia o beneficios para iniciar el proceso de transformación hacia el Data Warehouse.
      </p>
  
      <div class="bg-gray-900/50 p-6 rounded-xl border border-gray-700/50 border-dashed">
        <form onsubmit={(e) => { e.preventDefault(); handleETLSubmit(); }} class="space-y-4">
          <div>
            <label for="file-upload" class="block text-sm font-medium text-gray-300 mb-2">Seleccionar Planilla Excel</label>
            <input 
              id="file-upload" 
              type="file" 
              accept=".xlsx, .xls"
              bind:files
              class="block w-full text-sm text-gray-400
                file:mr-4 file:py-2.5 file:px-4
                file:rounded-lg file:border-0
                file:text-sm file:font-semibold
                file:bg-gray-800 file:text-blue-400
                hover:file:bg-gray-700 cursor-pointer
                border border-gray-700 rounded-lg"
            />
          </div>
  
          {#if uploadMessage}
            <div class="p-3 bg-green-900/20 border border-green-800 rounded-lg text-green-400 text-sm" transition:slide>
              {uploadMessage}
            </div>
          {/if}
  
          <div class="flex justify-end">
            <button 
              type="submit" 
              disabled={!files || files.length === 0 || isLoadingETL}
              class="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center shadow-lg shadow-blue-900/20"
            >
              {#if isLoadingETL}
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Procesando...
              {:else}
                Iniciar Carga y Transformación
              {/if}
            </button>
          </div>
        </form>
      </div>
    </div>
  
    <div class="bg-gray-800/50 border border-gray-700 rounded-2xl p-6 shadow-lg backdrop-blur-sm">
      <div class="flex items-center mb-4">
        <div class="p-2 bg-green-900/30 rounded-lg mr-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-white">Exportación de Datos</h2>
      </div>
  
      <div class="grid md:grid-cols-3 gap-6 items-end">
        <div class="md:col-span-2">
          <p class="text-gray-400 text-sm mb-4">
            Exporta los datos consolidados y limpios del Data Warehouse. Esto generará un archivo compatible con herramientas externas.
          </p>
          <label for="format" class="block text-sm font-medium text-gray-300 mb-2">Formato de Salida</label>
          <select 
            id="format" 
            bind:value={exportFormat}
            class="w-full bg-gray-900 border border-gray-700 text-white text-sm rounded-lg focus:ring-green-500 focus:border-green-500 block p-2.5"
          >
            <option value="csv">CSV (Valores separados por comas)</option>
            <option value="xlsx">Excel (.xlsx)</option>
            <option value="json">JSON</option>
          </select>
        </div>
        
        <div class="flex justify-end md:justify-start">
          <button 
            onclick={handleExport}
            disabled={isLoadingExport}
            class="w-full md:w-auto px-5 py-2.5 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors flex items-center justify-center shadow-lg shadow-green-900/20"
          >
            {#if isLoadingExport}
              <span class="animate-pulse">Generando...</span>
            {:else}
              Exportar Datos
            {/if}
          </button>
        </div>
      </div>
    </div>
  
    <div class="bg-gray-800/50 border border-gray-700 rounded-2xl p-6 shadow-lg backdrop-blur-sm">
      <div class="flex items-center mb-6">
        <div class="p-2 bg-red-900/30 rounded-lg mr-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-white">Gestión de Acceso (AAA)</h2>
      </div>
  
      <div class="overflow-x-auto rounded-xl border border-gray-700">
        <table class="w-full text-sm text-left text-gray-400">
          <thead class="text-xs text-gray-300 uppercase bg-gray-900/80">
            <tr>
              <th scope="col" class="px-6 py-4">Usuario</th>
              <th scope="col" class="px-6 py-4">Rol</th>
              <th scope="col" class="px-6 py-4">Último Acceso</th>
              <th scope="col" class="px-6 py-4 text-center">Estado</th>
              <th scope="col" class="px-6 py-4 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {#each users as user}
              <tr class="bg-gray-800 border-b border-gray-700 hover:bg-gray-700/50 transition-colors">
                <th scope="row" class="px-6 py-4 font-medium text-white whitespace-nowrap">
                  {user.usuario}
                </th>
                <td class="px-6 py-4">
                  <span class={`px-2.5 py-1 rounded-full text-xs font-medium 
                    ${user.rol === 'Administrador' ? 'bg-red-900/30 text-red-400' : 
                      user.rol === 'Analista' ? 'bg-blue-900/30 text-blue-400' : 
                      'bg-gray-700 text-gray-300'}`}>
                    {user.rol}
                  </span>
                </td>
                <td class="px-6 py-4 font-mono text-xs">
                  {user.ultimoAcceso}
                </td>
                <td class="text-center px-6 py-4">
                  <span class={`inline-block w-2.5 h-2.5 rounded-full ${user.estado === 'Activo' ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-red-500'}`}></span>
                </td>
                <td class="px-6 py-4 text-right">
                  <button 
                    onclick={() => toggleUserStatus(user.id)}
                    class="font-medium text-red-400 hover:underline hover:text-red-300 transition-colors"
                  >
                    {user.estado === 'Activo' ? 'Revocar' : 'Activar'}
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
      
      <div class="flex items-center justify-between mt-4 text-xs text-gray-500">
        <span>Mostrando {users.length} de {users.length} usuarios</span>
        <div class="flex gap-2">
          <button class="px-3 py-1 bg-gray-800 rounded hover:bg-gray-700 disabled:opacity-50" disabled>Anterior</button>
          <button class="px-3 py-1 bg-gray-800 rounded hover:bg-gray-700 disabled:opacity-50" disabled>Siguiente</button>
        </div>
      </div>
    </div>
  
  </div>