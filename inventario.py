import hashlib
import time
from base import conectar_db
from base import sqlite3

def convertir_float_precio(texto):
    """
    Convierte texto de precio a float aceptando formatos comunes:
    '12,50', '12.50', '$12.500', '12.500,99', '12 500,99'
    """
    if texto is None:
        return None
    s = str(texto).strip()
    for ch in ['$', ' ',]:
        s = s.replace(ch, '')
    if ',' in s and '.' in s:
        s = s.replace('.', '')
        s = s.replace(',', '.')
    elif ',' in s and '.' not in s:
        s = s.replace(',', '.')
    else:
        if s.count('.') == 1:
            parte_decimal = s.split('.')[-1]
            if len(parte_decimal) == 3:
                s = s.replace('.', '')
    try:
        valor = float(s)
        return round(valor, 2)
    except ValueError:
        return None

def generar_id_unico(nombre):
    """Genera un ID único basado en el nombre y timestamp"""
    timestamp = str(time.time())
    unique_string = nombre + timestamp
    return hashlib.md5(unique_string.encode()).hexdigest()[:8]

def agregar_producto(nombre, cantidad, precio=None, fecha_vencimiento=None):
    """Agrega un producto a la base de datos"""
    conexion = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()

        cursor.execute("SELECT id, cantidad FROM productos WHERE nombre = ?", (nombre,))
        producto_existente = cursor.fetchone()

        if producto_existente:
            nueva_cantidad = producto_existente[1] + cantidad
            cursor.execute("""
                UPDATE productos 
                SET cantidad = ?, fecha_vencimiento = ?
                WHERE nombre = ?
            """, (nueva_cantidad, fecha_vencimiento, nombre))
            
            id_producto = producto_existente[0]
            print(f"Producto existente. Cantidad actualizada: {nueva_cantidad}")
        
        else:
            id_producto = generar_id_unico(nombre)
            cursor.execute("""
                INSERT INTO productos (id, nombre, cantidad, precio, fecha_vencimiento) 
                VALUES (?, ?, ?, ?, ?)
            """, (id_producto, nombre, cantidad, precio, fecha_vencimiento))
            
            print("Producto agregado con éxito!")

        conexion.commit()
        return id_producto

    except sqlite3.IntegrityError:
        print("Error: El producto ya existe en la base de datos")
        return None
    finally:
        if conexion:
            conexion.close()

def consultar_por_id(identificador):
    conexion = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre, cantidad, precio FROM productos WHERE id = ?", (identificador,))
        resultado = cursor.fetchone()
        if resultado:
            return {"nombre": resultado[0], "cantidad": resultado[1], "precio": resultado[2]}
        else:
            return "ID no encontrado"
    finally:
        conexion.close()
    
def listar_productos():
    conexion = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre, cantidad, precio FROM productos ORDER BY nombre")
        productos = cursor.fetchall()
    
        if not productos:
            print("El inventario está vacío")
            return
    
        print("\n--- INVENTARIO ---")
        for id_producto, nombre, cantidad, precio in productos:
            print(f"ID: {id_producto}")
            print(f"Nombre: {nombre}")
            print(f"Cantidad: {cantidad}")
            print(f"Precio: ${precio:.2f}")
            print("-" * 20)
    finally:
        conexion.close()
    
def actualizar_por_id(ide,nuevo_precio):
    conexion = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM productos WHERE id = ?", (ide,))
        count = cursor.fetchone()[0]
        if count >= 1:
            cursor.execute("UPDATE productos SET precio = ? WHERE id = ?", (nuevo_precio, ide))
            conexion.commit()
            return f"El precio del producto con ID {ide} ha sido actualizado."
    finally:
        if conexion:
            conexion.close()
            