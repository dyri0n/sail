-- Eliminar tablas si ya existen (para poder re-ejecutar el script)
DROP TABLE IF EXISTS stg_rotacion_empleados;
DROP TABLE IF EXISTS stg_asistencia_diaria;
DROP TABLE IF EXISTS stg_asistencia_semanal;
DROP TABLE IF EXISTS stg_capacitaciones_resumen;
DROP TABLE IF EXISTS stg_capacitaciones_participantes;
DROP TABLE IF EXISTS stg_perfiles_trabajo;
DROP TABLE IF EXISTS stg_procesos_seleccion;



-- Creamos la tabla de staging para la rotación de empleados
CREATE TABLE stg_rotacion_empleados (
    -- Detalles del empleado (Identificación)
    id_personal INTEGER PRIMARY KEY,
    numero_personal_texto VARCHAR(100),
    id_sociedad INTEGER,
    nombre_completo VARCHAR(255),
    nombre_empresa VARCHAR(255),
    area_personal VARCHAR(255),
    fecha_desde_area_personal DATE,
    fecha_hasta_area_personal DATE,

    -- Detalles de Organización
    unidad_organizativa VARCHAR(255),
    posicion VARCHAR(255),
    relacion_laboral VARCHAR(100),
    fecha_antiguedad_puesto DATE,
    denominacion_cargo_duplicada VARCHAR(255), -- Posible duplicado de 'posicion'

    -- Detalles del empleado (Personales)
    fecha_nacimiento DATE,
    edad INTEGER CHECK (edad > 0),
    pais_nacimiento VARCHAR(100),
    lugar_nacimiento VARCHAR(100),
    nacionalidad VARCHAR(100),
    estado_civil VARCHAR(50),
    numero_hijos INTEGER CHECK (numero_hijos >= 0),
    sexo VARCHAR(20),

    -- Detalles Cargos (Historial de cargos)
    fecha_desde_cargo DATE,
    fecha_hasta_cargo DATE,
    clase_fecha VARCHAR(100),
    fecha_generica DATE,

    -- Detalles Rotación y otros
    clase_prestamo VARCHAR(100),
    movilidad_geografica VARCHAR(100),
    experiencia_profesional TEXT,
    fecha_inicio_exp DATE,
    modificacion_exp VARCHAR(100),
    fecha_hasta_exp DATE,
    denominacion_clase_me VARCHAR(255),
    denominacion_motivo_med VARCHAR(255),
    fecha_alta DATE,
    fecha_baja DATE,
    nombre_superior VARCHAR(255)
);

-- Agregamos los comentarios a las columnas para usarlos como diccionario de datos

