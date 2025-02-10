import tkinter as tk
from tkinter import ttk
import psutil

# @TODO solucion DPI alto en pantallas https://stackoverflow.com/questions/62794931/high-dpi-tkinter-re-scaling-when-i-run-it-in-spyder-and-when-i-run-it-direct-in
import ctypes
try: # >= win 8.1
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except: # win 8.0 or less
    ctypes.windll.user32.SetProcessDPIAware()

root = tk.Tk()
root.title("Administrador de procesos")
root.geometry("800x500")  # Ajustamos el tamaño para incluir más columnas

# Hidden window temporally
root.withdraw()
# @TODO do not load this instruction before '.withdraw' otherwise a small blink occurs before loading the window completely
root.iconbitmap("taskmgr.exe_14_107.ico")

def center_window(window):
    window.update_idletasks()  # Actualizar la geometría de la ventana
    ancho_ventana = window.winfo_width()
    alto_ventana = window.winfo_height()
    ancho_pantalla = window.winfo_screenwidth()
    alto_pantalla = window.winfo_screenheight()
    x = (ancho_pantalla // 2) - (ancho_ventana // 2)
    y = (alto_pantalla // 2) - (alto_ventana // 2)
    window.geometry(f"+{x}+{y}")  # Establecer la posición de la ventana

center_window(root)

# Mostrar la ventana una vez centrada
root.deiconify()

# Resto del código (frame_tabla, tabla, scrollbar, etc.)
frame_tabla = tk.Frame(root)
frame_tabla.pack(expand=True, fill="both")

style = ttk.Style(root)
style.configure("Custom.Treeview",
                borderwidth=0,
                relief="flat",
                )

tabla = ttk.Treeview(frame_tabla, columns=("Id", "ProcessName", "Estado"), show="headings", style="Custom.Treeview")
tabla.heading("Id", text="ID", anchor='w', command=lambda: sort_column("Id"))
tabla.heading("ProcessName", text="Nombre del Proceso",anchor='w', command=lambda: sort_column("ProcessName"))
tabla.heading("Estado", text="Estado", anchor='w', command=lambda: sort_column("Estado"))

tabla.column("Id", width=100, anchor="w", stretch=True)
tabla.column("ProcessName", width=350, anchor="w", stretch=True)
tabla.column("Estado", width=150, anchor="w", stretch=True)

scrollbar = tk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
scrollbar.pack(side="right", fill="y")

tabla.config(yscrollcommand=scrollbar.set)
tabla.pack(expand=True, fill="both")

orden_ascendente = {"Id": True, "ProcessName": True, "Estado": True}
procesos_completos = []

def update_table():
    global procesos_completos
    for row in tabla.get_children():
        tabla.delete(row)

    procesos_completos = []
    for p in psutil.process_iter(attrs=['pid', 'name', 'status']):
        try:
            pid = p.info['pid']
            name = p.info['name']
            status = p.info['status']
            procesos_completos.append((pid, name, status))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    for pid, name, status in procesos_completos:
        tabla.insert("", "end", values=(pid, name, status))

    lbl_total.config(text=f"Total: {len(procesos_completos)}")

def sort_column(columna):
    global orden_ascendente
    datos = [(tabla.item(row)["values"][0], tabla.item(row)["values"][1], tabla.item(row)["values"][2]) for row in tabla.get_children()]

    if columna == "Id":
        datos.sort(key=lambda x: int(x[0]), reverse=not orden_ascendente["Id"])
        orden_ascendente["Id"] = not orden_ascendente["Id"]
    elif columna == "ProcessName":
        datos.sort(key=lambda x: x[1].lower(), reverse=not orden_ascendente["ProcessName"])
        orden_ascendente["ProcessName"] = not orden_ascendente["ProcessName"]
    elif columna == "Estado":
        datos.sort(key=lambda x: x[2].lower(), reverse=not orden_ascendente["Estado"])
        orden_ascendente["Estado"] = not orden_ascendente["Estado"]

    for row in tabla.get_children():
        tabla.delete(row)

    for pid, name, status in datos:
        tabla.insert("", "end", values=(pid, name, status))

    for col in ["Id", "ProcessName", "Estado"]:
        if col == columna:
            symbol = "▲" if orden_ascendente[col] else "▼"
        else:
            symbol = ""
        text = "ID" if col == "Id" else "Nombre del Proceso" if col == "ProcessName" else "Estado"
        tabla.heading(col, text=f"{text} {symbol}")

def filter_tasks():
    texto = entry_busqueda.get().strip().lower()

    for row in tabla.get_children():
        tabla.delete(row)

    if texto == "":
        datos_filtrados = procesos_completos
    else:
        datos_filtrados = [(pid, name, status) for pid, name, status in procesos_completos if texto in name.lower()]

    for pid, name, status in datos_filtrados:
        tabla.insert("", "end", values=(pid, name, status))

    lbl_total.config(text=f"Total: {len(datos_filtrados)}")

frame_controls = tk.Frame(root)
frame_controls.pack(pady=10, fill="x")

entry_busqueda = tk.Entry(frame_controls, width=30)
entry_busqueda.pack(side="left", padx=5, ipady=2)

btn_buscar = ttk.Button(frame_controls, text="Buscar", command=filter_tasks)
btn_buscar.pack(side="left", padx=5)

btn_actualizar = ttk.Button(frame_controls, text="Actualizar", command=update_table)
btn_actualizar.pack(side="left", padx=5)

lbl_total = tk.Label(frame_controls, text=f"Total: 0")
lbl_total.pack(side="left", padx=5)

update_table()

# Open main window
root.mainloop()