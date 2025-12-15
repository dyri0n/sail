INSERT INTO dwh.dim_empresa (id_empresa_sk, codigo_empresa_bk, nombre_empresa)
VALUES
    (1, 837, 'Sidesa'),
    (2, 841, 'Luckia Arica')

ON CONFLICT (codigo_empresa_bk)
DO UPDATE SET
    nombre_empresa = EXCLUDED.nombre_empresa;
    -- Esto permite que si un día cambias 'Sidesa' por 'Sidesa SPA', se actualice solo.
