<script lang="ts">
    import { fade, fly } from 'svelte/transition';
    export let data;

    // Estado de la interfaz
    let activeTab: 'pending' | 'processed' = 'pending'; // 'pending' = No Leídos
    let searchTerm = '';

    // Filtrado reactivo: Filtra por Tab activo Y por búsqueda
    $: filteredFiles = data.files.filter(file => 
        file.status === activeTab && 
        file.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Contadores para los badges de las pestañas
    $: countPending = data.files.filter(f => f.status === 'pending').length;
    $: countProcessed = data.files.filter(f => f.status === 'processed').length;
</script>

<div class="flex flex-col h-[calc(100vh-6rem)] gap-6">
    
    <div class="bg-gradient-to-r from-gray-900 to-gray-800 p-6 rounded-2xl border border-gray-700 shadow-xl shrink-0">
        <div class="flex flex-col lg:flex-row justify-between gap-6">
            <div>
                <h1 class="text-3xl font-bold text-white mb-2">Gestión de Archivos</h1>
                <p class="text-gray-400">Control de carga a Staging desde carpeta compartida</p>
            </div>

            <div class="relative w-full lg:w-72">
                <input 
                    type="text" 
                    bind:value={searchTerm}
                    placeholder="Buscar archivo..." 
                    class="w-full bg-gray-900/50 border border-gray-600 rounded-xl py-2.5 pl-10 pr-4 text-gray-200 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                >
                <svg class="w-5 h-5 text-gray-500 absolute left-3 top-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
            </div>
        </div>

        <div class="flex space-x-1 bg-gray-900/50 p-1 rounded-xl mt-6 w-full md:w-fit border border-gray-700/50">
            <button 
                on:click={() => activeTab = 'pending'}
                class="relative px-6 py-2.5 rounded-lg text-sm font-medium transition-all duration-300 flex items-center gap-2 flex-1 md:flex-none justify-center
                {activeTab === 'pending' ? 'text-white shadow-lg' : 'text-gray-400 hover:text-white hover:bg-white/5'}"
            >
                {#if activeTab === 'pending'}
                    <div class="absolute inset-0 bg-purple-600 rounded-lg -z-10" layout:id="activeTab"></div>
                {/if}
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                No Leídos
                <span class="ml-1 bg-gray-900/30 px-2 py-0.5 rounded-full text-xs border border-white/10">
                    {countPending}
                </span>
            </button>

            <button 
                on:click={() => activeTab = 'processed'}
                class="relative px-6 py-2.5 rounded-lg text-sm font-medium transition-all duration-300 flex items-center gap-2 flex-1 md:flex-none justify-center
                {activeTab === 'processed' ? 'text-white shadow-lg' : 'text-gray-400 hover:text-white hover:bg-white/5'}"
            >
                {#if activeTab === 'processed'}
                    <div class="absolute inset-0 bg-gray-600 rounded-lg -z-10" layout:id="activeTab"></div>
                {/if}
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Leídos (Staging)
                <span class="ml-1 bg-gray-900/30 px-2 py-0.5 rounded-full text-xs border border-white/10">
                    {countProcessed}
                </span>
            </button>
        </div>
    </div>

    <div class="flex-1 overflow-y-auto bg-gray-900/30 rounded-2xl border border-gray-700/50 p-6 min-h-0 relative">
        
        <div class="absolute top-4 right-6 text-xs font-mono text-gray-500">
            Carpeta: <span class="text-gray-400">/uploads/{activeTab === 'pending' ? 'no_leidos' : 'leidos'}</span>
        </div>

        {#if filteredFiles.length === 0}
            <div in:fade class="h-full flex flex-col items-center justify-center text-gray-500">
                <div class="w-20 h-20 bg-gray-800 rounded-full flex items-center justify-center mb-4 border border-gray-700">
                    {#if activeTab === 'pending'}
                        <svg class="w-10 h-10 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                    {:else}
                        <svg class="w-10 h-10 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                        </svg>
                    {/if}
                </div>
                <p class="text-lg font-medium">No hay archivos {activeTab === 'pending' ? 'pendientes' : 'procesados'}</p>
                <p class="text-sm opacity-60">
                    {activeTab === 'pending' ? 'Carga archivos en la carpeta compartida' : 'Ejecuta el ETL para mover archivos aquí'}
                </p>
            </div>
        {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {#each filteredFiles as file (file.name + file.status)}
                    <div 
                        in:fly={{ y: 20, duration: 300 }}
                        class="group relative bg-gray-800 hover:bg-gray-750 rounded-xl p-4 border transition-all duration-300 hover:-translate-y-1 hover:shadow-xl flex flex-col
                        {file.status === 'pending' 
                            ? 'border-gray-700 hover:border-purple-500/50' 
                            : 'border-gray-700/50 opacity-75 hover:opacity-100 hover:border-green-500/30'}"
                    >
                        <div class="flex justify-between items-start mb-4">
                            <div class="p-3 rounded-lg transition-colors
                                {file.status === 'pending' ? 'bg-purple-900/20 text-purple-400 group-hover:bg-purple-900/30' : 'bg-green-900/20 text-green-500'}">
                                <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
                                </svg>
                            </div>
                            
                            <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded border
                                {file.status === 'pending' 
                                    ? 'bg-yellow-900/20 text-yellow-500 border-yellow-500/20' 
                                    : 'bg-blue-900/20 text-blue-400 border-blue-500/20'}">
                                {file.status === 'pending' ? 'Pendiente' : 'Staging'}
                            </span>
                        </div>

                        <div class="mt-auto">
                            <h3 class="text-white font-medium text-sm truncate" title={file.name}>
                                {file.name}
                            </h3>
                            <div class="flex items-center justify-between mt-3 text-xs text-gray-400">
                                <div class="flex items-center">
                                    <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    {file.date}
                                </div>
                                <span class="bg-gray-900 px-1.5 py-0.5 rounded text-[10px] border border-gray-700">{file.size}</span>
                            </div>
                        </div>

                        <a 
                            href={`/api/download?file=${file.name}&folder=${file.status === 'pending' ? 'no_leidos' : 'leidos'}`}
                            class="absolute inset-0 z-10"
                            aria-label="Descargar archivo"
                        ></a>
                    </div>
                {/each}
            </div>
        {/if}
    </div>
</div>