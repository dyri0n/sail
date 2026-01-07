import { promises as fs } from 'fs';
import path from 'path';
import type { PageServerLoad } from './$types';

// Ruta al landing-zone (donde se depositan los archivos Excel para ETL)
const LANDING_ZONE_PATH = 'C:/Users/yampa/Trabajos/UTA/ici/p4/github/sail/landing-zone';

export const load: PageServerLoad = async () => {
    async function getFilesFromDir(dirPath: string, status: 'pending' | 'processed') {
        try {
            // Verificar que existe
            try { await fs.access(dirPath); }
            catch {
                console.error(`Directorio no existe: ${dirPath}`);
                return [];
            }

            const fileNames = await fs.readdir(dirPath);

            // Filtrar solo archivos Excel
            const excelFiles = fileNames.filter(f => /\.(xlsx|xls|csv)$/i.test(f));

            // Obtener stats de cada archivo
            return Promise.all(excelFiles.map(async (fileName) => {
                const filePath = path.join(dirPath, fileName);
                const stats = await fs.stat(filePath);

                return {
                    name: fileName,
                    path: filePath,
                    size: formatBytes(stats.size),
                    date: stats.mtime.toLocaleDateString('es-CL', {
                        day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
                    }),
                    timestamp: stats.mtime.getTime(),
                    status: status
                };
            }));
        } catch (error) {
            console.error(`Error leyendo landing-zone:`, error);
            return [];
        }
    }

    // Leer archivos del landing-zone (todos como "pending" por ahora)
    const files = await getFilesFromDir(LANDING_ZONE_PATH, 'pending');

    // Ordenar por fecha (más reciente primero)
    files.sort((a, b) => b.timestamp - a.timestamp);

    return {
        files,
        userRole: 'GERENCIA' // TODO: Get from locals when available
    };
};

function formatBytes(bytes: number, decimals = 2) {
    if (!+bytes) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`;
}