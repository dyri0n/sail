import type { PageServerLoad } from './$types';
import { PUBLIC_API_BASE_URL as API_BASE_URL } from '$env/static/public';

// Función para formatear fechas UTC del backend a hora de Chile
function formatChileDate(dateString: string | null): string {
    if (!dateString) return 'Pendiente';

    try {
        // El backend envía fechas en UTC sin 'Z', agregarlo si falta
        let isoString = dateString;
        if (!isoString.endsWith('Z') && !isoString.includes('+') && !isoString.includes('-', 10)) {
            isoString = dateString + 'Z';
        }

        const date = new Date(isoString);

        // Formatear en español chileno con zona horaria de Chile
        return date.toLocaleString('es-CL', {
            timeZone: 'America/Santiago',
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
    } catch (error) {
        console.error('Error formateando fecha:', error);
        return 'Fecha inválida';
    }
}

export const load: PageServerLoad = async ({ cookies, locals }) => {
    const token = cookies.get('access_token');

    // Obtener historial real del backend
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/etl/history?limit=50`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Error al cargar historial');
        }

        const data = await response.json();
        const rawHistory = data.history || [];

        // Transformar datos para la vista
        const history = rawHistory.map((item: any) => {
            const startDate = item.start_date || item.execution_date;
            const endDate = item.end_date;

            // Calcular duración si no viene pre-calculada
            let duracionStr = 'N/A';
            if (item.duration) {
                const min = Math.floor(item.duration / 60);
                const sec = item.duration % 60;
                duracionStr = `${min}m ${sec}s`;
            } else if (startDate && endDate) {
                const diff = (new Date(endDate).getTime() - new Date(startDate).getTime()) / 1000;
                if (diff >= 0) {
                    const min = Math.floor(diff / 60);
                    const sec = Math.floor(diff % 60);
                    duracionStr = `${min}m ${sec}s`;
                }
            }

            return {
                id: item.id,
                fecha: formatChileDate(startDate),
                estado: item.state === 'success' ? 'Exitoso' : (item.state === 'failed' ? 'Fallido' : 'En Progreso'),
                duracion: duracionStr,
                registros: 0, // El backend aun no reporta filas procesadas
                usuario: 'Admin', // TODO: Traer nombre real del usuario si está disponible
                detalles: `Run ID: ${item.dag_run_id}`
            };
        });

        // Calcular estadísticas reales
        const total = history.length;
        const exitosos = history.filter((h: any) => h.estado === 'Exitoso').length;
        const tasaExito = total > 0 ? Math.round((exitosos / total) * 100) + '%' : '0%';

        // Calcular duración promedio (solo de los que tienen duración parseable)
        let totalSeconds = 0;
        let countDuration = 0;
        rawHistory.forEach((h: any) => {
            if (h.duration) {
                totalSeconds += h.duration;
                countDuration++;
            }
        });

        let promedioDuracion = '0m 0s';
        if (countDuration > 0) {
            const avgSec = Math.floor(totalSeconds / countDuration);
            promedioDuracion = `${Math.floor(avgSec / 60)}m ${avgSec % 60}s`;
        }

        return {
            history,
            stats: {
                total,
                tasaExito,
                promedioDuracion
            }
        };

    } catch (error) {
        console.error("Error cargando historial ETL:", error);
        // Fallback a array vacío en error
        return {
            history: [],
            stats: {
                total: 0,
                tasaExito: '0%',
                promedioDuracion: '0m 0s'
            }
        };
    }
};