// +page.server.ts
import type { PageServerLoad } from './$types';

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

// Datos de ejemplo - En producción vendría de la API real
const logsEjemplo: LogEntry[] = [
  { id: '1', timestamp: '2025-10-18 15:39:23', nivel: 'INFO', modulo: 'AUTH', mensaje: 'Usuario juan.carlos inició sesión exitosamente', usuario: 'juan.carlos', ip: '192.168.1.100' },
  { id: '2', timestamp: '2025-10-18 15:40:12', nivel: 'SUCCESS', modulo: 'ETL', mensaje: 'Proceso ETL completado exitosamente', usuario: 'sistema', detalles: { registros_procesados: 1254, duracion: '2m 34s' }},
  { id: '3', timestamp: '2025-10-18 15:42:05', nivel: 'WARN', modulo: 'API', mensaje: 'Timeout en petición a endpoint /api/data', usuario: 'api-client', ip: '10.0.0.50' },
  { id: '4', timestamp: '2025-10-18 15:45:30', nivel: 'ERROR', modulo: 'DB', mensaje: 'Error de conexión a base de datos staging', usuario: 'sistema', detalles: { error_code: 'DB_CONN_001', intento: 3 }},
  { id: '5', timestamp: '2025-10-18 15:50:15', nivel: 'AUDIT', modulo: 'SECURITY', mensaje: 'Usuario admin.rrhh modificó permisos de usuario', usuario: 'admin.rrhh', ip: '192.168.1.101', detalles: { accion: 'UPDATE_ROLE', usuario_afectado: 'tomas.silva' }},
  { id: '6', timestamp: '2025-10-18 16:00:00', nivel: 'INFO', modulo: 'REPORT', mensaje: 'Reporte de rotación generado automáticamente', usuario: 'sistema' },
  { id: '7', timestamp: '2025-10-18 16:15:22', nivel: 'DEBUG', modulo: 'PREDICTION', mensaje: 'Modelo de predicción entrenado', usuario: 'ml-engine', detalles: { accuracy: 0.87, modelo: 'random_forest_v2' }},
  { id: '8', timestamp: '2025-10-18 16:30:45', nivel: 'AUDIT', modulo: 'SECURITY', mensaje: 'Intento de acceso fallido', usuario: 'desconocido', ip: '203.0.113.25', detalles: { intentos: 5, bloqueado: true }},
  { id: '9', timestamp: '2025-10-18 17:00:00', nivel: 'INFO', modulo: 'ETL', mensaje: 'Carga de datos Excel completada', usuario: 'operador.datos', ip: '192.168.1.150' },
  { id: '10', timestamp: '2025-10-18 17:30:00', nivel: 'SUCCESS', modulo: 'PREDICTION', mensaje: 'Predicción de rotación generada para 15 empleados', usuario: 'sistema' },
  { id: '11', timestamp: '2025-10-18 18:00:00', nivel: 'WARN', modulo: 'API', mensaje: 'Alta latencia en endpoint /api/predict', usuario: 'api-client', ip: '10.0.0.50' },
  { id: '12', timestamp: '2025-10-18 18:30:00', nivel: 'INFO', modulo: 'AUTH', mensaje: 'Usuario tomas.silva cerró sesión', usuario: 'tomas.silva', ip: '192.168.1.102' },
  { id: '13', timestamp: '2025-10-18 19:00:00', nivel: 'AUDIT', modulo: 'SECURITY', mensaje: 'Exportación de datos a CSV realizada', usuario: 'juan.carlos', ip: '192.168.1.100', detalles: { archivo: 'reporte_rotacion.csv', registros: 150 }},
  { id: '14', timestamp: '2025-10-18 20:00:00', nivel: 'ERROR', modulo: 'DB', mensaje: 'Error de integridad en tabla staging.empleados', usuario: 'sistema', detalles: { tabla: 'staging.empleados', error: 'DUPLICATE_KEY' }},
  { id: '15', timestamp: '2025-10-18 21:00:00', nivel: 'INFO', modulo: 'BACKUP', mensaje: 'Backup automático completado exitosamente', usuario: 'sistema' },
];

// Función para simular llamada a API
async function fetchLogsFromAPI(): Promise<LogEntry[]> {
  // En producción: const response = await fetch('http://api.luckia.cl/logs');
  // return await response.json();
  
  // Simulamos delay de API
  await new Promise(resolve => setTimeout(resolve, 100));
  return logsEjemplo;
}

// Función para calcular estadísticas
function calculateStats(logs: LogEntry[]): LogStats {
  return {
    total: logs.length,
    errores: logs.filter(l => l.nivel === 'ERROR').length,
    auditoria: logs.filter(l => l.nivel === 'AUDIT').length,
    ultimo: logs[0]?.timestamp || 'N/A'
  };
}

// Función para obtener valores únicos para filtros
function getFilterValues(logs: LogEntry[]) {
  const niveles = [...new Set(logs.map(log => log.nivel))];
  const modulos = [...new Set(logs.map(log => log.modulo))];
  const usuarios = [...new Set(logs.map(log => log.usuario))];
  
  return {
    niveles: ['todos', ...niveles],
    modulos: ['todos', ...modulos],
    usuarios: ['todos', ...usuarios]
  };
}

// Cargar datos para la página
export const load: PageServerLoad = async () => {
  const logs = await fetchLogsFromAPI();
  const stats = calculateStats(logs);
  const filters = getFilterValues(logs);
  
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
  exportCSV: async ({ request }) => {
    const formData = await request.formData();
    const filterData = Object.fromEntries(formData);
    
    // En producción: Llamar a API para exportar con filtros
    // const response = await fetch('http://api.luckia.cl/logs/export', {
    //   method: 'POST',
    //   body: JSON.stringify(filterData)
    // });
    
    // Simulamos generación de CSV
    const filteredLogs = logsEjemplo.filter(log => {
      if (filterData.nivel && filterData.nivel !== 'todos' && log.nivel !== filterData.nivel) return false;
      if (filterData.modulo && filterData.modulo !== 'todos' && log.modulo !== filterData.modulo) return false;
      if (filterData.usuario && filterData.usuario !== 'todos' && log.usuario !== filterData.usuario) return false;
      return true;
    });
    
    // Generar CSV
    const headers = ['Timestamp', 'Nivel', 'Módulo', 'Usuario', 'IP', 'Mensaje'];
    const csvRows = [];
    
    csvRows.push(headers.join(','));
    
    filteredLogs.forEach(log => {
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
    
    return {
      success: true,
      csvData: csvString,
      fileName: `logs_auditoria_${new Date().toISOString().split('T')[0]}.csv`,
      recordCount: filteredLogs.length
    };
  },
  
  clearLogs: async () => {
    // En producción: Llamar a API para limpiar logs antiguos
    // await fetch('http://api.luckia.cl/logs/clear', { method: 'POST' });
    
    return {
      success: true,
      message: 'Los logs antiguos han sido eliminados',
      clearedCount: logsEjemplo.length
    };
  }
};