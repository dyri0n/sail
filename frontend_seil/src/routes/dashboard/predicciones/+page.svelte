<script lang="ts">
    import { fly, fade } from 'svelte/transition';
    export let data;

    // Filtros
    let filterRisk = 'all'; // all, high, medium, low
    let searchTerm = '';

    // Lógica de filtrado reactiva
    $: filteredEmployees = data.empleados.filter(emp => {
        const matchesSearch = emp.nombre.toLowerCase().includes(searchTerm.toLowerCase()) || 
                              emp.area.toLowerCase().includes(searchTerm.toLowerCase());
        
        let matchesRisk = true;
        if (filterRisk === 'high') matchesRisk = emp.probabilidad >= 70;
        if (filterRisk === 'medium') matchesRisk = emp.probabilidad >= 40 && emp.probabilidad < 70;
        if (filterRisk === 'low') matchesRisk = emp.probabilidad < 40;

        return matchesSearch && matchesRisk;
    });

    // Función para color del riesgo
    const getRiskColor = (prob: number) => {
        if (prob >= 70) return 'text-red-500 bg-red-500/10 border-red-500/20';
        if (prob >= 40) return 'text-orange-400 bg-orange-400/10 border-orange-400/20';
        return 'text-green-500 bg-green-500/10 border-green-500/20';
    };

    const getProgressBarColor = (prob: number) => {
        if (prob >= 70) return 'bg-gradient-to-r from-red-600 to-red-500';
        if (prob >= 40) return 'bg-gradient-to-r from-orange-500 to-yellow-500';
        return 'bg-gradient-to-r from-green-500 to-emerald-500';
    };
</script>

