FROM postgres:18

# Configuración de zona horaria (Importante para sistemas de Asistencia/RRHH)
ENV TZ="America/Santiago"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copiamos los scripts de inicialización al directorio mágico de Postgres
# Se ejecutan en orden alfabético, por eso usamos prefijos numéricos
COPY ./init-scripts/01-users.sql /docker-entrypoint-initdb.d/01-users.sql
COPY ./init-scripts/02-schema-stg.sql /docker-entrypoint-initdb.d/02-schema-stg.sql
COPY ./init-scripts/03-schema-dwh.sql /docker-entrypoint-initdb.d/03-schema-dwh.sql

# Puerto por defecto
EXPOSE 5432
