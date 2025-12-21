-- =============================================================================
-- 04-SEED-TEST-DATA.SQL - Datos de prueba para ambiente de testing
-- =============================================================================
-- Solo incluir en Dockerfile.testing, NO en producción.
-- =============================================================================

SET ROLE stg_admin;
SET search_path TO stg;

-- =============================================================================
-- 1. DATOS DE PRUEBA: stg_rotacion_empleados
-- =============================================================================
INSERT INTO stg_rotacion_empleados (
    id_personal, numero_personal_texto, id_sociedad, nombre_completo,
    nombre_empresa, area_personal, fecha_desde_area_personal, fecha_hasta_area_personal,
    unidad_organizativa, posicion, relacion_laboral, fecha_antiguedad_puesto,
    fecha_nacimiento, edad, pais_nacimiento, nacionalidad, estado_civil,
    numero_hijos, sexo, fecha_alta, fecha_baja, nombre_superior
)
VALUES 
    (1001, 'EMP-1001', 837, 'GONZÁLEZ PÉREZ, JUAN CARLOS',
     'EMPRESA PRINCIPAL S.A.', 'Tecnología', '2020-01-15', '9999-12-31',
     'Gerencia TI', 'Analista Senior', 'Indefinido', '2020-01-15',
     '1985-03-22', 39, 'Chile', 'Chilena', 'Casado',
     2, 'Masculino', '2020-01-15', NULL, 'MARTÍNEZ SILVA, ROBERTO'),
    
    (1002, 'EMP-1002', 837, 'RODRÍGUEZ SILVA, MARÍA FERNANDA',
     'EMPRESA PRINCIPAL S.A.', 'Recursos Humanos', '2019-06-01', '9999-12-31',
     'Gerencia RRHH', 'Jefe de Selección', 'Indefinido', '2019-06-01',
     '1990-07-14', 34, 'Chile', 'Chilena', 'Soltera',
     0, 'Femenino', '2019-06-01', NULL, 'LÓPEZ MUÑOZ, CAROLINA'),
    
    (1003, 'EMP-1003', 841, 'MUÑOZ CONTRERAS, PEDRO ANTONIO',
     'FILIAL SERVICIOS LTDA.', 'Operaciones', '2021-03-10', '9999-12-31',
     'Gerencia Operaciones', 'Supervisor', 'Indefinido', '2021-03-10',
     '1988-11-30', 36, 'Chile', 'Chilena', 'Casado',
     3, 'Masculino', '2021-03-10', NULL, 'SOTO VERA, ANDRÉS'),
    
    (1004, 'EMP-1004', 837, 'TORRES LAGOS, ANA MARÍA',
     'EMPRESA PRINCIPAL S.A.', 'Finanzas', '2018-02-20', '9999-12-31',
     'Gerencia Finanzas', 'Contador General', 'Indefinido', '2018-02-20',
     '1982-09-05', 42, 'Chile', 'Chilena', 'Casada',
     1, 'Femenino', '2018-02-20', NULL, 'VARGAS PINTO, CLAUDIO'),
    
    (1005, 'EMP-1005', 841, 'SILVA BRAVO, CARLOS EDUARDO',
     'FILIAL SERVICIOS LTDA.', 'Comercial', '2022-08-01', '2024-06-30',
     'Gerencia Comercial', 'Ejecutivo Ventas', 'Plazo Fijo', '2022-08-01',
     '1995-12-18', 29, 'Chile', 'Chilena', 'Soltero',
     0, 'Masculino', '2022-08-01', '2024-06-30', 'MORALES DÍAZ, PATRICIA');

-- =============================================================================
-- 2. DATOS DE PRUEBA: stg_capacitaciones_resumen
-- =============================================================================
INSERT INTO stg_capacitaciones_resumen (
    mes, titulo_capacitacion, modalidad, fecha_inicio, fecha_fin,
    area_tematica, tipo_formador, gerencia, formador_proveedor,
    asistentes, horas, horas_totales, coste_total_euros,
    valoracion_formador, indice_satisfaccion, nps
)
VALUES 
    ('Enero', 'Excel Avanzado para Análisis de Datos', 'Presencial',
     '2024-01-15', '2024-01-17', 'Ofimática', 'Externo', 'Gerencia TI',
     'Capacitaciones Chile SpA', 15, 24, 360, 2500.00, 4.5, 92.50, 75),
    
    ('Febrero', 'Liderazgo y Gestión de Equipos', 'Híbrido',
     '2024-02-05', '2024-02-07', 'Habilidades Blandas', 'Externo', 'Gerencia RRHH',
     'Leadership Academy', 12, 16, 192, 3200.00, 4.8, 95.00, 85),
    
    ('Marzo', 'Seguridad Industrial Nivel I', 'Presencial',
     '2024-03-10', '2024-03-12', 'Seguridad', 'Interno', 'Gerencia Operaciones',
     'Depto. Prevención', 25, 12, 300, 500.00, 4.2, 88.00, 60),
    
    ('Abril', 'Power BI Fundamentos', 'Online',
     '2024-04-01', '2024-04-05', 'Tecnología', 'Externo', 'Gerencia Finanzas',
     'Microsoft Partner', 20, 20, 400, 1800.00, 4.6, 90.00, 70);

