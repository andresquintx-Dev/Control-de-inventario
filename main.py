import customtkinter as ctk
from tkinter import messagebox

# from Scripts.activate_this import base

from base import (crear_tabla, funprecio, conectar_db)
from inventario import (convertir_float_precio, agregar_producto,
                    consultar_por_id, listar_productos, 
                    actualizar_por_id)
from ventas import vender_producto_por_nombre, vender_producto_por_id
from tendencias import obtener_productos_stock_bajo, obtener_top_5_productos, obtener_ventas_totales

# --- Inicialización de la base de datos ---
crear_tabla()   # Crea la tabla "productos" si no existe
funprecio()     # Inicializa/prepara funciones relacionadas con precios

# =============================
#   Funciones para la GUI
# =============================

def refrescar_lista():
    """Refresca el listado de productos en la interfaz"""
    txt_lista.configure(state="normal")
    txt_lista.delete("1.0", "end")

    from base import conectar_db
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, cantidad, precio, fecha_vencimiento FROM productos ORDER BY nombre")
    productos = cursor.fetchall()
    conexion.close()

    if not productos:
        txt_lista.insert("end", "El inventario se encuentra vacío.\n")
    else:
     for id, nombre, cantidad, precio, fecha in productos:
      txt_lista.insert("end", f"ID: {id}\n")
      txt_lista.insert("end", f"Nombre: {nombre}\n")
      txt_lista.insert("end", f"Cantidad: {cantidad}\n")
      txt_lista.insert("end", f"Precio: ${precio:.2f}\n")
      txt_lista.insert("end", f"Fecha vencimiento: {fecha}\n")
      txt_lista.insert("end", "-"*30 + "\n")

    txt_lista.configure(state="disabled")

def accion_agregar():
    nombre = entry_nom.get().strip().lower()

    try:
        cantidad = int(entry_cantidad.get())
        if cantidad <= 0:
            messagebox.showerror("Error", "Cantidad inválida.")
            return
    except ValueError:
        messagebox.showerror("Error", "Cantidad inválida.")
        return

    precio_raw = entry_precio.get().strip()
    precio = convertir_float_precio(precio_raw)
    if precio is None or precio <= 0:
        messagebox.showerror("Error", "Precio inválido.")
        return
    
    fecha_vencimiento = entry_fecha.get().strip()
    if not fecha_vencimiento:
       messagebox.showerror("Error", "Ingrese fecha de vencimiento.")
       return

    id_generado = agregar_producto(nombre, cantidad, precio, fecha_vencimiento)
    if id_generado:
        lbl_salida.configure(text=f"!Producto agregado con éxito! El ID registrado es: {id_generado}")
        entry_nom.delete(0, "end")
        entry_cantidad.delete(0, "end")
        entry_precio.delete(0, "end")
        refrescar_lista()
    else:
        messagebox.showerror("Error", "No fue posible agregar el producto.")


def accion_consulta():
    valor = entry_consulta.get().strip()
    if not valor:
        messagebox.showwarning("Consulta inválida", "Ingrese un valor válido (ID o Nombre).")
        return

    conexion = conectar_db()
    cursor = conexion.cursor()

    # prueba ejercutar con el id
    cursor.execute("SELECT id, nombre, cantidad, precio, fecha_vencimiento FROM productos WHERE id = ?", (valor,))
    producto = cursor.fetchone()

    # en el caso que no lo haga lo intentara por nombre
    if not producto:
        cursor.execute("SELECT id, nombre, cantidad, precio, fecha_vencimiento FROM productos WHERE nombre = ?", (valor,))
        producto = cursor.fetchone()

    conexion.close()

    txt_resultado.configure(state="normal")
    if producto:
        txt_resultado.insert("end", f"Resultado de consulta'{valor}':\n")
        txt_resultado.insert("end", f"ID: {producto[0]}\n")
        txt_resultado.insert("end", f"Nombre: {producto[1]}\n")
        txt_resultado.insert("end", f"Cantidad: {producto[2]}\n")
        txt_resultado.insert("end", f"Fecha de vencimiento: {producto[4]}\n")
        txt_resultado.insert("end", "-"*30 + "\n\n")
    else:
        messagebox.showwarning("No encontrado", f" No existe ningún producto con '{valor}'.")
    txt_resultado.configure(state="disabled")


