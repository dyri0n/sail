import { promises as fs } from 'fs';
import path from 'path';
import type { PageServerLoad } from './$types';

// Definimos las rutas base
const BASE_PATH = path.join(process.cwd(), 'uploads');
const PATHS = {
    no_leidos: path.join(BASE_PATH, 'no_leidos'), // Pendientes de ir a Staging
    leidos: path.join(BASE_PATH, 'leidos')        // Ya cargados en Staging
};

export const load: PageServerLoad = async () => {
    // Función auxiliar para leer una carpeta específica
    async function getFilesFromDir(dirPath: string, status: 'pending' | 'processed') {
        try {
            // Crear carpeta si no existe
            try { await fs.access(dirPath); } 
            catch { await fs.mkdir(dirPath, { recursive: true }); }

            const fileNames = await fs.readdir(dirPath);
            
            // Filtrar excels
            const excelFiles = fileNames.filter(f => /\.(xlsx|xls|csv)$/i.test(f));

            // Obtener stats
            return Promise.all(excelFiles.map(async (fileName) => {
                const filePath = path.join(dirPath, fileName);
                const stats = await fs.stat(filePath);
                
                return {
                    name: fileName,
                    path: filePath, // Opcional, por seguridad mejor no enviarlo al cliente
                    size: formatBytes(stats.size),
                    date: stats.mtime.toLocaleDateString('es-CL', { 
                        day: '2-digit', month: 'short', hour: '2-digit', minute:'2-digit'
                    }),
                    timestamp: stats.mtime.getTime(),
                    status: status // 'pending' = No leído, 'processed' = Leído
                };
            }));
        } catch (error) {
            console.error(`Error en carpeta ${status}:`, error);
            return [];
        }
    }

    // Ejecutamos ambas lecturas en paralelo
    const [pendingFiles, processedFiles] = await Promise.all([
        getFilesFromDir(PATHS.no_leidos, 'pending'),
        getFilesFromDir(PATHS.leidos, 'processed')
    ]);

    // Unimos y ordenamos por fecha (más reciente primero)
    const allFiles = [...pendingFiles, ...processedFiles].sort((a, b) => b.timestamp - a.timestamp);

    return { files: allFiles };
};

function formatBytes(bytes: number, decimals = 2) {
    if (!+bytes) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`;
}