import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
    // Estos datos vendrían de tu API de Python / Base de datos
    return {
        kpis: {
            riesgoPromedio: 34,
            empleadosCriticos: 12,
            areaMasCritica: 'Seguridad',
            proximaTemporadaAlta: 'Diciembre - Enero'
        },
        areas: [
            { nombre: 'Seguridad', riesgo: 78, tendencia: 'up', temporada: 'Verano', empleados: 45 },
            { nombre: 'Mesas de Juego', riesgo: 65, tendencia: 'stable', temporada: 'Fiestas Patrias', empleados: 32 },
            { nombre: 'Alimentos y Bebidas', riesgo: 42, tendencia: 'down', temporada: 'Fines de semana', empleados: 28 },
            { nombre: 'Tragamonedas', riesgo: 25, tendencia: 'stable', temporada: 'Constante', empleados: 15 },
            { nombre: 'Limpieza', riesgo: 55, tendencia: 'up', temporada: 'Invierno', empleados: 20 },
        ],
        empleados: [
            { id: 1, nombre: 'Juan Pérez', area: 'Seguridad', cargo: 'Guardia', probabilidad: 92, factor: 'Sobrecarga Horaria', fechaEstimada: '15 Nov 2025' },
            { id: 2, nombre: 'María González', area: 'Mesas', cargo: 'Croupier', probabilidad: 88, factor: 'Estancamiento Salarial', fechaEstimada: '01 Dic 2025' },
            { id: 3, nombre: 'Carlos Ruiz', area: 'Seguridad', cargo: 'Supervisor', probabilidad: 75, factor: 'Clima Laboral', fechaEstimada: '20 Ene 2026' },
            { id: 4, nombre: 'Ana López', area: 'A&B', cargo: 'Garzona', probabilidad: 65, factor: 'Oferta Competencia', fechaEstimada: 'Feb 2026' },
            { id: 5, nombre: 'Pedro Díaz', area: 'Limpieza', cargo: 'Auxiliar', probabilidad: 45, factor: 'Salud', fechaEstimada: 'Mar 2026' },
            { id: 6, nombre: 'Luisa Mora', area: 'Mesas', cargo: 'Jefe de Sala', probabilidad: 15, factor: 'N/A', fechaEstimada: 'Estable' },
            { id: 7, nombre: 'Jorge Tapia', area: 'Tragamonedas', cargo: 'Técnico', probabilidad: 12, factor: 'N/A', fechaEstimada: 'Estable' },
        ]
    };
};