def accion_buscar():
    nombre = entry_mod_id_2.get().strip()
    conexion = conectar_db()
    cursor = conexion.cursor()
    if nombre.isalnum():
        cursor.execute("SELECT COUNT(*) FROM productos WHERE id = ?", (nombre,))
        existe = cursor.fetchone()[0]

        if existe == 0:
            messagebox.showerror("Error", f"No existe un producto con el ID: {nombre}")
            return
        
        resultado = consultar_por_id(nombre)

        if isinstance(resultado, dict):
           lbl_act_1.configure(
    text=f"Nombre: {resultado['nombre']}\n"
         f"Cantidad: {resultado['cantidad']}\n"
         f"Precio actual: ${resultado['precio']:.2f}\n"
         f"Fecha actual: {resultado['fecha_vencimiento']}"

)
        conexion.close()

    else:
        messagebox.showinfo("Info", "Digite un ID o un nombre:")
        conexion.close()
        return
    
def accion_modificar():
    nombre = entry_mod_id_2.get().strip()
    conexion = conectar_db()
    cursor = conexion.cursor()
    if nombre.isalnum():
        cursor.execute("SELECT COUNT(*) FROM productos WHERE id = ?", (nombre,))
        existe = cursor.fetchone()[0]

        if existe == 0:
            messagebox.showerror("Error", f"No existe un producto con ID {nombre}")
            return
        
        nuevo_precio = entry_nuevo_precio.get().strip()
        precio = convertir_float_precio(nuevo_precio)
        if precio is None or precio <= 0:
            messagebox.showerror("Error", "Precio inválido.")
            return
        nueva_fecha = entry_nueva_fecha.get().strip()

        if not nueva_fecha:
            messagebox.showerror("Error", "Ingrese nueva fecha de vencimiento.")
            return

        actualizar_por_id(nombre, precio, nueva_fecha)  

    else:
        messagebox.showinfo("Info", "Digite un ID")
        return

def accion_vender_por_nombre():
    nombre = entry_vender_nombre.get().strip()

    try:
        cantidad = int(entry_vender_cantidad.get())
        if cantidad <= 0:
            messagebox.showerror("Error", "La cantidad debe ser mayor a 0.")
            return
    except ValueError:
        messagebox.showerror("Error", "Cantidad inválida.")
        return

    vender_producto_por_nombre(nombre, cantidad)
    lbl_vender.configure(text=f"Venta exitosa de {cantidad} unidades del producto {nombre}.")
    refrescar_lista()

def accion_vender_por_id():
    identificador = entry_vender_id.get().strip()

    try:
        cantidad = int(entry_vender_cantidad_id.get())
        if cantidad <= 0:
            messagebox.showerror("Error", "La cantidad debe ser mayor 0.")
            return
    except ValueError:
        messagebox.showerror("Error", "Cantidad inválida.")
        return

    vender_producto_por_id(identificador, cantidad)
    lbl_vender.configure(text=f"Venta exitosa de {cantidad} unidades del ID {identificador}.")
    refrescar_lista()


# =============================
#   Interfaz con CustomTkinter
# =============================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("Sistema de Inventario")
root.geometry("900x600")

# --- Crear pestañas ---
notebook = ctk.CTkTabview(root)
notebook.pack(fill="both", expand=True, padx=8, pady=8)

tab_inv = notebook.add("Inventario")
tab_mod = notebook.add("Actualizar")
tab_ventas = notebook.add("Ventas")
tab_consulta = notebook.add("Consulta")
tab_Tendencias = notebook.add("Tendencias")
tab_Eliminar = notebook.add("Eliminar")



# =============================
#   Pestaña Inventario
# =============================

left = ctk.CTkFrame(tab_inv)
left.pack(side="left", fill="y", padx=6, pady=6)

ctk.CTkLabel(left, text="Nombre:").pack(anchor="w")
entry_nom = ctk.CTkEntry(left, width=200)
entry_nom.pack(anchor="w")