COMMENT ON COLUMN stg_rotacion_empleados.id_personal IS 'ID Numérico entero (Nº pers.).';
COMMENT ON COLUMN stg_rotacion_empleados.numero_personal_texto IS 'Número de personal (campo de texto).';
COMMENT ON COLUMN stg_rotacion_empleados.id_sociedad IS 'ID de la sociedad (ej. 837).';
COMMENT ON COLUMN stg_rotacion_empleados.nombre_completo IS 'APELLIDOS, NOMBRES (todo en mayúsculas).';
COMMENT ON COLUMN stg_rotacion_empleados.nombre_empresa IS 'Nombre de la empresa (razón social completa).';
COMMENT ON COLUMN stg_rotacion_empleados.area_personal IS 'Denom.área personal.';
COMMENT ON COLUMN stg_rotacion_empleados.fecha_desde_area_personal IS 'Fecha "Desde" asociada al área personal.';
COMMENT ON COLUMN stg_rotacion_empleados.fecha_hasta_area_personal IS 'Fecha "Hasta" asociada al área personal.';
COMMENT ON COLUMN stg_rotacion_empleados.unidad_organizativa IS 'Denominación de unidad organiz.';
COMMENT ON COLUMN stg_rotacion_empleados.posicion IS 'Denominación de posiciones (Cargo).';
COMMENT ON COLUMN stg_rotacion_empleados.relacion_laboral IS 'Relación laboral.';
COMMENT ON COLUMN stg_rotacion_empleados.fecha_antiguedad_puesto IS 'Fecha de antigüedad en el puesto (Ant_puesto).';
COMMENT ON COLUMN stg_rotacion_empleados.denominacion_cargo_duplicada IS 'Campo "Denominación" (parece duplicado de "posicion").';
COMMENT ON COLUMN stg_rotacion_empleados.fecha_nacimiento IS 'Fecha de nacimiento (Fe.nacim.).';
COMMENT ON COLUMN stg_rotacion_empleados.edad IS 'Edad del empleado.';
COMMENT ON COLUMN stg_rotacion_empleados.pais_nacimiento IS 'País de nacimiento.';
COMMENT ON COLUMN stg_rotacion_empleados.lugar_nacimiento IS 'Lugar de nacimiento.';
COMMENT ON COLUMN stg_rotacion_empleados.nacionalidad IS 'Nacionalidad.';
COMMENT ON COLUMN stg_rotacion_empleados.estado_civil IS 'Clave para el estado civil.';
COMMENT ON COLUMN stg_rotacion_empleados.numero_hijos IS 'Nº de hijos.';
COMMENT ON COLUMN stg_rotacion_empleados.sexo IS 'Texto sexo.';
COMMENT ON COLUMN stg_rotacion_empleados.fecha_desde_cargo IS 'Fecha "Desde" asociada a Detalles Cargos.';
COMMENT ON COLUMN stg_rotacion_empleados.fecha_hasta_cargo IS 'Fecha "Hasta" asociada a Detalles Cargos.';
COMMENT ON COLUMN stg_rotacion_empleados.clase_fecha IS 'Clase de fecha.';
COMMENT ON COLUMN stg_rotacion_empleados.fecha_generica IS 'Campo genérico "Fecha".';
COMMENT ON COLUMN stg_rotacion_empleados.clase_prestamo IS 'Clase de préstamo.';
COMMENT ON COLUMN stg_rotacion_empleados.movilidad_geografica IS 'Movilidad geográfica.';
COMMENT ON COLUMN stg_rotacion_empleados.experiencia_profesional IS 'Experiencia Profesional.';
COMMENT ON COLUMN stg_rotacion_empleados.fecha_inicio_exp IS 'Fecha "Inicio" de la experiencia profesional.';
COMMENT ON COLUMN stg_rotacion_empleados.modificacion_exp IS 'Campo "Modificación" de la experiencia profesional.';
COMMENT ON COLUMN stg_rotacion_empleados.fecha_hasta_exp IS 'Fecha "Hasta" de la experiencia profesional.';
COMMENT ON COLUMN stg_rotacion_empleados.denominacion_clase_me IS 'Denominación de la clase de me.';
COMMENT ON COLUMN stg_rotacion_empleados.denominacion_motivo_med IS 'Denominación del motivo de med.';
COMMENT ON COLUMN stg_rotacion_empleados.fecha_alta IS 'Fecha de Alta (contratación).';
COMMENT ON COLUMN stg_rotacion_empleados.fecha_baja IS 'Fecha de Baja (desvinculación).';
COMMENT ON COLUMN stg_rotacion_empleados.nombre_superior IS 'Nombre del superior (GO).';

-- Resumen anual de capacitaciones
CREATE TABLE stg_capacitaciones_resumen (
    -- Columna para el ID único, se auto-incrementa
    id_capacitacion SERIAL PRIMARY KEY,
    
    -- Detalles de la capacitación
    mes VARCHAR(20) NOT NULL,
    titulo_capacitacion VARCHAR(255) NOT NULL,
    modalidad VARCHAR(100),            -- Reemplaza el ENUM
    fecha_inicio DATE,
    fecha_fin DATE,
    area_tematica VARCHAR(100),        -- Reemplaza el ENUM
    tipo_formador VARCHAR(100),        -- Reemplaza el ENUM
    gerencia VARCHAR(50),
    formador_proveedor VARCHAR(255),
    
    -- Métricas de la capacitación
    asistentes INTEGER CHECK (asistentes > 0),
    horas INTEGER CHECK (horas > 0),
    horas_totales INTEGER,
    coste_total_euros NUMERIC(10, 2) CHECK (coste_total_euros >= 0),
    
    -- Métricas de evaluación
    valoracion_formador NUMERIC(3, 1) CHECK (valoracion_formador >= 1 AND valoracion_formador <= 5),
    indice_satisfaccion NUMERIC(5, 2) CHECK (indice_satisfaccion >= 0 AND indice_satisfaccion <= 100),
    nps INTEGER CHECK (nps >= -100 AND nps <= 100)
);

-- Agregamos los comentarios a las columnas para usarlos como diccionario de datos

