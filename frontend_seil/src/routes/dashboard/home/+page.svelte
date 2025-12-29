<script lang="ts">
    import { goto } from '$app/navigation';
    // Recibimos los datos del archivo +page.server.ts automáticamente
    export let data;

    function navegar() {
        // Aquí podrías poner lógica extra si fuera necesario
        goto('/dashboard/usuarios');
    }
</script>

<div class="space-y-10">
    <!-- Header con bienvenida -->
    <div class="bg-gradient-to-r from-gray-900 to-gray-800 rounded-2xl p-8 shadow-xl">
        <div class="flex items-center space-x-4">
            <div class="w-16 h-16 bg-gradient-to-br from-red-600 to-red-700 rounded-xl flex items-center justify-center shadow-lg">
                <span class="text-2xl font-bold text-white">LA</span>
            </div>
            <div>
                <h1 class="text-4xl font-bold text-white">Hola, {data.user.nombre}</h1>
                <p class="text-gray-300 mt-2 text-lg">Panel de control de análisis de Luckia Casino</p>
            </div>
        </div>
    </div>

    <!-- Grid de funciones -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-4 gap-6">
        <!-- ETL -->
        <a href="/dashboard/etl" class="block group relative bg-gradient-to-br from-gray-900 to-gray-800 p-6 rounded-2xl border border-gray-700 hover:border-red-500 transition-all duration-300 text-left overflow-hidden shadow-lg hover:shadow-2xl transform hover:-translate-y-1">
            <div class="absolute inset-0 bg-gradient-to-r from-red-600/0 via-red-600/5 to-red-600/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000 pointer-events-none"></div>
            
            <div class="relative z-10 h-14 w-14 bg-gradient-to-br from-red-600/20 to-red-700/20 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                </svg>
            </div>
            <h3 class="font-bold text-xl text-white mb-2">Ejecutar ETL</h3>
            <p class="text-gray-400 text-sm">Procesar y transformar datos operacionales</p>
            
            <div class="mt-4 flex items-center text-red-400 text-sm font-medium">
                <span>Iniciar proceso</span>
                <svg class="w-4 h-4 ml-2 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
                </svg>
            </div>
        </a>
        <!-- User Activity -->
        <a href="/dashboard/usuarios" class="btn-effect block group relative bg-gradient-to-br from-gray-900 to-gray-800 p-6 rounded-2xl border border-gray-700 hover:border-green-500 transition-all duration-300 text-left overflow-hidden shadow-lg hover:shadow-2xl transform hover:-translate-y-1">
            
            <div class="absolute inset-0 bg-gradient-to-r from-green-600/0 via-green-600/5 to-green-600/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000 pointer-events-none"></div>
            
            <div class="relative z-10 h-14 w-14 bg-gradient-to-br from-green-600/20 to-green-700/20 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
            </div>
            <h3 class="font-bold text-xl text-white mb-2">Actividad Usuarios</h3>
            <p class="text-gray-400 text-sm">Monitorizar sesiones y acciones</p>
            
            <div class="mt-4 flex items-center text-green-400 text-sm font-medium">
                <span>Ver análisis</span>
                <svg class="w-4 h-4 ml-2 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
                </svg>
            </div>
        </a>

        <!-- Files -->
        <a href="/dashboard/directorios" class="block group relative bg-gradient-to-br from-gray-900 to-gray-800 p-6 rounded-2xl border border-gray-700 hover:border-purple-500 transition-all duration-300 text-left overflow-hidden shadow-lg hover:shadow-2xl transform hover:-translate-y-1">
    
            <div class="absolute inset-0 bg-gradient-to-r from-purple-600/0 via-purple-600/5 to-purple-600/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000 pointer-events-none"></div>
            
            <div class="relative z-10 h-14 w-14 bg-gradient-to-br from-purple-600/20 to-purple-700/20 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 19a2 2 0 01-2-2V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1M5 19h14a2 2 0 002-2v-5a2 2 0 00-2-2H9a2 2 0 00-2 2v5a2 2 0 01-2 2z" />
                </svg>
            </div>
            <h3 class="font-bold text-xl text-white mb-2">Archivos</h3>
            <p class="text-gray-400 text-sm">Explorar carpeta compartida</p>
            
            <div class="mt-4 flex items-center text-purple-400 text-sm font-medium">
                <span>Abrir archivos</span>
                <svg class="w-4 h-4 ml-2 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
                </svg>
            </div>
        </a>

        <!-- Predictive Model -->
        <a href="/dashboard/predicciones" class="block group relative bg-gradient-to-br from-gray-900 to-gray-800 p-6 rounded-2xl border border-gray-700 hover:border-orange-500 transition-all duration-300 text-left overflow-hidden shadow-lg hover:shadow-2xl transform hover:-translate-y-1">
            <div class="absolute inset-0 bg-gradient-to-r from-orange-600/0 via-orange-600/5 to-orange-600/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000 pointer-events-none"></div>
            
            <div class="relative z-10 h-14 w-14 bg-gradient-to-br from-orange-600/20 to-orange-700/20 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
            </div>
            <h3 class="font-bold text-xl text-white mb-2">Modelo Predictivo</h3>
            <p class="text-gray-400 text-sm">Análisis y tendencias futuras</p>
            
            <div class="mt-4 flex items-center text-orange-400 text-sm font-medium">
                <span>Ver predicciones</span>
                <svg class="w-4 h-4 ml-2 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
                </svg>
            </div>
        </a>
    </div>

    <!-- Sección informativa -->
    <div class="mt-12 p-6 bg-gradient-to-r from-gray-800/50 to-gray-900/50 rounded-2xl border border-gray-700">
        <h3 class="text-xl font-semibold text-white mb-4">📊 Acceso Rápido a Funciones</h3>
        <p class="text-gray-400 mb-4">
            Selecciona cualquiera de las opciones para acceder a las herramientas de análisis de Luckia Casino. 
            Todas las funciones están optimizadas para el procesamiento de datos en tiempo real.
        </p>
        <div class="flex items-center text-sm text-gray-500">
            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"></path>
            </svg>
            Última actualización: Hace 5 minutos
        </div>
    </div>
</div>

<style>
    /* Animaciones personalizadas */
    .group:hover .group-hover\:scale-110 {
        transform: scale(1.1);
    }
    
    .group:hover .group-hover\:-translate-y-1 {
        transform: translateY(-4px);
    }
    
    /* Suavizar las transiciones */
    * {
        transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Efecto de brillo en los bordes */
    button {
        position: relative;
        overflow: hidden;
    }
    
    button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.1),
            transparent
        );
        transition: left 0.7s;
    }
    
    button:hover::before {
        left: 100%;
    }
</style>