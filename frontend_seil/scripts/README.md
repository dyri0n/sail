# Scripts del Frontend SAIL

Scripts de utilidad para gestionar el frontend de SAIL (SvelteKit).

## Prerrequisitos

- Node.js instalado (versión 18 o superior recomendada)
- npm instalado (viene con Node.js)

## Scripts disponibles

### setup-frontend.ps1
Configura el entorno del frontend por primera vez:
- Verifica que Node.js y npm estén instalados
- Crea el archivo `.env` desde `.env.example`
- Instala todas las dependencias npm
- Crea directorios necesarios (logs)

```powershell
.\setup-frontend.ps1
```

### start-frontend.ps1
Inicia el servidor de desarrollo de Vite:
- Verifica que las dependencias estén instaladas
- Inicia el servidor en segundo plano
- Guarda el PID del proceso
- La aplicación estará disponible en http://localhost:5173

```powershell
.\start-frontend.ps1
```

### stop-frontend.ps1
Detiene el servidor de desarrollo:
- Lee el PID del archivo guardado
- Detiene el proceso npm y sus hijos (node/vite)
- Limpia el archivo PID

```powershell
.\stop-frontend.ps1
```

## Uso típico

```powershell
# Primera vez (setup)
cd frontend_seil\scripts
.\setup-frontend.ps1

# Iniciar el frontend
.\start-frontend.ps1

# Detener el frontend
.\stop-frontend.ps1
```

## Logs

Los logs del servidor se guardan en `frontend_seil/logs/`:
- `frontend.log` - Salida estándar
- `frontend.error.log` - Errores

## Notas

- El servidor de desarrollo se ejecuta en el puerto **5173** por defecto
- Para cambiar la configuración del servidor, edita `vite.config.ts`
- El archivo `.env` contiene las variables de entorno (ej: `PUBLIC_API_BASE_URL`)
