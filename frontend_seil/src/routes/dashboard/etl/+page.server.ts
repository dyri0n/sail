export async function load() {
    return {
        historial: [
            { id: 1, fecha: '2023-10-25 14:30', estado: 'Exitoso', duracion: '2m 15s' },
            { id: 2, fecha: '2023-10-24 09:15', estado: 'Fallido', duracion: '45s' },
            { id: 3, fecha: '2023-10-23 18:00', estado: 'Exitoso', duracion: '2m 10s' },
            { id: 4, fecha: '2023-10-22 10:00', estado: 'Exitoso', duracion: '2m 20s' },
            { id: 5, fecha: '2023-10-21 15:45', estado: 'Exitoso', duracion: '2m 12s' },
        ],
        logs: [
            { timestamp: '14:30:01', nivel: 'INFO', mensaje: 'Iniciando proceso ETL...' },
            { timestamp: '14:30:05', nivel: 'INFO', mensaje: 'Conexión a base de datos establecida.' },
            { timestamp: '14:30:15', nivel: 'WARN', mensaje: 'Transformación lenta en tabla de usuarios.' },
            { timestamp: '14:31:00', nivel: 'INFO', mensaje: 'Carga de datos completada.' },
            { timestamp: '14:32:15', nivel: 'SUCCESS', mensaje: 'Proceso finalizado correctamente.' },
        ]
    };
}