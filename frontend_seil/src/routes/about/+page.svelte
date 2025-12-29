<script lang="ts">
    import { fly } from 'svelte/transition';
    
    // Datos (Sin cambios)
    const techStack = [
        { name: 'SvelteKit', type: 'Frontend Framework', color: 'text-orange-500', bg: 'bg-orange-500/10', border: 'border-orange-500/20' },
        { name: 'Tailwind CSS', type: 'Estilos & UI', color: 'text-cyan-400', bg: 'bg-cyan-400/10', border: 'border-cyan-400/20' },
        { name: 'Python / Pandas', type: 'Motor ETL & AI', color: 'text-blue-400', bg: 'bg-blue-400/10', border: 'border-blue-400/20' },
        { name: 'TypeScript', type: 'Lógica Segura', color: 'text-blue-600', bg: 'bg-blue-600/10', border: 'border-blue-600/20' }
    ];

    const modules = [
        { title: 'Ingesta de Datos', desc: 'Sistema de carga dual (Staging/Producción) para archivos Excel operacionales.', icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12' },
        { title: 'Procesamiento ETL', desc: 'Limpieza, normalización y estructuración de datos crudos para el Data Warehouse.', icon: 'M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z' },
        { title: 'Inteligencia Artificial', desc: 'Algoritmos predictivos para la detección temprana de rotación de personal.', icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z' },
        { title: 'Seguridad & Auditoría', desc: 'Trazabilidad completa de acciones de usuario y gestión de roles.', icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z' }
    ];
</script>

<div class="flex flex-col gap-8 px-4 py-8 lg:py-10 max-w-7xl mx-auto">

    <div class="flex items-center mb-2">
        <a href="/" class="group flex items-center gap-3 px-5 py-2.5 rounded-full bg-gray-800 border border-gray-700 hover:bg-gray-750 hover:border-gray-500 transition-all duration-300 shadow-lg hover:shadow-xl hover:-translate-x-1">
            <svg class="w-4 h-4 text-gray-400 group-hover:text-white transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span class="text-sm font-medium text-gray-300 group-hover:text-white transition-colors">Volver al Inicio</span>
        </a>
    </div>

    <div class="relative bg-gradient-to-r from-gray-900 to-gray-800 rounded-3xl p-8 lg:p-12 overflow-hidden border border-gray-700 shadow-2xl">
        <div class="absolute top-0 right-0 -mt-10 -mr-10 w-64 h-64 bg-red-600/10 rounded-full blur-3xl"></div>
        <div class="absolute bottom-0 left-0 -mb-10 -ml-10 w-64 h-64 bg-purple-600/10 rounded-full blur-3xl"></div>

        <div class="relative z-10 max-w-3xl">
            <div class="inline-flex items-center px-3 py-1 rounded-full bg-gray-800 border border-gray-600 text-xs font-medium text-gray-300 mb-6">
                <span class="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                Sistema Operativo v2.4.0
            </div>
            <h1 class="text-4xl lg:text-5xl font-bold text-white mb-4 leading-tight">
                Plataforma de Analítica <br>
                <span class="text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-red-600">Luckia Casino Arica</span>
            </h1>
            <p class="text-gray-400 text-lg leading-relaxed">
                Una solución integral de Business Intelligence diseñada para transformar datos operacionales en decisiones estratégicas. Integra procesos ETL automatizados, gestión documental segura y modelos predictivos de Recursos Humanos.
            </p>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6" in:fly={{ y: 20, duration: 400, delay: 100 }}>
        <div class="bg-gray-900 rounded-2xl border border-gray-700 p-6 shadow-lg">
            <h3 class="text-xl font-bold text-white mb-6">Stack Tecnológico</h3>
            <div class="space-y-4">
                {#each techStack as tech}
                    <div class="flex items-center p-3 rounded-xl border {tech.border} {tech.bg} transition-transform hover:scale-105">
                        <div class="w-2 h-2 rounded-full {tech.color.replace('text', 'bg')} mr-3"></div>
                        <div>
                            <p class="text-white font-bold text-sm">{tech.name}</p>
                            <p class="{tech.color} text-xs">{tech.type}</p>
                        </div>
                    </div>
                {/each}
            </div>
        </div>

        <div class="lg:col-span-2 bg-gray-900 rounded-2xl border border-gray-700 p-6 shadow-lg flex flex-col justify-center relative overflow-hidden">
            <h3 class="text-xl font-bold text-white mb-8 z-10">Flujo de Datos del Sistema</h3>
            
            <div class="relative z-10 flex flex-col md:flex-row justify-between items-center gap-4 md:gap-0 px-4">
                <div class="flex flex-col items-center text-center group">
                    <div class="w-16 h-16 rounded-2xl bg-gray-800 border border-gray-600 flex items-center justify-center shadow-lg group-hover:border-green-500 transition-colors">
                        <svg class="w-8 h-8 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                    </div>
                    <p class="text-gray-300 text-sm mt-3 font-medium">Excel / Origen</p>
                </div>

                <div class="hidden md:block h-0.5 w-full bg-gray-700 relative mx-4"><div class="absolute right-0 -top-1.5 w-3 h-3 border-t-2 border-r-2 border-gray-700 rotate-45"></div></div>
                <div class="md:hidden w-0.5 h-12 bg-gray-700 my-2"></div>

                <div class="flex flex-col items-center text-center group">
                    <div class="w-16 h-16 rounded-2xl bg-gray-800 border border-gray-600 flex items-center justify-center shadow-lg group-hover:border-red-500 transition-colors">
                        <svg class="w-8 h-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
                    </div>
                    <p class="text-gray-300 text-sm mt-3 font-medium">Motor ETL</p>
                </div>

                <div class="hidden md:block h-0.5 w-full bg-gray-700 relative mx-4"><div class="absolute right-0 -top-1.5 w-3 h-3 border-t-2 border-r-2 border-gray-700 rotate-45"></div></div>
                <div class="md:hidden w-0.5 h-12 bg-gray-700 my-2"></div>

                <div class="flex flex-col items-center text-center group">
                    <div class="w-16 h-16 rounded-2xl bg-gray-800 border border-gray-600 flex items-center justify-center shadow-lg group-hover:border-purple-500 transition-colors">
                        <svg class="w-8 h-8 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                    </div>
                    <p class="text-gray-300 text-sm mt-3 font-medium">Modelos IA</p>
                </div>

                <div class="hidden md:block h-0.5 w-full bg-gray-700 relative mx-4"><div class="absolute right-0 -top-1.5 w-3 h-3 border-t-2 border-r-2 border-gray-700 rotate-45"></div></div>
                <div class="md:hidden w-0.5 h-12 bg-gray-700 my-2"></div>

                <div class="flex flex-col items-center text-center group">
                    <div class="w-16 h-16 rounded-2xl bg-gray-800 border border-gray-600 flex items-center justify-center shadow-lg group-hover:border-blue-500 transition-colors">
                        <svg class="w-8 h-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>
                    </div>
                    <p class="text-gray-300 text-sm mt-3 font-medium">Dashboard</p>
                </div>
            </div>
            
            <div class="absolute inset-0 bg-[url('/grid.svg')] opacity-5"></div>
        </div>
    </div>

    <div class="mt-4">
        <h2 class="text-2xl font-bold text-white mb-6 pl-2">Módulos del Sistema</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {#each modules as mod, i}
                <div 
                    in:fly={{ y: 20, duration: 300, delay: 200 + (i * 50) }}
                    class="group bg-gray-800/50 hover:bg-gray-800 p-6 rounded-2xl border border-gray-700 hover:border-gray-500 transition-all duration-300 hover:-translate-y-1"
                >
                    <div class="w-12 h-12 bg-gray-700/50 rounded-xl flex items-center justify-center mb-4 group-hover:bg-white/10 transition-colors">
                        <svg class="w-6 h-6 text-gray-300 group-hover:text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={mod.icon} />
                        </svg>
                    </div>
                    <h4 class="text-lg font-bold text-white mb-2">{mod.title}</h4>
                    <p class="text-sm text-gray-400 leading-relaxed">{mod.desc}</p>
                </div>
            {/each}
        </div>
    </div>

    <div class="mt-8 border-t border-gray-800 pt-8 flex flex-col items-center">
        <p class="text-gray-500 text-sm">Desarrollado para el Departamento de Informática</p>
        <p class="text-gray-600 text-xs mt-1">© 2025 Luckia Arica • Versión de Desarrollo</p>
    </div>

</div>