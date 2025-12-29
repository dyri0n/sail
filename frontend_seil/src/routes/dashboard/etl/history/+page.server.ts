import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
    // Simulamos una base de datos más extensa
    const history = Array.from({ length: 20 }, (_, i) => ({
        id: 20 - i,
        fecha: `2025-10-${25 - Math.floor(i/2)} ${14 + (i%5)}:${30 + (i%10)}`,
        estado: i === 2 || i === 8 ? 'Fallido' : 'Exitoso',
        duracion: `${Math.floor(Math.random() * 3) + 1}m ${Math.floor(Math.random() * 59)}s`,
        registros: Math.floor(Math.random() * 500) + 100,
        usuario: i % 3 === 0 ? 'Sistema (Auto)' : 'jyampara',
        detalles: i === 2 ? 'Error de conexión SAP' : 'Carga completada OK'
    }));

    return {
        history,
        stats: {
            total: 154,
            tasaExito: '92%',
            promedioDuracion: '2m 10s'
        }
    };
};