ctk.CTkLabel(left, text="Cantidad:").pack(anchor="w")
entry_cantidad = ctk.CTkEntry(left, width=200)
entry_cantidad.pack(anchor="w")
    
ctk.CTkLabel(left, text="Precio:").pack(anchor="w")
entry_precio = ctk.CTkEntry(left, width=200)
entry_precio.pack(anchor="w")

ctk.CTkLabel(left, text="Fecha de vencimiento (YYYY-MM-DD)").pack(anchor="w")
entry_fecha = ctk.CTkEntry(left, width=200)
entry_fecha.pack(anchor="w")

ctk.CTkButton(left, text="Agregar producto", command=accion_agregar).pack(anchor="w", pady=4)
lbl_salida = ctk.CTkLabel(left, text="")
lbl_salida.pack(anchor="w", pady=2)


right = ctk.CTkFrame(tab_inv)
right.pack(side="right", fill="both", expand=True, padx=6, pady=6)

ctk.CTkLabel(right, text="Listado de productos:").pack(anchor="w")
txt_lista = ctk.CTkTextbox(right, width=500, height=400, state="disabled")
txt_lista.pack(fill="both", expand=True)

refrescar_lista()

# =============================
#   Pestaña Actualizar
# =============================

ctk.CTkLabel(tab_mod, text="Ingrese el ID del producto:").pack(anchor="w")
entry_mod_id_2 = ctk.CTkEntry(tab_mod, width=200)
entry_mod_id_2.pack(anchor="w")

ctk.CTkButton(tab_mod, text="Buscar producto", command=accion_buscar).pack(anchor="w", pady=2)
lbl_buscar_id = ctk.CTkLabel(tab_mod, text="")
lbl_buscar_id.pack(anchor="w", pady=2)
lbl_act_1 = ctk.CTkLabel(tab_mod, text="")
lbl_act_1.pack(anchor="w", pady=2)

ctk.CTkLabel(tab_mod, text="Precio nuevo:").pack(anchor="w")
entry_nuevo_precio = ctk.CTkEntry(tab_mod, width=200)
entry_nuevo_precio.pack(anchor="w")

ctk.CTkLabel(tab_mod, text="Nueva fecha de vencimiento (YYYY-MM-DD):").pack(anchor="w")
entry_nueva_fecha = ctk.CTkEntry(tab_mod, width=200)
entry_nueva_fecha.pack(anchor="w")

ctk.CTkButton(tab_mod, text="Actualizar", command=accion_modificar).pack(anchor="w", pady=2)
lbl_act = ctk.CTkLabel(tab_mod, text="")
lbl_act.pack(anchor="w", pady=2)

# =============================
#   Pestaña Ventas
# =============================

ctk.CTkLabel(tab_ventas, text="Nombre producto:").pack(anchor="w")
entry_vender_nombre = ctk.CTkEntry(tab_ventas, width=200)
entry_vender_nombre.pack(anchor="w")

ctk.CTkLabel(tab_ventas, text="Cantidad:").pack(anchor="w")
entry_vender_cantidad = ctk.CTkEntry(tab_ventas, width=200)
entry_vender_cantidad.pack(anchor="w")

ctk.CTkButton(tab_ventas, text="Vender por nombre", command=accion_vender_por_nombre).pack(anchor="w", pady=2)

ctk.CTkLabel(tab_ventas, text="ID producto:").pack(anchor="w")
entry_vender_id = ctk.CTkEntry(tab_ventas, width=200)
entry_vender_id.pack(anchor="w")

ctk.CTkLabel(tab_ventas, text="Cantidad:").pack(anchor="w")
entry_vender_cantidad_id = ctk.CTkEntry(tab_ventas, width=200)
entry_vender_cantidad_id.pack(anchor="w")

ctk.CTkButton(tab_ventas, text="Vender por ID", command=accion_vender_por_id).pack(anchor="w", pady=2)

lbl_vender = ctk.CTkLabel(tab_ventas, text="")
lbl_vender.pack(anchor="w", pady=2)

# =============================
#   Pestaña Consulta
# =============================

