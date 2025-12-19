FROM postgres:18

# Configuración de zona horaria (Chile)
ENV TZ="America/Santiago"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Script de inicialización del schema staging
COPY ./init-scripts/01-init_schema.sql /docker-entrypoint-initdb.d/01-init_schema.sql

# Puerto por defecto
EXPOSE 5432
