import tkinter as tk
from tkinter import ttk
import psutil
import config

# @TODO solucion DPI alto en pantallas https://stackoverflow.com/questions/62794931/high-dpi-tkinter-re-scaling-when-i-run-it-in-spyder-and-when-i-run-it-direct-in
import ctypes
try: # >= win 8.1
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except: # win 8.0 or less
    ctypes.windll.user32.SetProcessDPIAware()

root = tk.Tk()
root.title(config.APP_TITLE)
root.geometry(config.WINDOW_SIZE)  # Ajustamos el tamaño para incluir más columnas

# Hidden window temporally
root.withdraw()
# @TODO do not load this instruction before '.withdraw' otherwise a small blink occurs before loading the window completely
root.iconbitmap(config.APP_ICON)

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

tabla = ttk.Treeview(frame_tabla, 
                    columns=(config.COLUMN_ID, config.COLUMN_PROCESS_NAME, config.COLUMN_STATUS), 
                    show="headings", 
                    style="Custom.Treeview")
tabla.heading(config.COLUMN_ID, text=config.COLUMN_HEADERS[config.COLUMN_ID], anchor='w', command=lambda: sort_column(config.COLUMN_ID))
tabla.heading(config.COLUMN_PROCESS_NAME, text=config.COLUMN_HEADERS[config.COLUMN_PROCESS_NAME],anchor='w', command=lambda: sort_column(config.COLUMN_PROCESS_NAME))
tabla.heading(config.COLUMN_STATUS, text=config.COLUMN_HEADERS[config.COLUMN_STATUS], anchor='w', command=lambda: sort_column(config.COLUMN_STATUS))

tabla.column("Id", width=100, anchor="w", stretch=True)
tabla.column("ProcessName", width=350, anchor="w", stretch=True)
tabla.column("Status", width=150, anchor="w", stretch=True)

scrollbar = tk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
scrollbar.pack(side="right", fill="y")

tabla.config(yscrollcommand=scrollbar.set)
tabla.pack(expand=True, fill="both")

orden_ascendente = {config.COLUMN_ID: True, config.COLUMN_PROCESS_NAME: True, config.COLUMN_STATUS: True}
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

    lbl_total.config(text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: {len(procesos_completos)}")

def sort_column(columna):
    global orden_ascendente
    datos = [(tabla.item(row)["values"][0], tabla.item(row)["values"][1], tabla.item(row)["values"][2]) for row in tabla.get_children()]

    if columna == config.COLUMN_ID:
        datos.sort(key=lambda x: int(x[0]), reverse=not orden_ascendente["Id"])
        orden_ascendente["Id"] = not orden_ascendente["Id"]
    elif columna == config.COLUMN_PROCESS_NAME:
        datos.sort(key=lambda x: x[1].lower(), reverse=not orden_ascendente["ProcessName"])
        orden_ascendente["ProcessName"] = not orden_ascendente["ProcessName"]
    elif columna == config.COLUMN_STATUS:
        datos.sort(key=lambda x: x[2].lower(), reverse=not orden_ascendente["Status"])
        orden_ascendente["Status"] = not orden_ascendente["Status"]

    for row in tabla.get_children():
        tabla.delete(row)

    for pid, name, status in datos:
        tabla.insert("", "end", values=(pid, name, status))

    process_list = [config.COLUMN_ID, config.COLUMN_PROCESS_NAME, config.COLUMN_STATUS]
    for col in process_list:
        if col == columna:
            symbol = config.SORT_ASC_ICON if orden_ascendente[col] else config.SORT_DESC_ICON
        else:
            symbol = ""
        text = config.COLUMN_HEADERS[config.COLUMN_ID] if col == config.COLUMN_ID else config.COLUMN_HEADERS[config.COLUMN_PROCESS_NAME] if col == config.COLUMN_PROCESS_NAME else config.COLUMN_HEADERS[config.COLUMN_STATUS]
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

    lbl_total.config(text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: {len(datos_filtrados)}")

frame_controls = tk.Frame(root)
frame_controls.pack(pady=10, fill="x")

entry_busqueda = tk.Entry(frame_controls, width=30)
entry_busqueda.pack(side="left", padx=5, ipady=2)

btn_buscar = ttk.Button(frame_controls, text=config.BOTTOM_FRAME[config.BUTTON_SEARCH], command=filter_tasks)
btn_buscar.pack(side="left", padx=5)

btn_actualizar = ttk.Button(frame_controls, text=config.BOTTOM_FRAME[config.BUTTON_UPDATE], command=update_table)
btn_actualizar.pack(side="left", padx=5)

lbl_total = tk.Label(frame_controls, text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: 0")
lbl_total.pack(side="left", padx=5)

update_table()

# Open main window
root.mainloop()