INSERT INTO dwh.dim_empresa (codigo, nombre)
VALUES
    (837, 'Sidesa'),
    (841, 'Luckia Arica')

ON CONFLICT (codigo)
DO UPDATE SET
    nombre = EXCLUDED.nombre;
    -- Esto permite que si un día cambias 'Sidesa' 
    -- por 'Sidesa SPA', se actualice solo.
