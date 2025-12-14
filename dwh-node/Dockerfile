FROM postgres:18

# Configuración de zona horaria (Importante para sistemas de Asistencia/RRHH)
ENV TZ="America/Santiago"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copiamos el script de inicialización al directorio mágico de Postgres
COPY ./init-scripts/init_dwh.sql /docker-entrypoint-initdb.d/10-init_schema.sql

# Puerto por defecto
EXPOSE 5432
