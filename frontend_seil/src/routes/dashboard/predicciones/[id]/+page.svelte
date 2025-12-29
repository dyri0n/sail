<script lang="ts">
    import { fly, fade } from 'svelte/transition';
    export let data;
    const { employee } = data;

    // Función para color del riesgo
    const getRiskColor = (score: number) => {
        if (score >= 70) return 'text-red-500 from-red-500 to-red-600';
        if (score >= 40) return 'text-orange-400 from-orange-400 to-orange-500';
        return 'text-green-500 from-green-400 to-green-500';
    };

    // Calcular coordenadas para el gráfico simple de SVG
    const historyPoints = employee.riesgo.historial.map((val, i) => {
        const x = (i / (employee.riesgo.historial.length - 1)) * 100;
        const y = 100 - val; // Invertir Y porque SVG 0 es arriba
        return `${x},${y}`;
    }).join(' ');
</script>

<div class="flex flex-col gap-6 max-w-7xl mx-auto pb-10 px-4 lg:px-0">
    
    <div>
        <a href="/dashboard/predicciones" class="inline-flex items-center text-gray-400 hover:text-white transition-colors group">
            <div class="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center mr-3 border border-gray-700 group-hover:border-gray-500 transition-all">
                <svg class="w-4 h-4 transform group-hover:-translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
            </div>
            <span class="font-medium">Volver a Predicciones</span>
        </a>
    </div>

    <div in:fly={{ y: 20, duration: 400 }} class="bg-gradient-to-r from-gray-900 to-gray-800 rounded-3xl p-6 lg:p-8 border border-gray-700 shadow-2xl relative overflow-hidden">
        <div class="absolute top-0 right-0 w-96 h-96 bg-orange-600/5 rounded-full blur-3xl -mr-20 -mt-20"></div>

        <div class="relative z-10 flex flex-col md:flex-row gap-8 items-center md:items-start">
            
            <div class="flex flex-col items-center md:items-start flex-1 text-center md:text-left">
                <div class="w-24 h-24 rounded-2xl bg-gray-700 mb-4 border-2 border-gray-600 flex items-center justify-center text-3xl font-bold text-gray-400 shadow-lg">
                    {employee.nombre.charAt(0)}
                </div>
                <h1 class="text-3xl font-bold text-white">{employee.nombre}</h1>
                <p class="text-orange-400 text-lg font-medium">{employee.cargo}</p>
                <div class="flex gap-4 mt-4 text-sm text-gray-400">
                    <div class="flex items-center">
                        <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
                        {employee.area}
                    </div>
                    <div class="flex items-center">
                        <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                        {employee.antiguedad}
                    </div>
                </div>
            </div>

            <div class="flex flex-col items-center justify-center p-6 bg-gray-900/50 rounded-2xl border border-gray-700/50 backdrop-blur-sm">
                <p class="text-gray-400 text-sm font-medium uppercase tracking-wider mb-2">Probabilidad de Fuga</p>
                <div class="relative w-32 h-32 flex items-center justify-center">
                    <svg class="w-full h-full transform -rotate-90">
                        <circle cx="64" cy="64" r="56" stroke="currentColor" stroke-width="12" fill="transparent" class="text-gray-800" />
                        <circle cx="64" cy="64" r="56" stroke="currentColor" stroke-width="12" fill="transparent" 
                            stroke-dasharray="351.86" 
                            stroke-dashoffset={351.86 - (351.86 * employee.riesgo.score) / 100}
                            class="{getRiskColor(employee.riesgo.score)}"
                            stroke-linecap="round"
                        />
                    </svg>
                    <div class="absolute inset-0 flex flex-col items-center justify-center">
                        <span class="text-3xl font-bold text-white">{employee.riesgo.score}%</span>
                        <span class="text-xs font-bold uppercase {employee.riesgo.score >= 70 ? 'text-red-400' : 'text-green-400'}">
                            {employee.riesgo.nivel}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <div class="lg:col-span-2 space-y-6" in:fly={{ y: 20, duration: 400, delay: 100 }}>
            
            <div class="bg-gray-900 border border-orange-500/30 rounded-2xl p-6 shadow-lg relative overflow-hidden">
                <div class="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-orange-500 to-red-500"></div>
                <h3 class="text-lg font-bold text-white mb-2 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                    Análisis de IA
                </h3>
                <p class="text-gray-300 leading-relaxed text-sm lg:text-base">
                    {employee.iaInsight}
                </p>
            </div>

            <div class="bg-gray-900 rounded-2xl border border-gray-700 p-6 shadow-lg">
                <h3 class="text-lg font-bold text-white mb-6">Factores Clave de Riesgo</h3>
                <div class="space-y-6">
                    {#each employee.factores as factor}
                        <div>
                            <div class="flex justify-between items-end mb-1">
                                <span class="font-medium text-white">{factor.nombre}</span>
                                <span class="text-xs font-mono {factor.impacto > 50 ? 'text-red-400' : 'text-gray-400'}">
                                    Impacto: {factor.impacto}%
                                </span>
                            </div>
                            <div class="w-full bg-gray-800 rounded-full h-2.5 mb-2 overflow-hidden">
                                <div class="bg-gradient-to-r {getRiskColor(factor.impacto)} h-2.5 rounded-full" style="width: {factor.impacto}%"></div>
                            </div>
                            <p class="text-xs text-gray-500">{factor.descripcion}</p>
                        </div>
                    {/each}
                </div>
            </div>

            <div class="bg-gray-900 rounded-2xl border border-gray-700 p-6 shadow-lg">
                <h3 class="text-lg font-bold text-white mb-4">Historial de Riesgo (6 Meses)</h3>
                
                <div class="h-48 w-full relative mt-6 px-2">
                    
                    <div class="absolute inset-0 flex flex-col justify-between text-xs text-gray-600 pointer-events-none border-l border-gray-800 ml-1">
                        <span class="pl-2 border-t border-gray-800/50 w-full block pt-1">100%</span>
                        <span class="pl-2 border-t border-gray-800/50 w-full block pt-1">50%</span>
                        <span class="pl-2 border-t border-gray-800/50 w-full block pt-1">0%</span>
                    </div>

                    <svg class="absolute inset-0 w-full h-full overflow-visible" viewBox="0 0 100 100" preserveAspectRatio="none">
                        <defs>
                            <linearGradient id="gradientLine" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stop-color="#22c55e" /> <stop offset="50%" stop-color="#f97316" /> <stop offset="100%" stop-color="#ef4444" /> </linearGradient>
                            <linearGradient id="gradientArea" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" stop-color="#f97316" stop-opacity="0.2" />
                                <stop offset="100%" stop-color="#f97316" stop-opacity="0" />
                            </linearGradient>
                        </defs>

                        <polygon 
                            fill="url(#gradientArea)" 
                            points={`0,100 ${historyPoints} 100,100`}
                            class="opacity-70"
                        />

                        <polyline 
                            fill="none" 
                            stroke="url(#gradientLine)" 
                            stroke-width="3" 
                            points={historyPoints}
                            vector-effect="non-scaling-stroke"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        />
                    </svg>

                    <div class="absolute inset-0 w-full h-full">
                        {#each employee.riesgo.historial as val, i}
                            {@const x = (i / (employee.riesgo.historial.length - 1)) * 100}
                            {@const y = 100 - val}
                            
                            <div 
                                class="absolute w-4 h-4 rounded-full border-2 border-orange-500 bg-gray-900 cursor-pointer hover:scale-125 hover:bg-orange-500 hover:border-white transition-all duration-200 z-10 group shadow-lg shadow-black/50"
                                style="left: {x}%; top: {y}%; transform: translate(-50%, -50%);"
                            >
                                <div class="opacity-0 group-hover:opacity-100 absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1 bg-gray-800 border border-gray-600 text-white text-xs font-bold rounded-lg whitespace-nowrap shadow-xl pointer-events-none transition-opacity duration-200 z-20">
                                    Mes {i+1}: <span class="{val >= 70 ? 'text-red-400' : 'text-orange-400'}">{val}%</span>
                                    <div class="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-600"></div>
                                </div>
                            </div>
                        {/each}
                    </div>
                </div>
            </div>

            </div>

        <div class="space-y-6" in:fly={{ y: 20, duration: 400, delay: 200 }}>
            <div class="bg-gray-800 rounded-2xl border border-gray-700 p-6 shadow-lg sticky top-6">
                <h3 class="text-lg font-bold text-white mb-4">Plan de Retención</h3>
                
                <div class="space-y-3 mb-6">
                    {#each employee.accionesSugeridas as accion}
                        <div class="flex items-start gap-3 p-3 bg-gray-900/50 rounded-xl border border-gray-700/50">
                            <div class="mt-0.5 min-w-[1.25rem]">
                                <input type="checkbox" class="w-5 h-5 rounded border-gray-600 text-orange-600 focus:ring-orange-500 bg-gray-700">
                            </div>
                            <span class="text-sm text-gray-300">{accion}</span>
                        </div>
                    {/each}
                </div>

                <div class="flex flex-col gap-3">
                    <button class="w-full py-3 px-4 bg-orange-600 hover:bg-orange-700 text-white font-bold rounded-xl transition-colors shadow-lg shadow-orange-900/20 flex items-center justify-center">
                        <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                        Agendar Reunión 1:1
                    </button>
                    <button class="w-full py-3 px-4 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-xl transition-colors flex items-center justify-center">
                        <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                        Exportar Informe PDF
                    </button>
                </div>
                
                <div class="mt-6 pt-6 border-t border-gray-700 text-center">
                    <p class="text-xs text-gray-500 mb-2">¿Consideras que esta predicción es errónea?</p>
                    <button class="text-xs text-gray-400 hover:text-white underline">Reportar Falso Positivo</button>
                </div>
            </div>
        </div>
    </div>
</div>