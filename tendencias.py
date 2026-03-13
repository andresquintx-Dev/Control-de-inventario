# tendencias.py
from base import conectar_db, funvendidos

def obtener_productos_stock_bajo(limite=5):
    """Obtiene productos con stock bajo (menos de 5 unidades) ordenados por stock ascendente"""
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT id, nombre, cantidad, precio FROM productos WHERE cantidad < 5 ORDER BY cantidad ASC")
    productos = cursor.fetchall()
    conexion.close()
    
    return productos

def obtener_top_5_productos():
    """Obtiene el top 5 de productos más vendidos"""
    funvendidos()
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT nombre, vendidos, precio FROM productos ORDER BY vendidos DESC LIMIT 5")
    productos = cursor.fetchall()
    conexion.close()
    
    return productos

def obtener_ventas_totales():
    """Obtiene las ventas totales"""
    funvendidos()
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT SUM(vendidos) FROM productos")
    total_ventas = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(vendidos * precio) FROM productos")
    total_ingresos = cursor.fetchone()[0] or 0
    conexion.close()
    
    return total_ventas, total_ingresos