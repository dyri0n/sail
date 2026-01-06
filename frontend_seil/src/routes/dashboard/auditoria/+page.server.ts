// +page.server.ts
import type { PageServerLoad } from './$types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Definimos las interfaces de los datos
interface LogEntry {
  id: string;
  timestamp: string;
  nivel: 'INFO' | 'WARN' | 'ERROR' | 'SUCCESS' | 'DEBUG' | 'AUDIT';
  modulo: string;
  mensaje: string;
  usuario: string;
  ip?: string;
  detalles?: Record<string, any>;
}

interface LogStats {
  total: number;
  errores: number;
  auditoria: number;
  ultimo: string;
}

// Función para obtener logs desde la API real
async function fetchLogsFromAPI(accessToken: string): Promise<LogEntry[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/audit/logs?limit=100`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      console.error('Error fetching logs:', response.status, response.statusText);
      return [];
    }

    const data = await response.json();
    return data.logs || [];
  } catch (error) {
    console.error('Error fetching logs from API:', error);
    return [];
  }
}

// Función para obtener estadísticas desde la API
async function fetchStatsFromAPI(accessToken: string): Promise<LogStats> {
  try {
    const response = await fetch(`${API_BASE_URL}/audit/stats`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      console.error('Error fetching stats:', response.status, response.statusText);
      return { total: 0, errores: 0, auditoria: 0, ultimo: 'N/A' };
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching stats from API:', error);
    return { total: 0, errores: 0, auditoria: 0, ultimo: 'N/A' };
  }
}

// Función para obtener valores de filtros desde la API
async function getFilterValues(accessToken: string) {
  try {
    const response = await fetch(`${API_BASE_URL}/audit/filters`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      console.error('Error fetching filters:', response.status, response.statusText);
      return {
        niveles: ['todos', 'INFO', 'WARN', 'ERROR', 'SUCCESS', 'DEBUG', 'AUDIT'],
        modulos: ['todos', 'AUTH', 'ETL', 'ADMIN'],
        usuarios: ['todos']
      };
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching filters from API:', error);
    return {
      niveles: ['todos', 'INFO', 'WARN', 'ERROR', 'SUCCESS', 'DEBUG', 'AUDIT'],
      modulos: ['todos', 'AUTH', 'ETL', 'ADMIN'],
      usuarios: ['todos']
    };
  }
}

// Cargar datos para la página
export const load: PageServerLoad = async ({ cookies }) => {
  // Obtener token de autenticación
  const accessToken = cookies.get('access_token');

  if (!accessToken) {
    // Si no hay token, retornar datos vacíos
    return {
      logs: [],
      stats: { total: 0, errores: 0, auditoria: 0, ultimo: 'N/A' },
      filters: {
        niveles: ['todos'],
        modulos: ['todos'],
        usuarios: ['todos']
      },
      metadata: {
        title: 'Logs y Auditoría',
        description: 'Sistema de logs y auditoría del Casino Luckia',
        lastUpdated: new Date().toISOString(),
        error: 'No autenticado'
      }
    };
  }

  // Obtener logs, stats y filters en paralelo
  const [logs, stats, filters] = await Promise.all([
    fetchLogsFromAPI(accessToken),
    fetchStatsFromAPI(accessToken),
    getFilterValues(accessToken)
  ]);

  return {
    logs,
    stats,
    filters,
    metadata: {
      title: 'Logs y Auditoría',
      description: 'Sistema de logs y auditoría del Casino Luckia',
      lastUpdated: new Date().toISOString()
    }
  };
};

// Acciones para exportar datos
export const actions = {
  exportCSV: async ({ request, cookies }) => {
    const formData = await request.formData();
    const filterData = Object.fromEntries(formData);

    // Obtener token para hacer la petición
    const accessToken = cookies.get('access_token');
    if (!accessToken) {
      return {
        success: false,
        message: 'No autenticado'
      };
    }

    // Construir URL con filtros
    const params = new URLSearchParams();
    if (filterData.nivel && filterData.nivel !== 'todos') params.append('nivel', filterData.nivel as string);
    if (filterData.modulo && filterData.modulo !== 'todos') params.append('modulo', filterData.modulo as string);
    if (filterData.usuario && filterData.usuario !== 'todos') params.append('usuario', filterData.usuario as string);

    try {
      const response = await fetch(`${API_BASE_URL}/audit/logs?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        return {
          success: false,
          message: 'Error al obtener logs para exportar'
        };
      }

      const data = await response.json();
      const filteredLogs = data.logs || [];

      // Generar CSV
      const headers = ['Timestamp', 'Nivel', 'Módulo', 'Usuario', 'IP', 'Mensaje'];
      const csvRows = [];

      csvRows.push(headers.join(','));

      filteredLogs.forEach((log: LogEntry) => {
        const row = [
          log.timestamp,
          log.nivel,
          log.modulo,
          log.usuario,
          log.ip || 'N/A',
          `"${log.mensaje.replace(/"/g, '""')}"`
        ];
        csvRows.push(row.join(','));
      });

      const csvString = csvRows.join('\n');
      const fileName = `logs_auditoria_${new Date().toISOString().split('T')[0]}.csv`;

      return {
        success: true,
        csvData: csvString,
        fileName,
        recordCount: filteredLogs.length
      };
    } catch (error) {
      console.error('Error in exportCSV action:', error);
      return {
        success: false,
        message: 'Error al exportar logs'
      };
    }
  },

  clearLogs: async () => {
    // En producción: Llamar a API para limpiar logs antiguos
    // await fetch('http://api.luckia.cl/logs/clear', { method: 'POST' });

    return {
      success: true,
      message: 'Función no implementada en el backend aún',
      clearedCount: 0
    };
  }
};