COMMENT ON COLUMN stg_capacitaciones_resumen.id_capacitacion IS 'Identificador numérico único del registro de capacitación.';
COMMENT ON COLUMN stg_capacitaciones_resumen.mes IS 'Mes en que se reporta la capacitación.';
COMMENT ON COLUMN stg_capacitaciones_resumen.titulo_capacitacion IS 'Nombre oficial del curso o programa.';
COMMENT ON COLUMN stg_capacitaciones_resumen.modalidad IS 'Modalidad de la capacitación (ej. PRESENCIAL, ONLINE).';
COMMENT ON COLUMN stg_capacitaciones_resumen.fecha_inicio IS 'Fecha de inicio del curso.';
COMMENT ON COLUMN stg_capacitaciones_resumen.fecha_fin IS 'Fecha de finalización del curso.';
COMMENT ON COLUMN stg_capacitaciones_resumen.area_tematica IS 'Categoría principal a la que pertenece el curso (ej. NEGOCIO, CLIENTE).';
COMMENT ON COLUMN stg_capacitaciones_resumen.tipo_formador IS 'Indica si el formador es de la empresa o externo (ej. INTERNO, EXTERNO).';
COMMENT ON COLUMN stg_capacitaciones_resumen.gerencia IS 'Gerencia que organiza o recibe la capacitación.';
COMMENT ON COLUMN stg_capacitaciones_resumen.formador_proveedor IS 'Nombre de la persona o entidad que imparte el curso.';
COMMENT ON COLUMN stg_capacitaciones_resumen.asistentes IS 'Número de participantes en el curso.';
COMMENT ON COLUMN stg_capacitaciones_resumen.horas IS 'Duración en horas del curso por persona.';
COMMENT ON COLUMN stg_capacitaciones_resumen.horas_totales IS 'Horas multiplicadas por el número de asistentes.';
COMMENT ON COLUMN stg_capacitaciones_resumen.coste_total_euros IS 'Costo total del curso en Euros.';
COMMENT ON COLUMN stg_capacitaciones_resumen.valoracion_formador IS 'Calificación (ej. 1-5) del formador.';
COMMENT ON COLUMN stg_capacitaciones_resumen.indice_satisfaccion IS 'Porcentaje de satisfacción de los asistentes.';
COMMENT ON COLUMN stg_capacitaciones_resumen.nps IS 'Net Promoter Score de la capacitación.';


-- Tabla de 
-- Creamos la tabla para los participantes de las capacitaciones
-- Esta tabla contiene la información de cada empleado que asiste a un curso.

CREATE TABLE stg_capacitaciones_participantes (
    -- "N°": Identificador único del registro de asistencia
    id_asistencia SERIAL PRIMARY KEY,
    
    -- "MES": Mes en que se realizó el curso
    mes VARCHAR(20),
    
    -- "Rut": RUT único del participante
    rut VARCHAR(12) NOT NULL UNIQUE,
    
    -- "NºEMPLEADO": ID del empleado (SAP)
    id_empleado INTEGER,
    
    -- "NOMBRE": Nombres del participante
    nombre VARCHAR(255),
    
    -- "APELLIDOS": Apellidos del participante
    apellidos VARCHAR(255),
    
    -- "CORREO": Email corporativo único del participante
    correo VARCHAR(255) UNIQUE,
    
    -- "NOMBRE CURSO": Nombre del curso al que asistió
    -- Este campo se usará para relacionar con la tabla 'capacitaciones'
    nombre_curso VARCHAR(255) NOT NULL,
    
    -- "TOTAL HRS FORMACION": Total de horas de formación
    total_horas_formacion INTEGER
);

-- Agregamos los comentarios a las columnas para usarlos como diccionario de datos

COMMENT ON COLUMN stg_capacitaciones_participantes.id_asistencia IS 'Identificador numérico único del registro de participante (N°).';
COMMENT ON COLUMN stg_capacitaciones_participantes.mes IS 'Mes en que se realizó el curso.';
COMMENT ON COLUMN stg_capacitaciones_participantes.rut IS 'RUT del participante (Formato XXXXXXXX-X).';
COMMENT ON COLUMN stg_capacitaciones_participantes.id_empleado IS 'ID del empleado (probablemente coincide con ID SAP).';
COMMENT ON COLUMN stg_capacitaciones_participantes.nombre IS 'Nombres del participante.';
COMMENT ON COLUMN stg_capacitaciones_participantes.apellidos IS 'Apellidos del participante.';
COMMENT ON COLUMN stg_capacitaciones_participantes.correo IS 'Email corporativo del participante.';
COMMENT ON COLUMN stg_capacitaciones_participantes.nombre_curso IS 'Nombre del curso al que asistió. Se usa para la relación.';
COMMENT ON COLUMN stg_capacitaciones_participantes.total_horas_formacion IS 'Total de horas de formación recibidas por el participante.';


