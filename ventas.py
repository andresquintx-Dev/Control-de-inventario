from base import conectar_db, funvendidos

def vender_producto_por_nombre(nombre, cantidad):
    funvendidos()
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT cantidad, precio FROM productos WHERE nombre = ?", (nombre,))
    prod = cursor.fetchone()
    if not prod:
        print("Producto no encontrado")
        conexion.close()
        return
    stock, precio = prod
    if cantidad > stock:
        print(f"No hay suficiente stock. Disponible: {stock}")
        conexion.close()
        return
    nuevo_stock = stock - cantidad
    total = cantidad * precio
    cursor.execute("UPDATE productos SET cantidad = ?, vendidos = vendidos + ? WHERE nombre = ?", 
                   (nuevo_stock, cantidad, nombre))
    conexion.commit()
    conexion.close()
    print(f"Venta registrada: {cantidad} x {nombre}")

def vender_producto_por_id(identificador, cantidad):
    funvendidos()
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre, cantidad, precio FROM productos WHERE id = ?", (identificador,))
    prod = cursor.fetchone()
    if not prod:
        print("ID no encontrado")
        conexion.close()
        return
    nombre, stock, precio = prod
    if cantidad > stock:
        print(f"No hay suficiente stock. Disponible: {stock}")
        conexion.close()
        return
    nuevo_stock = stock - cantidad
    total = cantidad * precio
    cursor.execute("UPDATE productos SET cantidad = ?, vendidos = vendidos + ? WHERE id = ?", 
                   (nuevo_stock, cantidad, identificador))
    conexion.commit()
    conexion.close()
    print(f"Venta registrada: {cantidad} x {nombre}")