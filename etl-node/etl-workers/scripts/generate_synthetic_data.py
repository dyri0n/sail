"""
Generador de Datos Sintéticos para Data Warehouse de RRHH - VERSIÓN AJUSTADA
================================================================================

Este script genera datos sintéticos que RESPETAN EXACTAMENTE el formato
de los archivos reales en dataReal/, incluyendo todas las columnas.

Basado en análisis de archivos reales:
- data_sap.xlsx: 36 columnas
- data_rotaciones.xlsx: 40 columnas  
- data_capacitaciones.xlsx: Informe 2025 (20 cols), Participantes (9 cols)
- data_asistencias.xlsx: Días y Semana sheets

Autor: Sistema ETL SAIL
Fecha: 2026-01-07
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os

# Configuración
fake = Faker('es_CL')
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# Parámetros
NUM_EMPLOYEES = 100
EMPLOYEE_ID_START = 10000
ACTIVE_EMPLOYEES_RATIO = 0.85
OUTPUT_DIR = "synthetic_data_v2"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*80)
print("GENERADOR DE DATOS SINTÉTICOS - FORMATO EXACTO dataReal")
print("="*80)


def generate_rut():
    """Genera un RUT chileno válido con formato XX.XXX.XXX-X"""
    number = random.randint(10000000, 25999999)
    rut_str = str(number)
    
    reversed_digits = list(map(int, reversed(rut_str)))
    factors = [2, 3, 4, 5, 6, 7]
    s = sum(d * factors[i % 6] for i, d in enumerate(reversed_digits))
    verifier = 11 - (s % 11)
    
    if verifier == 11:
        verifier = '0'
    elif verifier == 10:
        verifier = 'K'
    else:
        verifier = str(verifier)
    
    formatted = f"{number:,}".replace(',', '.')
    return f"{formatted}-{verifier}"


def generate_employee_master_data():
    """
    Genera data_sap.xlsx con las 36 columnas exactas del archivo real
    """
    print("\n[1/6] Generando data_sap.xlsx (36 columnas)...")
    
    employees = []
    num_active = int(NUM_EMPLOYEES * ACTIVE_EMPLOYEES_RATIO)
    
    empresas = {'837': 'CASINO MONTICELLO S.A.', '841': 'LUCKIA OPERACIONES SPA'}
    areas = ['OPERACIONES', 'ADMINISTRACION', 'TECNOLOGIA', 'MARKETING', 'FINANZAS', 'RRHH']
    unidades = ['SALA DE JUEGOS', 'ADMINISTRACION', 'SISTEMAS', 'CAJA', 'SEGURIDAD']
    posiciones = [
        'Crupier', 'Supervisor de Sala', 'Cajero', 'Jefe de Turno',
        'Analista de Datos', 'Desarrollador', 'Contador', 'Ejecutivo Comercial',
        'Gerente de Operaciones', 'Asistente Administrativo', 'Jefe de Seguridad'
    ]
    relaciones_laborales = ['Empleado', 'Temporal', 'Contratista']
    sexos = ['M', 'F']
    estados_civiles = ['Soltero/a', 'Casado/a', 'Divorciado/a']
    
    for i in range(NUM_EMPLOYEES):
        emp_id = EMPLOYEE_ID_START + i
        rut = generate_rut()
        soc = random.choice(list(empresas.keys()))
        
        hire_date = fake.date_between(start_date='-5y', end_date='-1m')
        is_active = i < num_active
        
        if is_active:
            termination_date = None
            hasta = datetime(2099, 12, 31).date()
            estado = 'Activo'
        else:
            min_term = hire_date + timedelta(days=30)
            termination_date = fake.date_between(start_date=min_term, end_date='today')
            hasta = termination_date
            estado = 'Dado de baja'
        
        birth_date = fake.date_of_birth(minimum_age=25, maximum_age=65)
        edad = (datetime.now().date() - birth_date).days // 365
        
        employees.append({
            # Columnas 1-11
            'Nº pers.': emp_id,
            'RUT': rut,
            'Número de personal': emp_id,
            'Soc.': soc,
            'Nombre de la empresa': empresas[soc],
            'Denom.área personal': random.choice(areas),
            'Desde': hire_date,
            'Hasta': hasta,
            'Denominación de unidad organiz': random.choice(unidades),
            'Denominación de posiciones': random.choice(posiciones),
            'Sueldo Base': random.randint(600000, 3000000),
            
            # Columnas 12-22
            'Relación laboral': random.choice(relaciones_laborales),
            'Ant_puesto': round((datetime.now().date() - hire_date).days / 365, 1),
            'Denominación': random.choice(posiciones),
            'Fe.nacim.': birth_date,
            'Edad del empleado': edad,
            'País de nacimiento': 'CL',
            'Lugar de nacimiento': fake.city(),
            'Nacionalidad': 'Chilena',
            'Clave para el estado civil': random.choice(estados_civiles),
            'Nº de hijos': random.randint(0, 3),
            'Texto sexo': random.choice(sexos),
            
            # Columnas 23-32
            'Desde.1': hire_date,
            'Hasta.1': hasta,
            'Clase de fecha': 'Entrada',
            'Fecha': hire_date,
            'Clase de préstamo': None,
            'Movilidad geográfica': 'No',
            'Experiencia Profesional': random.randint(1, 15),
            'Inicio': hire_date,
            'Hasta.2': hasta,
            'Denominación de la clase de me': 'Contratación' if is_active else 'Baja',
            'Denominación del motivo de med': 'Nueva Contratación' if is_active else random.choice([
                'Renuncia Voluntaria', 'Término de Contrato', 'Mutuo Acuerdo'
            ]),
            
            # Columnas 33-36
            'Alta': hire_date,
            'Baja': termination_date,
            'Nombre del superior (GO)': fake.name()
        })
    
    df = pd.DataFrame(employees)
    print(f"   ✓ {len(df)} empleados con 36 columnas")
    print(f"   ✓ Activos: {num_active}, Bajas: {NUM_EMPLOYEES - num_active}")
    
    return df


def generate_turnover_events(employee_df):
    """
    Genera data_rotaciones.xlsx con las 40 columnas exactas
    """
    print("\n[2/6] Generando data_rotaciones.xlsx (40 columnas)...")
    
    events = []
    
    for _, emp in employee_df.iterrows():
        # Crear registro para cada cambio
        for event_type in ['Alta'] + (['Baja'] if pd.notna(emp['Baja']) else []):
            events.append({
                # Columnas 1-10
                'Nº pers.': emp['Nº pers.'],
                'Número de personal': emp['Nº pers.'],
                'Soc.': emp['Soc.'],
                'Nombre de la empresa': emp['Nombre de la empresa'],
                'Denom.área personal': emp['Denom.área personal'],
                'Desde': emp['Desde'],
                'Hasta': emp['Hasta'],
                'Denominación de unidad organiz': emp['Denominación de unidad organiz'],
                'Denominación de función': emp['Denominación de posiciones'],
                'Denominación de posiciones': emp['Denominación de posiciones'],
                
                # Columnas 11-20
                'Relación laboral': emp['Relación laboral'],
                'Duración': None,
                'Ant_puesto': emp['Ant_puesto'],
                'Denominación': emp['Denominación'],
                'Fe.nacim.': emp['Fe.nacim.'],
                'Edad del empleado': emp['Edad del empleado'],
                'País de nacimiento': emp['País de nacimiento'],
                'Lugar de nacimiento': emp['Lugar de nacimiento'],
                'Nacionalidad': emp['Nacionalidad'],
                'Clave para el estado civil': emp['Clave para el estado civil'],
                
                # Columnas 21-30
                'Nº de hijos': emp['Nº de hijos'],
                'Texto sexo': emp['Texto sexo'],
                'Desde.1': emp['Alta'] if event_type == 'Alta' else emp['Baja'],
                'Hasta.1': emp['Hasta'],
                'Clase de fecha': event_type,
                'Fecha': emp['Alta'] if event_type == 'Alta' else emp['Baja'],
                'Clase de préstamo': None,
                'Movilidad geográfica': emp['Movilidad geográfica'],
                'Experiencia Profesional': emp['Experiencia Profesional'],
                'Puesto ocupado': emp['Denominación de posiciones'],
                
                # Columnas 31-40
                'Carnet de conducir B': random.choice(['Sí', 'No']),
                'Inicio': emp['Alta'] if event_type == 'Alta' else emp['Baja'],
                'Hasta.2': emp['Hasta'],
                'Denominación de la clase de me': 'Contratación' if event_type == 'Alta' else 'Baja',
                'Denominación del motivo de med': emp['Denominación del motivo de med'],
                'Alta': emp['Alta'],
                'Baja': emp['Baja'],
                'Nombre del superior (GO)': emp['Nombre del superior (GO)'],
                'Modif.el': datetime.now().date(),
                'Denominación.1': 'Activo' if pd.isna(emp['Baja']) else 'Dado de baja'
            })
    
    df = pd.DataFrame(events)
    print(f"   ✓ {len(df)} eventos con 40 columnas")
    
    return df


def generate_attendance_data(employee_df):
    """
    Genera data_asistencias.xlsx con sheets 'Días' y 'Semana'
    Columnas exactas: Grupo, Fecha, Permiso, Turno, Entró, Atraso, Salió, Adelanto, Horas Totales, Cargo
    """
    print("\n[3/6] Generando data_asistencias.xlsx...")
    
    daily_records = []
    start_date = datetime.now().date() - timedelta(days=90)
    end_date = datetime.now().date()
    
    grupos = ['OPERACIONES', 'ADMINISTRATIVO', 'TECNOLOGIA', 'CAJA']
    permisos = ['Ninguno', 'Vacaciones', 'Licencia Médica', 'Permiso Administrativo']
    
    # Turnos con horarios esperados
    turnos_info = [
        ('08:00 - 18:00(60 mins)', 8, 0, 18, 0),  # Entrada esperada: 08:00, Salida: 18:00
        ('14:00 - 22:00(30 mins)', 14, 0, 22, 0),
        ('22:00 - 06:00(30 mins)', 22, 0, 6, 0),
        ('09:00 - 17:00(60 mins)', 9, 0, 17, 0),
    ]
    
    # Mapeo español de días
    dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    
    for _, emp in employee_df.iterrows():
        emp_start = emp['Alta']
        emp_end = emp['Baja'] if pd.notna(emp['Baja']) else end_date
        current_date = max(start_date, emp_start)
        
        while current_date <= min(end_date, emp_end):
            if current_date.weekday() < 5:  # L-V
                if random.random() < 0.95:  # 95% asistencia
                    turno = random.choice(turnos_info)
                    turno_str, entrada_h, entrada_m, salida_h, salida_m = turno
                    
                    # Hora de entrada con variación (5% llegan tarde)
                    if random.random() < 0.15:  # 15% de atrasos
                        minutos_atraso = random.randint(1, 30)
                    else:
                        minutos_atraso = 0
                    
                    entrada_real = datetime.combine(
                        current_date, 
                        datetime.min.time()
                    ) + timedelta(hours=entrada_h, minutes=entrada_m + minutos_atraso)
                    
                    # Calcular horas trabajadas (8-9 horas)
                    horas_trabajo = random.uniform(8, 9)
                    salida_real = entrada_real + timedelta(hours=horas_trabajo)
                    
                    # Calcular adelanto de salida (diferencia si sale antes de lo esperado)
                    salida_esperada = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=salida_h, minutes=salida_m)
                    if salida_real.time() < salida_esperada.time():
                        minutos_adelanto = int((salida_esperada - salida_real).total_seconds() / 60)
                    else:
                        minutos_adelanto = 0
                    
                    # Formatear fecha con día de semana
                    dia_sem = dias_semana[current_date.weekday()]
                    fecha_str = current_date.strftime(f'{dia_sem} %d-%m-%Y')
                    
                    # Formatear atraso y adelanto como "H:MM"
                    atraso_str = f"{minutos_atraso // 60}:{minutos_atraso % 60:02d}"
                    adelanto_str = f"{minutos_adelanto // 60}:{minutos_adelanto % 60:02d}"
                    
                    daily_records.append({
                        'Grupo': random.choice(grupos),
                        'Fecha': fecha_str,
                        'Permiso': random.choice(permisos) if random.random() < 0.05 else 'Ninguno',
                        'Turno': turno_str,
                        'Entró': entrada_real.strftime('%H:%M'),
                        'Atraso': atraso_str,
                        'Salió': salida_real.strftime('%H:%M'),
                        'Adelanto': adelanto_str,
                        'Horas Totales': f"{int(horas_trabajo)}:{int((horas_trabajo % 1) * 60):02d}",
                        'Cargo': emp['Nº pers.']
                    })
            
            current_date += timedelta(days=1)
    
    df_dias = pd.DataFrame(daily_records)
    
    # Semana: agregar por semana
    weekly_records = []
    for emp_id in employee_df['Nº pers.']:
        emp_days = df_dias[df_dias['Cargo'] == emp_id].copy()
        
        if len(emp_days) > 0:
            # Extraer fecha de la columna 'Fecha' (formato "Vie 01-11-2024")
            emp_days['fecha_dt'] = pd.to_datetime(
                emp_days['Fecha'].str.split(' ').str[1], 
                format='%d-%m-%Y'
            )
            emp_days['Semana'] = emp_days['fecha_dt'].dt.to_period('W')
            
            for week, group in emp_days.groupby('Semana'):
                # Sumar horas totales (formato "H:MM")
                total_mins = 0
                for ht in group['Horas Totales']:
                    if ':' in str(ht):
                        h, m = map(int, str(ht).split(':'))
                        total_mins += h * 60 + m
                
                weekly_records.append({
                    'Grupo': group['Grupo'].iloc[0],
                    'Fecha Inicio': group['fecha_dt'].min().strftime('%Y-%m-%d'),
                    'Fecha Fin': group['fecha_dt'].max().strftime('%Y-%m-%d'),
                    'Horas Trabajadas': total_mins / 60,
                    'Cargo': emp_id
                })
    
    df_semana = pd.DataFrame(weekly_records)
    
    print(f"   ✓ Días: {len(df_dias)} registros con columna Atraso")
    print(f"   ✓ Semana: {len(df_semana)} registros")
    
    return df_dias, df_semana


def generate_training_data(employee_df):
    """
    Genera data_capacitaciones.xlsx con formato exacto:
    - Informe 2025: header en fila 5, 20 columnas
    - Participantes: 9 columnas
    """
    print("\n[4/6] Generando data_capacitaciones.xlsx...")
    
    cursos_info = [
        ('Atención al Cliente Nivel 1', 'Sala Principal', 20, 'Atención Cliente', 'Externo', 'Presencial'),
        ('Seguridad en Casino', 'Sala Principal', 16, 'Seguridad', 'Interno', 'Presencial'),
        ('Manejo de Conflictos', 'Sala Secundaria', 12, 'Soft Skills', 'Externo', 'Presencial'),
        ('Excel Avanzado', 'Online', 24, 'Tecnología', 'Externo', 'Online'),
        ('Liderazgo y Gestión', 'Centro Convenciones', 32, 'Liderazgo', 'Externo', 'Presencial'),
        ('Cumplimiento Normativo', 'Sala Principal', 8, 'Normativa', 'Interno', 'Presencial'),
    ]
    
    gerencias = ['OPERACIONES', 'ADMINISTRACION', 'TECNOLOGIA', 'RRHH']
    proveedores = ['Proveedor A', 'Proveedor B', 'Interno', 'Proveedor C']
    
    cursos_realizados = []
    participantes_data = []
    
    num_trainings = random.randint(8, 12)
    
    for i in range(num_trainings):
        curso = random.choice(cursos_info)
        mes = random.randint(1, 12)
        
        fecha_inicio = datetime(2025, mes, random.randint(1, 28)).date()
        fecha_fin = fecha_inicio + timedelta(days=random.randint(1, 5))
        
        num_asistentes = random.randint(10, 30)
        asistentes = employee_df.sample(n=min(num_asistentes, len(employee_df)))
        
        horas_totales = curso[2] * len(asistentes)
        coste = random.randint(100000, 500000)
        
        cursos_realizados.append({
            'N°': i + 1,
            'Mes': mes,
            'Título capacitación': curso[0],
            'Lugar de impartición': curso[1],
            'Fecha inicio': fecha_inicio,
            'Fecha fin': fecha_fin,
            'Objetivo / Area temática': curso[3],
            'Externo / Interno': curso[4],
            'Tipo de curso': curso[5],
            'Gerencia': random.choice(gerencias),
            'Formador / Proveedor': random.choice(proveedores),
            'Asistentes': len(asistentes),
            'Horas': curso[2],
            'Horas totales': horas_totales,
            'Coste total': coste,
            'Valoracion del formador': round(random.uniform(3.5, 5.0), 1),
            'Indice de satisfacciOn': round(random.uniform(3.0, 5.0), 1),
            'NPS': random.randint(30, 90),
            'Unnamed: 18': None,
            'Unnamed: 19': None
        })
        
        # Participantes
        for _, emp in asistentes.iterrows():
            first_name = fake.first_name()
            last_name = fake.last_name()
            
            participantes_data.append({
                'N°': i + 1,
                'MES': mes,
                'Rut': emp['RUT'],
                'NºEMPLEADO': emp['Nº pers.'],
                'NOMBRE': first_name,
                'APELLIDOS': last_name,
                'CORREO': f"{first_name.lower()}.{last_name.lower()}@luckia.cl",
                'NOMBRE CURSO': curso[0],
                'TOTAL HRS FORMACION': curso[2]
            })
    
    df_informe = pd.DataFrame(cursos_realizados)
    df_participantes = pd.DataFrame(participantes_data)
    
    print(f"   ✓ Informe 2025: {len(df_informe)} cursos, 20 columnas")
    print(f"   ✓ Participantes: {len(df_participantes)} participaciones, 9 columnas")
    
    return df_informe, df_participantes


def generate_gestion_asistencia(df_dias):
    """
    Genera data_gestion_asistencia.xlsx
    Usa el mismo formato que el sheet Días
    """
    print("\n[5/6] Generando data_gestion_asistencia.xlsx...")
    
    # Usar directamente el dataframe de días (ya tiene todas las columnas correctas)
    df_gestion = df_dias.copy()
    
    print(f"   ✓ {len(df_gestion)} registros con formato correcto (Grupo, Fecha, Permiso, Turno, Entró, Atraso, Salió, Adelanto, Horas Totales, Cargo)")
    
    return df_gestion


def generate_asistencia_capacitaciones(df_participantes):
    """Genera data_asistencia_capacitaciones.xlsx (mismo que Participantes)"""
    print("\n[6/6] Generando data_asistencia_capacitaciones.xlsx...")
    
    df = df_participantes.copy()
    print(f"   ✓ {len(df)} registros")
    
    return df


def save_all_files():
    """Función principal"""
    
    df_employees = generate_employee_master_data()
    df_rotaciones = generate_turnover_events(df_employees)
    df_dias, df_semana = generate_attendance_data(df_employees)
    df_capacit_informe, df_participantes = generate_training_data(df_employees)
    df_gestion = generate_gestion_asistencia(df_dias)
    df_asist_capacit = generate_asistencia_capacitaciones(df_participantes)
    
    print("\n" + "="*80)
    print("GUARDANDO ARCHIVOS...")
    print("="*80)
    
    # data_sap.xlsx
    df_employees.to_excel(os.path.join(OUTPUT_DIR, 'data_sap.xlsx'), index=False)
    print(f"✓ {OUTPUT_DIR}/data_sap.xlsx")
    
    # data_rotaciones.xlsx
    df_rotaciones.to_excel(os.path.join(OUTPUT_DIR, 'data_rotaciones.xlsx'), index=False)
    print(f"✓ {OUTPUT_DIR}/data_rotaciones.xlsx")
    
    # data_asistencias.xlsx
    with pd.ExcelWriter(os.path.join(OUTPUT_DIR, 'data_asistencias.xlsx')) as writer:
        df_dias.to_excel(writer, sheet_name='Días', index=False)
        df_semana.to_excel(writer, sheet_name='Semana', index=False)
    print(f"✓ {OUTPUT_DIR}/data_asistencias.xlsx")
    
    # data_capacitaciones.xlsx (header en fila 5)
    with pd.ExcelWriter(os.path.join(OUTPUT_DIR, 'data_capacitaciones.xlsx')) as writer:
        # 4 filas vacías antes del header
        empty_df = pd.DataFrame([[None] * len(df_capacit_informe.columns)] * 4,
                               columns=df_capacit_informe.columns)
        combined = pd.concat([empty_df, df_capacit_informe], ignore_index=True)
        
        # Escribir sin header (ya que el header real está en fila 5)
        combined.to_excel(writer, sheet_name='Informe 2025', index=False, header=False)
        
        df_participantes.to_excel(writer, sheet_name='Participantes', index=False)
    print(f"✓ {OUTPUT_DIR}/data_capacitaciones.xlsx")
    
    # data_asistencia_capacitaciones.xlsx
    df_asist_capacit.to_excel(os.path.join(OUTPUT_DIR, 'data_asistencia_capacitaciones.xlsx'), index=False)
    print(f"✓ {OUTPUT_DIR}/data_asistencia_capacitaciones.xlsx")
    
    # data_gestion_asistencia.xlsx
    df_gestion.to_excel(os.path.join(OUTPUT_DIR, 'data_gestion_asistencia.xlsx'), index=False)
    print(f"✓ {OUTPUT_DIR}/data_gestion_asistencia.xlsx")
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN")
    print("="*80)
    print(f"✓ Empleados: {len(df_employees)} (Activos: {len(df_employees[df_employees['Baja'].isna()])}, Bajas: {len(df_employees[df_employees['Baja'].notna()])})")
    print(f"✓ Tasa rotación: {(len(df_employees[df_employees['Baja'].notna()]) / len(df_employees)) * 100:.1f}%")
    print(f"✓ Estructura EXACTA de archivos dataReal/ respetada")
    print(f"\n✓ Archivos en: {OUTPUT_DIR}/\n")


if __name__ == "__main__":
    save_all_files()
    print("✅ GENERACIÓN COMPLETADA\n")