-- 8. Tabla de Perfiles de Trabajo (DFT) (Págs. 11-16) [cite: 98, 124, 125]
-- Esta tabla es casi todo TEXTO libre, es para almacenar los documentos WORD
CREATE TABLE stg_perfiles_trabajo (
    id SERIAL PRIMARY KEY,
    puesto TEXT,                              -- [cite: 124]
    categoria TEXT,                           -- [cite: 124]
    nombre_empleado TEXT,                     -- [cite: 124]
    fecha DATE,                        -- [cite: 124]
    linea_ascendente TEXT,                    -- 
    linea_descendente TEXT,                   --
    principal_mision TEXT,                    -- [cite: 124]
    responsabilidades TEXT,                   -- [cite: 124]
    informa_y_reporta TEXT,                   -- [cite: 125]
    tareas_semanales TEXT,                    -- [cite: 125, 158]
    tareas_mensuales TEXT,                    -- [cite: 125]
    tareas_trimestrales TEXT,                 -- [cite: 125]
    tareas_semestrales TEXT,                  -- [cite: 125]
    tareas_anuales TEXT,                      -- [cite: 125]
    otras_tareas TEXT,                        -- [cite: 125]
    competencias TEXT,                        -- [cite: 125]
    habilidades_generales TEXT,               -- [cite: 125]
    habilidades_cognitivos TEXT,              -- [cite: 125]
    habilidades_fisicos TEXT,                 -- [cite: 125]
    habilidades_sensoriales TEXT,             -- [cite: 125]
    condiciones_trabajo TEXT,                 -- [cite: 125]
    apartado_legal TEXT                       -- [firma]
);

-- Creamos la tabla para el proceso de selección de personal
CREATE TABLE stg_proceso_seleccion (
    -- "CONTROL INTERNO": ID del proceso de selección
    id_control_interno INTEGER PRIMARY KEY,
    
    -- Detalles del proceso de selección
    fecha_cierre_proceso DATE,
    situacion TEXT,
    motivo VARCHAR(255),
    detalle_motivo TEXT,
    publicado_portal_interno BOOLEAN,
    fecha_envio_responsable DATE,
    fecha_entrevista_responsable DATE,
    duracion_entrevista_gerente NUMERIC(10, 2), -- Horas o minutos (ej. 1.5 horas)
    duracion_dias_total INTEGER CHECK (duracion_dias_total >= 0),
    fuente_reclutamiento VARCHAR(255),
    detalle_fuente TEXT,
    observaciones TEXT,
    coste_proceso NUMERIC(12, 2) CHECK (coste_proceso >= 0),
    n_cv_recibidos INTEGER CHECK (n_cv_recibidos >= 0),
    n_personas_entrevistadas_telefono INTEGER CHECK (n_personas_entrevistadas_telefono >= 0),
    n_personas_entrevistadas_presencial INTEGER CHECK (n_personas_entrevistadas_presencial >= 0),
    n_personas_finalistas INTEGER CHECK (n_personas_finalistas >= 0),

    -- Detalles del Puesto de trabajo
    puesto VARCHAR(255),
    centro_area VARCHAR(255),
    detalle_puesto VARCHAR(255),
    gerencia VARCHAR(100),
    linea_negocio VARCHAR(100),
    grupo VARCHAR(10), -- Para valores como 'G6'

    -- Detalles del empleado/candidato seleccionado
    persona VARCHAR(255),
    sexo VARCHAR(20),
    edad INTEGER CHECK (edad > 0),
    formacion VARCHAR(255),
    anos_experiencia INTEGER CHECK (anos_experiencia >= 0),
    sector_procedencia VARCHAR(255),
    activo BOOLEAN,
    continuidad_mas_4_meses BOOLEAN,
    origen VARCHAR(100),
    
    -- Campos ambiguos
    total_ambiguo INTEGER -- Columna "TOTAL" descrita como "AMBIGUO"
);

-- Agregamos los comentarios a las columnas para usarlos como diccionario de datos

