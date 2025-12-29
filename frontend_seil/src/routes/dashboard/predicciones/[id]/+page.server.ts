import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
    const id = params.id;

    // Simulador simple: Genera datos distintos según si el ID es par o impar
    // Esto es ideal para la demo: ID 1 = Crítico, ID 2 = Seguro, etc.
    const isCritical = parseInt(id || '0') % 2 !== 0; // Impares son críticos

    const employeeData = {
        id: id,
        // Cambiamos el nombre según el ID para que se note la navegación
        nombre: isCritical ? 'Juan Pérez' : 'María González',
        cargo: isCritical ? 'Guardia de Seguridad' : 'Supervisor de Sala',
        area: isCritical ? 'Seguridad' : 'Operaciones',
        antiguedad: isCritical ? '3 años, 2 meses' : '5 años',
        edad: isCritical ? 34 : 42,
        foto: null,
        riesgo: {
            score: isCritical ? 92 : 35,
            nivel: isCritical ? 'Crítico' : 'Bajo',
            tendencia: isCritical ? 'up' : 'stable',
            // Historial diferente para cada caso
            historial: isCritical 
                ? [65, 68, 72, 80, 88, 92] // Tendencia subiendo (Tu caso original)
                : [40, 38, 35, 36, 34, 35] // Tendencia estable/baja
        },
        factores: isCritical ? [
            { nombre: 'Sobrecarga Horaria', impacto: 95, descripcion: 'Promedio de 12 horas extra semanales.' },
            { nombre: 'Estancamiento Salarial', impacto: 80, descripcion: 'Sin ajustes en 18 meses.' },
            { nombre: 'Distancia al Trabajo', impacto: 40, descripcion: 'Vive a 45 min del recinto.' },
            { nombre: 'Evaluación de Desempeño', impacto: 20, descripcion: 'Evaluación positiva.' }
        ] : [
            { nombre: 'Distancia al Trabajo', impacto: 15, descripcion: 'Vive cerca del recinto.' },
            { nombre: 'Carga Laboral', impacto: 10, descripcion: 'Horario normalizado.' }
        ],
        iaInsight: isCritical 
            ? "El modelo detecta un patrón de 'Burnout'. La combinación de horas extra y falta de incentivos ha disparado el riesgo."
            : "Empleado estable con buenos indicadores de retención. No se requieren acciones inmediatas.",
        accionesSugeridas: isCritical ? [
            "Programar reunión 1 a 1 para revisar carga laboral.",
            "Evaluar posibilidad de bono por desempeño.",
            "Ofrecer días compensatorios."
        ] : [
            "Mantener plan de carrera actual.",
            "Incluir en programa de mentoría."
        ]
    };

    if (!employeeData) {
        throw error(404, 'Empleado no encontrado');
    }

    return { employee: employeeData };
};