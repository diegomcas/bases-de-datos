import mysql.connector
from datetime import datetime
import getpass
import os
import sys

# Los datos de conexión salen del entorno. Nunca escribas una contraseña acá:
# este archivo se versiona, y lo que entra al historial no sale más.
#
#   Windows (PowerShell):  $env:ELCHIP_DB_PASS = "tu_clave"
#   Linux / Mac:           export ELCHIP_DB_PASS="tu_clave"
#
# Si no está definida, el programa la pide al arrancar.
DB_CONFIG = {
    'host': os.environ.get('ELCHIP_DB_HOST', 'localhost'),
    'user': os.environ.get('ELCHIP_DB_USER', 'root'),
    'password': os.environ.get('ELCHIP_DB_PASS') or getpass.getpass('Contraseña de MySQL: '),
    'database': os.environ.get('ELCHIP_DB_NAME', 'el_chip')
}

def get_db_connection(with_db=True):
    config = DB_CONFIG.copy()
    if not with_db:
        del config['database']
    try:
        conn = mysql.connector.connect(**config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        sys.exit(1)

def init_db():
    # Connect without database first to create it if it doesn't exist
    conn = get_db_connection(with_db=False)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    conn.close()

    # In a real environment, we would execute the ElChip.sql file here.
    # For this ABM, we assume the schema is already created by the .sql script.
    print("Base de datos inicializada. Asegúrese de haber ejecutado ElChip.sql.")

# --- Helper Functions for Master Tables ---

def get_or_create_master(table, column, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    id_col = f"id_{table}"
    
    cursor.execute(f"SELECT {id_col} FROM {table} WHERE {column} = %s", (value,))
    result = cursor.fetchone()
    
    if result:
        res_id = result[0]
    else:
        cursor.execute(f"INSERT INTO {table} ({column}) VALUES (%s)", (value,))
        res_id = cursor.lastrowid
        conn.commit()
    
    conn.close()
    return res_id

# --- ABM Functions ---

def buscar_o_crear_cliente():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("\n--- Búsqueda de Cliente ---")
    apellido = input("Apellido: ")
    cursor.execute("SELECT * FROM cliente WHERE apellido LIKE %s", (f"%{apellido}%",))
    clientes = cursor.fetchall()
    
    if clientes:
        print("\nClientes encontrados:")
        for idx, c in enumerate(clientes):
            print(f"{idx + 1}. {c['nombre']} {c['apellido']} (ID: {c['id_cliente']})")
        
        opcion = input("\nSeleccione un cliente por número, o presione Enter para crear uno nuevo: ")
        if opcion.isdigit() and 1 <= int(opcion) <= len(clientes):
            res_id = clientes[int(opcion) - 1]['id_cliente']
            conn.close()
            return res_id
            
    print("\nRegistrando nuevo cliente...")
    nombre = input("Nombre: ")
    apellido = input("Apellido: ")
    
    cursor.execute("INSERT INTO cliente (nombre, apellido) VALUES (%s, %s)", (nombre, apellido))
    new_id = cursor.lastrowid
    
    # Agregar un teléfono inicial
    tel = input("Teléfono: ")
    if tel:
        id_tipo_tel = get_or_create_master('telefonotipo', 'tipo', 'Celular')
        cursor.execute("INSERT INTO telefono (numero, id_telefonotipo, id_cliente) VALUES (%s, %s, %s)", 
                       (tel, id_tipo_tel, new_id))
    
    # Agregar un email inicial
    email = input("Email: ")
    if email:
        id_tipo_email = get_or_create_master('emailtipo', 'tipo', 'Personal')
        cursor.execute("INSERT INTO email (email, id_emailtipo, id_cliente) VALUES (%s, %s, %s)", 
                       (email, id_tipo_email, new_id))
        
    conn.commit()
    conn.close()
    return new_id

def buscar_o_crear_equipo():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("\n--- Datos del Equipo ---")
    nro_serie = input("Número de Serie (S/N): ")
    cursor.execute('''
        SELECT e.*, m.nombre as marca_nombre 
        FROM equipo e 
        JOIN marca m ON e.id_marca = m.id_marca 
        WHERE nro_serie = %s
    ''', (nro_serie,))
    equipo = cursor.fetchone()
    
    if equipo:
        print(f"Equipo encontrado: {equipo['marca_nombre']} {equipo['modelo']}")
        res_id = equipo['id_equipo']
        conn.close()
        return res_id
    
    print("Equipo no encontrado. Registrando...")
    tipo = input("Tipo (Celular/Tablet/Smartwatch): ")
    marca_nombre = input("Marca: ")
    id_marca = get_or_create_master('marca', 'nombre', marca_nombre)
    modelo = input("Modelo: ")
    
    cursor.execute("INSERT INTO equipo (tipo, id_marca, modelo, nro_serie) VALUES (%s, %s, %s, %s)", 
                   (tipo, id_marca, modelo, nro_serie))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def crear_orden_servicio():
    id_cliente = buscar_o_crear_cliente()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id_empleado, usuario FROM empleado")
    empleados = cursor.fetchall()
    print("\nSeleccione Empleado:")
    for e in empleados:
        print(f"{e['id_empleado']}. {e['usuario']}")
    id_empleado = int(input("ID Empleado: "))
    
    # Estado inicial: Pendiente (ID 1 asumiendo poblado)
    id_estado_pendiente = get_or_create_master('orden_estado', 'nombre', 'Pendiente')
    
    cursor.execute("INSERT INTO orden_servicio (id_empleado, id_cliente, id_orden_estado) VALUES (%s, %s, %s)", 
                   (id_empleado, id_cliente, id_estado_pendiente))
    nro_orden = cursor.lastrowid
    
    while True:
        id_equipo = buscar_o_crear_equipo()
        
        cursor.execute("SELECT * FROM problema")
        problemas = cursor.fetchall()
        print("\nProblemas disponibles:")
        for p in problemas:
            print(f"{p['id_problema']}. {p['descripcion']} (Mano de obra: ${p['mano_obra']})")
        
        ids_problemas = input("Ingrese los IDs de los problemas separados por coma: ").split(',')
        
        for p_id in ids_problemas:
            cursor.execute("INSERT INTO orden_servicio_has_equipo (nro_orden, id_equipo, id_problema) VALUES (%s, %s, %s)",
                           (nro_orden, id_equipo, int(p_id.strip())))
        
        mas_equipos = input("\n¿Desea agregar otro equipo a esta orden? (s/n): ")
        if mas_equipos.lower() != 's':
            break
            
    conn.commit()
    conn.close()
    actualizar_total_orden(nro_orden)
    print(f"\n¡Orden Nro {nro_orden} creada con éxito!")

def actualizar_total_orden(nro_orden):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Sumar mano de obra de los problemas asociados
    cursor.execute('''
        SELECT SUM(p.mano_obra) 
        FROM orden_servicio_has_equipo ose
        JOIN problema p ON ose.id_problema = p.id_problema
        WHERE ose.nro_orden = %s
    ''', (nro_orden,))
    mano_obra_total = cursor.fetchone()[0] or 0
    
    # Sumar repuestos (usando el precio histórico guardado en la relación)
    cursor.execute('''
        SELECT SUM(phr.precio_unitario * phr.cantidad)
        FROM orden_servicio_has_equipo ose
        JOIN problema_has_repuesto phr ON ose.id_problema = phr.id_problema
        WHERE ose.nro_orden = %s
    ''', (nro_orden,))
    repuestos_total = cursor.fetchone()[0] or 0
    
    total = mano_obra_total + repuestos_total
    cursor.execute("UPDATE orden_servicio SET total = %s WHERE nro_orden = %s", (total, nro_orden))
    conn.commit()
    conn.close()

def gestionar_pagos_y_entrega():
    nro_orden = int(input("\nIngrese Nro de Orden: "))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT o.*, c.nombre, c.apellido 
        FROM orden_servicio o 
        JOIN cliente c ON o.id_cliente = c.id_cliente 
        WHERE nro_orden = %s
    ''', (nro_orden,))
    orden = cursor.fetchone()
    
    if not orden:
        print("Orden no encontrada.")
        conn.close()
        return

    print(f"\nOrden {nro_orden} - Cliente: {orden['nombre']} {orden['apellido']}")
    print(f"Total estimado: ${orden['total']}")
    
    print("\nEstados disponibles:")
    cursor.execute("SELECT * FROM orden_estado")
    estados = cursor.fetchall()
    for st in estados:
        print(f"{st['id_orden_estado']}. {st['nombre']}")
    
    id_nuevo_estado = input("Seleccione ID de Nuevo Estado [Enter para no cambiar]: ")
    if id_nuevo_estado:
        cursor.execute("UPDATE orden_servicio SET id_orden_estado = %s WHERE nro_orden = %s", (id_nuevo_estado, nro_orden))
        
        # Si se entrega, gestionar pagos múltiples
        cursor.execute("SELECT nombre FROM orden_estado WHERE id_orden_estado = %s", (id_nuevo_estado,))
        nombre_estado = cursor.fetchone()['nombre']
        
        if nombre_estado == 'Entregado':
            total_final = float(orden['total'])
            print(f"\nTotal a cubrir: ${total_final}")
            monto_pagado = 0
            
            while monto_pagado < total_final:
                print(f"\nResta pagar: ${total_final - monto_pagado}")
                cursor.execute("SELECT * FROM metodo_pago")
                metodos = cursor.fetchall()
                for m in metodos:
                    print(f"{m['id_metodo_pago']}. {m['nombre']}")
                
                id_metodo = int(input("Seleccione ID Método de Pago: "))
                monto = float(input("Monto a pagar con este método: "))
                
                cursor.execute("INSERT INTO orden_servicio_pago (nro_orden, id_metodo_pago, monto) VALUES (%s, %s, %s)",
                               (nro_orden, id_metodo, monto))
                monto_pagado += monto
            
            cursor.execute("UPDATE orden_servicio SET fecha_entrega = NOW() WHERE nro_orden = %s", (nro_orden,))
            
            # Descontar stock (basado en repuestos del problema)
            cursor.execute('''
                SELECT phr.id_repuesto, phr.cantidad
                FROM orden_servicio_has_equipo ose
                JOIN problema_has_repuesto phr ON ose.id_problema = phr.id_problema
                WHERE ose.nro_orden = %s
            ''', (nro_orden,))
            repuestos = cursor.fetchall()
            for r in repuestos:
                cursor.execute("UPDATE repuesto SET stock = stock - %s WHERE id_repuesto = %s", (r['cantidad'], r['id_repuesto']))

    conn.commit()
    conn.close()
    print("Orden actualizada correctamente.")

def listar_ordenes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT o.nro_orden, o.fecha_ingreso, st.nombre as estado_nombre, o.total, c.nombre, c.apellido
        FROM orden_servicio o
        JOIN cliente c ON o.id_cliente = c.id_cliente
        JOIN orden_estado st ON o.id_orden_estado = st.id_orden_estado
        ORDER BY o.fecha_ingreso DESC
    ''')
    ordenes = cursor.fetchall()
    
    print("\n--- Listado de Órdenes ---")
    print(f"{'Nro':<5} | {'Fecha':<20} | {'Cliente':<25} | {'Estado':<12} | {'Total':<10}")
    print("-" * 85)
    for o in ordenes:
        print(f"{o['nro_orden']:<5} | {str(o['fecha_ingreso']):<20} | {o['nombre'] + ' ' + o['apellido']:<25} | {o['estado_nombre']:<12} | ${o['total']:<10}")
    conn.close()

def ver_stock():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM repuesto")
    repuestos = cursor.fetchall()
    
    print("\n--- Stock de Repuestos ---")
    for r in repuestos:
        print(f"ID: {r['id_repuesto']} | {r['nombre']:<30} | Stock: {r['stock']} | Precio: ${r['precio_unitario']}")
    conn.close()

def ver_detalle_orden_completa():
    nro_orden = input("\nIngrese Nro de Orden para ver detalle completo: ")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM orden_servicio_completa WHERE `Nro Orden` = %s', (nro_orden,))
    detalles = cursor.fetchall()
    
    if not detalles:
        print("No se encontraron detalles para esa orden.")
    else:
        print(f"\n--- Detalle Completo de la Orden {nro_orden} ---")
        d = detalles[0]
        print(f"Cliente: {d['Cliente']}")
        print(f"Fecha Ingreso: {d['Fecha Ingreso']}")
        print(f"Estado Actual: {d['Estado Actual']}")
        print(f"Métodos de Pago: {d['Metodos de Pago']}")
        print(f"Monto Total: ${d['Monto Total']}")
        print("-" * 60)
        print(f"{'Marca / Modelo':<40} | {'Problemas Detectados'}")
        print("-" * 60)
        for d in detalles:
            equipo = f"{d['Marcas']} {d['Modelos']}"
            print(f"{equipo:<40} | {d['Problemas Detectados']}")
            
    conn.close()

# --- Main Menu ---

def main():
    init_db()
    while True:
        print("\n==============================")
        print("   SISTEMA EL CHIP - ABM (MySQL)")
        print("==============================")
        print("1. Nueva Orden de Servicio")
        print("2. Gestionar Pago y Entrega (Actualizar Estado)")
        print("3. Listar Órdenes (Resumen)")
        print("4. Ver Detalle Completo de una Orden (VISTA)")
        print("5. Ver Stock de Repuestos")
        print("6. Salir")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            crear_orden_servicio()
        elif opcion == '2':
            gestionar_pagos_y_entrega()
        elif opcion == '3':
            listar_ordenes()
        elif opcion == '4':
            ver_detalle_orden_completa()
        elif opcion == '5':
            ver_stock()
        elif opcion == '6':
            print("Saliendo...")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()