frame_consulta = ctk.CTkFrame(tab_consulta)
frame_consulta.pack(fill="both", expand=True, padx=10, pady=10)
ctk.CTkButton(frame_consulta, text="Consultar", command=accion_consulta).pack(anchor="w", pady=5)

# Campo de entrada (puede ser ID o nombre)

ctk.CTkLabel(frame_consulta, text="Ingrese ID o Nombre del producto:").pack(anchor="w")
entry_consulta = ctk.CTkEntry(frame_consulta, width=200)
entry_consulta.pack(anchor="w")


ctk.CTkLabel(frame_consulta, text="Resultado de la consulta:").pack(anchor="w", pady=10)
txt_resultado = ctk.CTkTextbox(frame_consulta, width=500, height=200, state="disabled")
txt_resultado.pack(fill="both", expand=True, pady=5)

# Botón para limpiar resultados

def limpiar_resultado():
    txt_resultado.configure(state="normal")
    txt_resultado.delete("1.0", "end")
    txt_resultado.configure(state="disabled")

ctk.CTkButton(frame_consulta, text="Limpiar resultados", command=limpiar_resultado).pack(anchor="w", pady=5)

# =============================
#   Pestaña Tendencias
# =============================

def formatear_precio(precio):
    """Formatea el precio para mostrar sin decimales y con puntos de miles"""
    try:
        precio_int = int(precio)
        return f"${precio_int:,}".replace(",", ".")
    except:
        return f"${precio}"

def mostrar_stock_bajo():
    """Muestra productos con stock bajo"""
    productos = obtener_productos_stock_bajo()
    
    if productos:
        texto = "\n⚠️ PRODUCTOS CON STOCK BAJO\n\n"
        for i, (id, nombre, cantidad, precio) in enumerate(productos, 1):
            texto += f"{i}. {nombre}\n"
            texto += f"    Stock: {cantidad} unidades.\n"
            texto += f"    Precio: {formatear_precio(precio)}\n"
            texto += "-" * 50 + "\n"
    else:
        texto = "✅ Todo el stock se encuentra en niveles adecuados."
    
    lbl_tendencia_producto.configure(text=texto)

def mostrar_ventas_totales():
    """Muestra las ventas totales"""
    total_ventas, total_ingresos = obtener_ventas_totales()
    
    if total_ventas > 0:
        texto = f"\n💰 VENTAS TOTALES\n\n"
        texto += f"     Unidades vendidas: {total_ventas}\n"
        texto += f"     Ingresos totales: {formatear_precio(total_ingresos)}\n"
    else:
        texto = "No hay ventas registradas."
    
    lbl_tendencia_ventas.configure(text=texto)

def mostrar_top_5_productos():
    """Muestra el top 5 de productos más vendidos"""
    productos = obtener_top_5_productos()
    
    if productos:
        texto = "\n📊 TOP 5 MEDICAMENTOS\n\n"
        for i, (nombre, vendidos, precio) in enumerate(productos, 1):
            ingresos = vendidos * precio
            texto += f"{i}. {nombre}\n"
            texto += f"   Vendidos: {vendidos} unidades.\n"
            texto += f"   Precio: {formatear_precio(precio)}\n"
            texto += f"   Ingresos: {formatear_precio(ingresos)}\n"
            texto += "-" * 20 + "\n"
    else:
        texto = "No hay datos de ventas disponibles."
    
    # Mostrar en el área de texto
    txt_tendencias.configure(state="normal")
    txt_tendencias.delete("1.0", "end")
    txt_tendencias.insert("end", texto)
    txt_tendencias.configure(state="disabled")

# Configuración de la interfaz para Tendencias
frame_tendencias = ctk.CTkFrame(tab_Tendencias)
frame_tendencias.pack(fill="both", expand=True, padx=10, pady=10)

# Título
ctk.CTkLabel(frame_tendencias, text="ANÁLISIS DE TENDENCIAS", 
             font=("Arial", 16, "bold")).pack(pady=10)

# Sección: Stock bajo
frame_producto = ctk.CTkFrame(frame_tendencias)
frame_producto.pack(fill="x", padx=5, pady=5)

ctk.CTkButton(frame_producto, text="Stock Bajo", 
              command=mostrar_stock_bajo, width=200).pack(side="left", padx=5)
