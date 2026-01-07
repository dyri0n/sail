<script lang="ts">
    import MetricCard from '$lib/components/MetricCard.svelte';
    import LineChart from '$lib/components/charts/LineChart.svelte';
    import BarChart from '$lib/components/charts/BarChart.svelte';
    import PieChart from '$lib/components/charts/PieChart.svelte';
    
    export let data;

    // Función para formatear números con separador de miles
    function formatNumber(num: number): string {
        return new Intl.NumberFormat('es-CL').format(num);
    }

    // Procesar datos para gráficos
    $: chartData = data.metrics ? {
        // Asistencia - Ausentismo mensual
        ausentismo: {
            labels: data.metrics.asistencia.tasa_ausentismo_mensual.map((m) => m.label),
            datasets: [{
                label: 'Tasa de Ausentismo (%)',
                data: data.metrics.asistencia.tasa_ausentismo_mensual.map((m) => m.value),
                borderColor: 'rgb(239, 68, 68)',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                tension: 0.3
            }]
        },
        // Asistencia - Atrasos mensual
        atrasos: {
            labels: data.metrics.asistencia.tasa_atrasos_mensual.map((m) => m.label),
            datasets: [{
                label: 'Tasa de Atrasos (%)',
                data: data.metrics.asistencia.tasa_atrasos_mensual.map((m) => m.value),
                backgroundColor: 'rgba(251, 146, 60, 0.8)',
            }]
        },
        // Rotación - Headcount
        headcount: {
            labels: data.metrics.rotacion.headcount_mensual.map((m) => m.label),
            datasets: [{
                label: 'Headcount',
                data: data.metrics.rotacion.headcount_mensual.map((m) => m.value),
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.3
            }]
        },
        // Rotación - Altas vs Bajas
        movimientos: {
            labels: data.metrics.rotacion.altas_mensuales.map((m) => m.label),
            datasets: [
                {
                    label: 'Altas',
                    data: data.metrics.rotacion.altas_mensuales.map((m) => m.value),
                    backgroundColor: 'rgba(34, 197, 94, 0.8)',
                },
                {
                    label: 'Bajas',
                    data: data.metrics.rotacion.bajas_mensuales.map((m) => m.value),
                    backgroundColor: 'rgba(239, 68, 68, 0.8)',
                }
            ]
        },
        // Selección - Fuentes de reclutamiento
        fuentes: {
            labels: data.metrics.seleccion.fuentes_reclutamiento.map((f) => f.label),
            datasets: [{
                data: data.metrics.seleccion.fuentes_reclutamiento.map((f) => f.value),
                backgroundColor: [
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(251, 146, 60, 0.8)',
                    'rgba(168, 85, 247, 0.8)',
                    'rgba(236, 72, 153, 0.8)',
                ]
            }]
        },
        // Capacitación - Horas mensuales
        capacitacion: {
            labels: data.metrics.capacitacion.horas_capacitacion_mensual.map((m) => m.label),
            datasets: [{
                label: 'Horas de Capacitación',
                data: data.metrics.capacitacion.horas_capacitacion_mensual.map((m) => m.value),
                borderColor: 'rgb(168, 85, 247)',
                backgroundColor: 'rgba(168, 85, 247, 0.1)',
                tension: 0.3
            }]
        },
        // Capacitación - Participación por categoría
        categorias: {
            labels: data.metrics.capacitacion.participacion_por_categoria.map((c) => c.label),
            datasets: [{
                label: 'Participantes',
                data: data.metrics.capacitacion.participacion_por_categoria.map((c) => c.value),
                backgroundColor: 'rgba(168, 85, 247, 0.8)',
            }]
        }
    } : null;
</script>