<div class="flex flex-col gap-6 pb-10">
    
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
            <h1 class="text-3xl font-bold text-white">Modelo Predictivo de Rotación</h1>
            <p class="text-gray-400 mt-1">Estimaciones basadas en IA sobre tendencias de fuga de talento</p>
        </div>
        <div class="flex items-center gap-2 bg-orange-900/20 border border-orange-500/30 px-4 py-2 rounded-xl">
            <span class="relative flex h-3 w-3">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-3 w-3 bg-orange-500"></span>
            </span>
            <span class="text-orange-400 text-sm font-medium">Modelo Actualizado: Hoy 08:00 AM</span>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-gradient-to-br from-gray-900 to-gray-800 p-5 rounded-2xl border border-gray-700 shadow-lg">
            <p class="text-gray-400 text-sm font-medium uppercase">Probabilidad Global de Rotación</p>
            <div class="flex items-end gap-2 mt-2">
                <span class="text-3xl font-bold text-white">{data.kpis.riesgoPromedio}%</span>
                <span class="text-sm text-green-400 mb-1 flex items-center">
                    <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"/></svg>
                    -2% vs mes anterior
                </span>
            </div>
        </div>
        <div class="bg-gradient-to-br from-gray-900 to-gray-800 p-5 rounded-2xl border border-gray-700 shadow-lg relative overflow-hidden">
            <div class="absolute right-0 top-0 p-4 opacity-10">
                <svg class="w-16 h-16 text-red-500" fill="currentColor" viewBox="0 0 20 20"><path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z"/></svg>
            </div>
            <p class="text-gray-400 text-sm font-medium uppercase">Empleados en Riesgo Crítico</p>
            <div class="flex items-end gap-2 mt-2">
                <span class="text-3xl font-bold text-red-500">{data.kpis.empleadosCriticos}</span>
                <span class="text-sm text-gray-400 mb-1">Requieren atención</span>
            </div>
        </div>
        <div class="bg-gradient-to-br from-gray-900 to-gray-800 p-5 rounded-2xl border border-gray-700 shadow-lg">
            <p class="text-gray-400 text-sm font-medium uppercase">Área Más Vulnerable</p>
            <div class="mt-2">
                <span class="text-2xl font-bold text-orange-400">{data.kpis.areaMasCritica}</span>
            </div>
        </div>
        <div class="bg-gradient-to-br from-gray-900 to-gray-800 p-5 rounded-2xl border border-gray-700 shadow-lg">
            <p class="text-gray-400 text-sm font-medium uppercase">Próxima Temporada Alta</p>
            <div class="mt-2 flex items-center">
                <svg class="w-5 h-5 text-yellow-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
                <span class="text-xl font-bold text-white">{data.kpis.proximaTemporadaAlta}</span>
            </div>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <div class="lg:col-span-1 bg-gradient-to-b from-gray-900 to-gray-800 rounded-2xl border border-gray-700 shadow-xl p-6">
            <h2 class="text-xl font-bold text-white mb-6 flex items-center">
                <svg class="w-5 h-5 mr-2 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
                Riesgo por Departamentos
            </h2>
            
            <div class="space-y-6">
                {#each data.areas as area}
                    <div class="group">
                        <div class="flex justify-between items-center mb-2">
                            <span class="font-medium text-white">{area.nombre}</span>
                            <span class="text-xs font-mono text-gray-400">Temp: {area.temporada}</span>
                        </div>
                        <div class="relative h-2 bg-gray-700 rounded-full overflow-hidden">
                            <div 
                                class="absolute top-0 left-0 h-full rounded-full {getProgressBarColor(area.riesgo)} transition-all duration-1000 group-hover:brightness-110"
                                style="width: {area.riesgo}%"
                            ></div>
                        </div>
                        <div class="flex justify-between mt-1 text-xs">
                            <span class="text-gray-500">{area.empleados} Empleados</span>
                            <span class="{area.riesgo > 60 ? 'text-red-400' : 'text-gray-400'} font-bold">{area.riesgo}% Riesgo</span>
                        </div>
                    </div>
                {/each}
            </div>
            
            <div class="mt-8 p-4 bg-orange-900/10 border border-orange-500/20 rounded-xl">
                <h4 class="text-orange-400 font-bold text-sm mb-1">Insight Automático</h4>
                <p class="text-gray-400 text-xs leading-relaxed">
                    El área de <strong>Seguridad</strong> muestra una tendencia al alza del 15% para la temporada de Verano debido a la alta demanda de eventos. Se recomienda reforzar incentivos.
                </p>
            </div>
        </div>

        <div class="lg:col-span-2 bg-gray-900 rounded-2xl border border-gray-700 shadow-xl overflow-hidden flex flex-col">
            <div class="p-6 border-b border-gray-700 bg-gray-800/50 flex flex-col sm:flex-row justify-between gap-4">
                <h2 class="text-xl font-bold text-white">Predicciones Individuales</h2>
                
                <div class="flex gap-2">
                    <select 
                        bind:value={filterRisk}
                        class="bg-gray-900 border border-gray-600 text-gray-300 text-sm rounded-lg focus:ring-orange-500 focus:border-orange-500 block p-2.5"
                    >
                        <option value="all">Todo Riesgo</option>
                        <option value="high">Alto (Crítico)</option>
                        <option value="medium">Medio</option>
                        <option value="low">Bajo</option>
                    </select>
                    
                    <input 
                        type="text" 
                        bind:value={searchTerm}
                        placeholder="Buscar empleado..." 
                        class="bg-gray-900 border border-gray-600 text-gray-300 text-sm rounded-lg focus:ring-orange-500 focus:border-orange-500 block p-2.5 w-full sm:w-48"
                    >
                </div>
            </div>

            <div class="overflow-x-auto rounded-xl border border-gray-700 shadow-xl">
                <table class="w-full text-sm text-left text-gray-400">
                    <thead class="text-xs text-gray-500 uppercase bg-gray-900/90 border-b border-gray-700">
                        <tr>
                            <th scope="col" class="px-6 py-4">Empleado</th>
                            <th scope="col" class="px-6 py-4">Cargo / Área</th>
                            <th scope="col" class="px-6 py-4 text-center">Probabilidad Fuga</th>
                            <th scope="col" class="px-6 py-4">Factor Clave</th>
                            <th scope="col" class="px-6 py-4">Estimación</th>
                            <th scope="col" class="px-4 py-4 text-center w-16">
                                <span class="sr-only">Ver</span> </th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-800">
                        {#each filteredEmployees as emp (emp.id)}
                            <tr class="group hover:bg-gray-800/60 transition-colors duration-200" in:fly={{ y: 10, duration: 200 }}>
                                
                                <td class="px-6 py-4 font-medium text-white">
                                    <a href="/dashboard/predicciones/{emp.id}" class="hover:text-orange-400 transition-colors">
                                        {emp.nombre}
                                    </a>
                                </td>
            
                                <td class="px-6 py-4">
                                    <div class="flex flex-col">
                                        <span class="text-gray-300 font-medium">{emp.cargo}</span>
                                        <span class="text-xs text-gray-500 mt-0.5">{emp.area}</span>
                                    </div>
                                </td>
            
                                <td class="px-6 py-4">
                                    <div class="flex flex-col items-center justify-center gap-1">
                                        <span class="font-bold text-lg {emp.probabilidad >= 70 ? 'text-red-400' : emp.probabilidad >= 40 ? 'text-orange-400' : 'text-green-400'}">
                                            {emp.probabilidad}%
                                        </span>
                                        <div class="w-20 bg-gray-700 rounded-full h-1.5 overflow-hidden">
                                            <div class="h-full rounded-full {getProgressBarColor(emp.probabilidad)} transition-all duration-500" style="width: {emp.probabilidad}%"></div>
                                        </div>
                                    </div>
                                </td>
            
                                <td class="px-6 py-4">
                                    <span class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium border border-gray-700 bg-gray-800 text-gray-300 whitespace-nowrap shadow-sm group-hover:border-gray-600 transition-colors">
                                        {emp.factor}
                                    </span>
                                </td>
            
                                <td class="px-6 py-4 font-mono text-gray-400 text-xs">
                                    {emp.fechaEstimada}
                                </td>
                                
                                <td class="px-4 py-4 text-center">
                                    <a 
                                        href="/dashboard/predicciones/{emp.id}" 
                                        class="inline-flex items-center justify-center w-8 h-8 rounded-lg bg-gray-800 text-gray-400 hover:text-white hover:bg-orange-600 transition-all shadow-md hover:shadow-orange-900/20 border border-gray-700 hover:border-orange-500 group-hover:translate-x-1"
                                        title="Ver detalles de {emp.nombre}"
                                    >
                                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                                        </svg>
                                    </a>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
            
            {#if filteredEmployees.length === 0}
                <div class="p-8 text-center text-gray-500">
                    No se encontraron empleados con los filtros seleccionados.
                </div>
            {/if}
            
        </div>
    </div>
</div>