lbl_tendencia_producto = ctk.CTkLabel(frame_producto, text="Presiona el botón para ver.", 
                                     wraplength=300, justify="left")
lbl_tendencia_producto.pack(side="left", padx=10, fill="x", expand=True)

# Sección: Ventas totales
frame_ventas = ctk.CTkFrame(frame_tendencias)
frame_ventas.pack(fill="x", padx=5, pady=5)

ctk.CTkButton(frame_ventas, text="Ventas totales", 
              command=mostrar_ventas_totales, width=200).pack(side="left", padx=5)
lbl_tendencia_ventas = ctk.CTkLabel(frame_ventas, text="Presiona el botón para ver.", 
                                   wraplength=300, justify="left")
lbl_tendencia_ventas.pack(side="left", padx=10, fill="x", expand=True)

# Sección: Top 5 productos (usa el área de texto)
frame_top5 = ctk.CTkFrame(frame_tendencias)
frame_top5.pack(fill="x", padx=5, pady=5)

ctk.CTkButton(frame_top5, text="Top 5 Medicamentos", 
              command=mostrar_top_5_productos, width=200).pack(side="left", padx=5)
ctk.CTkLabel(frame_top5, text="Resultado en el área de texto inferior ↓").pack(side="left", padx=10)

# Área de texto para el top 5
txt_tendencias = ctk.CTkTextbox(frame_tendencias, height=200, state="disabled")
txt_tendencias.pack(fill="both", expand=True, pady=10)

# =============================
#   Pestaña Eliminar
# =============================

frame_eliminar = ctk.CTkFrame(tab_Eliminar)
frame_eliminar.pack(fill="both", expand=True, padx=10, pady=10)

# Eliminar por nombre
ctk.CTkLabel(frame_eliminar, text="Eliminar por nombre:").pack(anchor="w")
entry_eliminar_tab = ctk.CTkEntry(frame_eliminar, width=200)
entry_eliminar_tab.pack(anchor="w")

def accion_eliminar_tab():
    nombre = entry_eliminar_tab.get().strip().lower()
    if not nombre:
        lbl_eliminar_tab.configure(text="Ingrese un nombre válido.")
        return
    
    from base import conectar_db
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE nombre = ?", (nombre,))
    conexion.commit()
    filas = cursor.rowcount
    conexion.close()

    refrescar_lista()
    if filas > 0:
        lbl_eliminar_tab.configure(text=f"Producto {nombre} eliminado.")
    else:
        lbl_eliminar_tab.configure(text=f"Producto no encontrado.")

ctk.CTkButton(frame_eliminar, text="Eliminar producto", command=accion_eliminar_tab).pack(anchor="w", pady=5)
lbl_eliminar_tab = ctk.CTkLabel(frame_eliminar, text="")
lbl_eliminar_tab.pack(anchor="w", pady=5)

# Eliminar por ID
ctk.CTkLabel(frame_eliminar, text="Eliminar por ID:").pack(anchor="w", pady=10)
entry_eliminar_id_tab = ctk.CTkEntry(frame_eliminar, width=200)
entry_eliminar_id_tab.pack(anchor="w")

def accion_eliminar_id_tab():
    identificador = entry_eliminar_id_tab.get().strip()
    if not identificador:
        lbl_eliminar_id_tab.configure(text="Ingrese un ID válido.")
        return

    from base import conectar_db
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (identificador,))
    conexion.commit()
    filas = cursor.rowcount
    conexion.close()

    refrescar_lista()
    if filas > 0:
        lbl_eliminar_id_tab.configure(text=f"Producto con ID {identificador} eliminado.")
    else:
        lbl_eliminar_id_tab.configure(text=f"ID no encontrado.")

ctk.CTkButton(frame_eliminar, text="Eliminar por ID", command=accion_eliminar_id_tab).pack(anchor="w", pady=5)
lbl_eliminar_id_tab = ctk.CTkLabel(frame_eliminar, text="")
lbl_eliminar_id_tab.pack(anchor="w", pady=5)


# =============================
#   Iniciar programa
# =============================
root.mainloop()