COMMENT ON COLUMN stg_proceso_seleccion.id_control_interno IS 'ID del proceso de selección (CONTROL INTERNO).';
COMMENT ON COLUMN stg_proceso_seleccion.fecha_cierre_proceso IS 'Fecha de cierre (serial de Excel).';
COMMENT ON COLUMN stg_proceso_seleccion.situacion IS 'Estado o descripción actual del proceso.';
COMMENT ON COLUMN stg_proceso_seleccion.motivo IS 'Causa de la vacante (ej. Despido (sustitución)).';
COMMENT ON COLUMN stg_proceso_seleccion.detalle_motivo IS 'Explicación del motivo de la vacante.';
COMMENT ON COLUMN stg_proceso_seleccion.publicado_portal_interno IS 'Indica si se publicó internamente (N/D se almacena como NULL).';
COMMENT ON COLUMN stg_proceso_seleccion.fecha_envio_responsable IS 'Fecha de envío (serial de Excel).';
COMMENT ON COLUMN stg_proceso_seleccion.fecha_entrevista_responsable IS 'Fecha de entrevista (serial de Excel).';
COMMENT ON COLUMN stg_proceso_seleccion.duracion_entrevista_gerente IS 'Duración en horas o días de la entrevista.';
COMMENT ON COLUMN stg_proceso_seleccion.duracion_dias_total IS 'Días totales que tomó el proceso.';
COMMENT ON COLUMN stg_proceso_seleccion.fuente_reclutamiento IS 'Canal por el que se obtuvo al candidato.';
COMMENT ON COLUMN stg_proceso_seleccion.detalle_fuente IS 'Detalle de la fuente de reclutamiento.';
COMMENT ON COLUMN stg_proceso_seleccion.observaciones IS 'Comentarios adicionales sobre el proceso.';
COMMENT ON COLUMN stg_proceso_seleccion.coste_proceso IS 'Costo total del proceso de selección en Euros.';
COMMENT ON COLUMN stg_proceso_seleccion.n_cv_recibidos IS 'Número de currículums recibidos.';
COMMENT ON COLUMN stg_proceso_seleccion.n_personas_entrevistadas_telefono IS 'Número de entrevistas telefónicas.';
COMMENT ON COLUMN stg_proceso_seleccion.n_personas_entrevistadas_presencial IS 'Número de entrevistas presenciales.';
COMMENT ON COLUMN stg_proceso_seleccion.n_personas_finalistas IS 'Número de finalistas en el proceso.';
COMMENT ON COLUMN stg_proceso_seleccion.puesto IS 'Nombre del cargo a cubrir.';
COMMENT ON COLUMN stg_proceso_seleccion.centro_area IS 'Área o centro de costo solicitante.';
COMMENT ON COLUMN stg_proceso_seleccion.detalle_puesto IS 'Descripción o nombre detallado del puesto.';
COMMENT ON COLUMN stg_proceso_seleccion.gerencia IS 'Gerencia solicitante.';
COMMENT ON COLUMN stg_proceso_seleccion.linea_negocio IS 'Unidad de negocio.';
COMMENT ON COLUMN stg_proceso_seleccion.grupo IS 'Clasificación o grupo salarial del puesto (ej. G6).';
COMMENT ON COLUMN stg_proceso_seleccion.persona IS 'Nombre del candidato seleccionado o finalista.';
COMMENT ON COLUMN stg_proceso_seleccion.sexo IS 'Sexo del candidato.';
COMMENT ON COLUMN stg_proceso_seleccion.edad IS 'Edad del candidato.';
COMMENT ON COLUMN stg_proceso_seleccion.formacion IS 'Nivel educacional del candidato.';
COMMENT ON COLUMN stg_proceso_seleccion.anos_experiencia IS 'Años de experiencia laboral del candidato.';
COMMENT ON COLUMN stg_proceso_seleccion.sector_procedencia IS 'Industria o sector del que proviene el candidato.';
COMMENT ON COLUMN stg_proceso_seleccion.activo IS 'Indica si el candidato está activo (si/no).';
COMMENT ON COLUMN stg_proceso_seleccion.continuidad_mas_4_meses IS 'Indica si el candidato continuó más de 4 meses.';
COMMENT ON COLUMN stg_proceso_seleccion.origen IS 'Origen geográfico del candidato.';
COMMENT ON COLUMN stg_proceso_seleccion.total_ambiguo IS 'Campo "TOTAL" descrito como AMBIGUO.';