-- =============================================================================
-- 3. DATOS DE PRUEBA: stg_capacitaciones_participantes
-- =============================================================================
INSERT INTO stg_capacitaciones_participantes (
    mes, rut, id_empleado, nombre, apellidos, correo, nombre_curso, total_horas_formacion
)
VALUES 
    ('Enero', '12345678-9', 1001, 'Juan Carlos', 'González Pérez', 
     'jgonzalez@empresa.cl', 'Excel Avanzado para Análisis de Datos', 24),
    ('Enero', '98765432-1', 1002, 'María Fernanda', 'Rodríguez Silva',
     'mrodriguez@empresa.cl', 'Excel Avanzado para Análisis de Datos', 24),
    ('Febrero', '98765432-1', 1002, 'María Fernanda', 'Rodríguez Silva',
     'mrodriguez@empresa.cl', 'Liderazgo y Gestión de Equipos', 16),
    ('Marzo', '55555555-5', 1003, 'Pedro Antonio', 'Muñoz Contreras',
     'pmunoz@filial.cl', 'Seguridad Industrial Nivel I', 12),
    ('Abril', '44444444-4', 1004, 'Ana María', 'Torres Lagos',
     'atorres@empresa.cl', 'Power BI Fundamentos', 20);

-- =============================================================================
-- 4. DATOS DE PRUEBA: stg_proceso_seleccion
-- =============================================================================
INSERT INTO stg_proceso_seleccion (
    id_control_interno, fecha_cierre_proceso, situacion, motivo,
    publicado_portal_interno, duracion_dias_total, fuente_reclutamiento,
    coste_proceso, n_cv_recibidos, n_personas_entrevistadas_telefono,
    n_personas_entrevistadas_presencial, n_personas_finalistas,
    puesto, gerencia, persona, sexo, edad, formacion,
    anos_experiencia, activo, continuidad_mas_4_meses
)
VALUES 
    (2024001, '2024-02-15', 'Cerrado - Contratado', 'Reemplazo',
     TRUE, 30, 'Portal Empleo', 1500.00, 45, 12, 5, 2,
     'Analista de Datos', 'Gerencia TI', 'Juan Pérez', 'Masculino', 28,
     'Ingeniería Civil Informática', 3, TRUE, TRUE),
    
    (2024002, '2024-03-20', 'Cerrado - Contratado', 'Nuevo cargo',
     TRUE, 45, 'LinkedIn', 2200.00, 60, 15, 8, 3,
     'Jefe de Proyectos', 'Gerencia Operaciones', 'Ana López', 'Femenino', 35,
     'Ingeniería Industrial', 8, TRUE, TRUE),
    
    (2024003, '2024-04-10', 'Cerrado - Desierto', 'Expansión',
     FALSE, 60, 'Headhunter', 5000.00, 20, 8, 4, 1,
     'Gerente Comercial', 'Gerencia Comercial', NULL, NULL, NULL,
     NULL, NULL, FALSE, FALSE),
    
    (2024004, NULL, 'En Proceso', 'Reemplazo',
     TRUE, NULL, 'Referidos', 0.00, 15, 5, 0, 0,
     'Asistente Contable', 'Gerencia Finanzas', NULL, NULL, NULL,
     'Contador Auditor', 2, FALSE, FALSE);

-- =============================================================================
-- 5. DATOS DE PRUEBA: stg_perfiles_trabajo
-- =============================================================================
INSERT INTO stg_perfiles_trabajo (
    puesto, categoria, nombre_empleado, fecha, principal_mision,
    responsabilidades, competencias
)
VALUES 
    ('Analista Senior', 'Profesional', 'Juan Carlos González Pérez', '2024-01-15',
     'Analizar datos y generar reportes para la toma de decisiones',
     'Desarrollo de dashboards, ETL, análisis predictivo',
     'SQL, Python, Power BI, pensamiento analítico'),
    
    ('Jefe de Selección', 'Jefatura', 'María Fernanda Rodríguez Silva', '2024-01-15',
     'Liderar los procesos de reclutamiento y selección de personal',
     'Gestión de vacantes, entrevistas, onboarding',
     'Entrevistas por competencias, ATS, liderazgo');

-- Restaurar rol
RESET ROLE;
