import sqlite3

def conectar_db():
    return sqlite3.connect('inventario.db')

def crear_tabla():
    conexion = conectar_db()
    cursor = conexion.cursor()

    # Crear tabla si no existe (ya con la nueva columna)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id TEXT PRIMARY KEY,
            nombre TEXT UNIQUE,
            cantidad INTEGER,
            precio REAL DEFAULT 0,
            fecha_vencimiento TEXT
        )
    ''')

    # Verificar si la columna fecha_vencimiento existe
    cursor.execute("PRAGMA table_info(productos)")
    columnas = [col[1] for col in cursor.fetchall()]

    if "fecha_vencimiento" not in columnas:
        cursor.execute("ALTER TABLE productos ADD COLUMN fecha_vencimiento TEXT")

    conexion.commit()
    conexion.close()

def funprecio():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("PRAGMA table_info(productos)")
    cols = [row[1] for row in cursor.fetchall()]
    if "precio" not in cols:
        cursor.execute("ALTER TABLE productos ADD COLUMN precio REAL DEFAULT 0")
        conexion.commit()
    conexion.close()

def funvendidos():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("PRAGMA table_info(productos)")
    cols = [row[1] for row in cursor.fetchall()]
    if "vendidos" not in cols:
        cursor.execute("ALTER TABLE productos ADD COLUMN vendidos INTEGER DEFAULT 0")
        conexion.commit()
    conexion.close()