<div class="space-y-8">
    <!-- Header -->
    <div class="bg-gradient-to-r from-gray-900 to-gray-800 rounded-2xl p-8 shadow-xl">
        <div class="flex items-center justify-between">
            <div>
                <h1 class="text-4xl font-bold text-white mb-2">📊 Métricas Claves</h1>
                <p class="text-gray-300 text-lg">Dashboard integral de indicadores de RRHH</p>
            </div>
            {#if data.metrics}
                <div class="text-right">
                    <p class="text-gray-400 text-sm">Período</p>
                    <p class="text-white font-medium">
                        {new Date(data.metrics.periodo_inicio).toLocaleDateString('es-CL')} - 
                        {new Date(data.metrics.periodo_fin).toLocaleDateString('es-CL')}
                    </p>
                </div>
            {/if}
        </div>
    </div>

    {#if data.error}
        <div class="bg-red-900/20 border border-red-500 rounded-xl p-6">
            <h3 class="text-red-400 font-bold mb-2">Error al cargar métricas</h3>
            <p class="text-gray-300">{data.error}</p>
        </div>
    {:else if data.metrics}
        <!-- KPI Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
                title="Headcount Actual"
                value={formatNumber(data.metrics.rotacion.headcount_actual)}
                subtitle="Empleados activos"
                icon="neutral"
                color="blue"
            />
            <MetricCard
                title="Tasa de Rotación"
                value="{data.metrics.rotacion.tasa_rotacion}%"
                subtitle="Del período"
                icon={data.metrics.rotacion.tasa_rotacion > 10 ? 'down' : 'neutral'}
                color={data.metrics.rotacion.tasa_rotacion > 10 ? 'red' : 'green'}
            />
            <MetricCard
                title="Ausentismo"
                value="{data.metrics.asistencia.total_ausencias}"
                subtitle="Ausencias registradas"
                icon="down"
                color="orange"
            />
            <MetricCard
                title="Horas Capacitación"
                value={formatNumber(Math.round(data.metrics.capacitacion.total_horas_capacitacion))}
                subtitle="{formatNumber(data.metrics.capacitacion.total_participantes)} participantes"
                icon="up"
                color="purple"
            />
        </div>

        <!-- Asistencia Section -->
        <div>
            <h2 class="text-2xl font-bold text-white mb-4 flex items-center">
                <span class="w-2 h-8 bg-red-500 rounded mr-3"></span>
                Asistencia y Puntualidad
            </h2>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="bg-gradient-to-br from-gray-900 to-gray-800 p-6 rounded-2xl border border-gray-700 shadow-lg">
                    <LineChart data={chartData.ausentismo} title="Tasa de Ausentismo Mensual" height={300} />
                </div>
                <div class="bg-gradient-to-br from-gray-900 to-gray-800 p-6 rounded-2xl border border-gray-700 shadow-lg">
                    <BarChart data={chartData.atrasos} title="Tasa de Atrasos Mensual" height={300} />
                </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                <MetricCard
                    title="Total Ausencias"
                    value={formatNumber(data.metrics.asistencia.total_ausencias)}
                    color="red"
                    icon="neutral"
                />
                <MetricCard
                    title="Total Atrasos"
                    value={formatNumber(data.metrics.asistencia.total_atrasos)}
                    color="orange"
                    icon="neutral"
                />
                <MetricCard
                    title="Promedio Atraso"
                    value="{Math.round(data.metrics.asistencia.promedio_minutos_atraso)} min"
                    color="orange"
                    icon="neutral"
                />
            </div>
        </div>

        <!-- Rotación Section -->
        <div>
            <h2 class="text-2xl font-bold text-white mb-4 flex items-center">
                <span class="w-2 h-8 bg-blue-500 rounded mr-3"></span>
                Rotación y Dotación
            </h2>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="bg-gradient-to-br from-gray-900 to-gray-800 p-6 rounded-2xl border border-gray-700 shadow-lg">
                    <LineChart data={chartData.headcount} title="Evolución de Headcount" height={300} />
                </div>
                <div class="bg-gradient-to-br from-gray-900 to-gray-800 p-6 rounded-2xl border border-gray-700 shadow-lg">
                    <BarChart data={chartData.movimientos} title="Altas vs Bajas Mensuales" height={300} stacked={false} />
                </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                <MetricCard
                    title="Total Altas"
                    value={formatNumber(data.metrics.rotacion.total_altas)}
                    color="green"
                    icon="up"
                />
                <MetricCard
                    title="Total Bajas"
                    value={formatNumber(data.metrics.rotacion.total_bajas)}
                    color="red"
                    icon="down"
                />
                <MetricCard
                    title="Tasa Rotación"
                    value="{data.metrics.rotacion.tasa_rotacion.toFixed(1)}%"
                    color={data.metrics.rotacion.tasa_rotacion > 10 ? 'red' : 'green'}
                    icon="neutral"
                />
            </div>
        </div>

        <!-- Selección Section -->
        <div>
            <h2 class="text-2xl font-bold text-white mb-4 flex items-center">
                <span class="w-2 h-8 bg-green-500 rounded mr-3"></span>
                Selección y Reclutamiento
            </h2>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="bg-gradient-to-br from-gray-900 to-gray-800 p-6 rounded-2xl border border-gray-700 shadow-lg">
                    {#if data.metrics.seleccion.fuentes_reclutamiento.length > 0}
                        <PieChart data={chartData.fuentes} title="Fuentes de Reclutamiento" height={300} />
                    {:else}
                        <div class="h-[300px] flex items-center justify-center text-gray-500">
                            No hay datos de fuentes de reclutamiento
                        </div>
                    {/if}
                </div>
                <div class="grid grid-cols-1 gap-4 content-start">
                    <MetricCard
                        title="Tiempo Promedio Contratación"
                        value="{data.metrics.seleccion.tiempo_contratacion_promedio} días"
                        color="green"
                        icon="neutral"
                    />
                    <MetricCard
                        title="Candidatos por Vacante"
                        value={data.metrics.seleccion.candidatos_por_vacante.toFixed(1)}
                        color="blue"
                        icon="neutral"
                    />
                    <MetricCard
                        title="Tasa de Continuidad"
                        value="{data.metrics.seleccion.continuidad_rate.toFixed(1)}%"
                        subtitle="Empleados que permanecen +3 meses"
                        color={data.metrics.seleccion.continuidad_rate > 80 ? 'green' : 'orange'}
                        icon={data.metrics.seleccion.continuidad_rate > 80 ? 'up' : 'neutral'}
                    />
                </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <MetricCard
                    title="Procesos Cerrados"
                    value={formatNumber(data.metrics.seleccion.procesos_cerrados)}
                    color="green"
                    icon="neutral"
                />
                <MetricCard
                    title="Procesos Activos"
                    value={formatNumber(data.metrics.seleccion.procesos_activos)}
                    color="blue"
                    icon="neutral"
                />
            </div>
        </div>

        <!-- Capacitación Section -->
        <div>
            <h2 class="text-2xl font-bold text-white mb-4 flex items-center">
                <span class="w-2 h-8 bg-purple-500 rounded mr-3"></span>
                Capacitación y Desarrollo
            </h2>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="bg-gradient-to-br from-gray-900 to-gray-800 p-6 rounded-2xl border border-gray-700 shadow-lg">
                    <LineChart data={chartData.capacitacion} title="Horas de Capacitación Mensual" height={300} />
                </div>
                <div class="bg-gradient-to-br from-gray-900 to-gray-800 p-6 rounded-2xl border border-gray-700 shadow-lg">
                    {#if data.metrics.capacitacion.participacion_por_categoria.length > 0}
                        <BarChart data={chartData.categorias} title="Participación por Categoría" height={300} />
                    {:else}
                        <div class="h-[300px] flex items-center justify-center text-gray-500">
                            No hay datos de participación por categoría
                        </div>
                    {/if}
                </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
                <MetricCard
                    title="Total Horas"
                    value={formatNumber(Math.round(data.metrics.capacitacion.total_horas_capacitacion))}
                    color="purple"
                    icon="neutral"
                />
                <MetricCard
                    title="Total Participantes"
                    value={formatNumber(data.metrics.capacitacion.total_participantes)}
                    color="purple"
                    icon="neutral"
                />
                <MetricCard
                    title="Satisfacción Promedio"
                    value={data.metrics.capacitacion.promedio_satisfaccion.toFixed(1)}
                    subtitle="Sobre 5.0"
                    color={data.metrics.capacitacion.promedio_satisfaccion > 4 ? 'green' : 'orange'}
                    icon="neutral"
                />
                <MetricCard
                    title="NPS Promedio"
                    value={Math.round(data.metrics.capacitacion.promedio_nps)}
                    color={data.metrics.capacitacion.promedio_nps > 50 ? 'green' : 'orange'}
                    icon="neutral"
                />
            </div>
        </div>
    {:else}
        <div class="bg-gray-800/50 rounded-xl p-12 text-center">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-red-500 mb-4"></div>
            <p class="text-gray-400">Cargando métricas...</p>
        </div>
    {/if}
</div>
