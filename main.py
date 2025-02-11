import tkinter as tk
from tkinter import ttk, font
import psutil
import config

config.adjust_dpi()

root = tk.Tk()
style = ttk.Style()
root.title(config.APP_TITLE)
root.geometry(config.WINDOW_SIZE)  # Ajustamos el tamaño para incluir más columnas

# Hidden window temporally
root.withdraw()
# @TODO do not load this instruction before '.withdraw' otherwise a small blink occurs before loading the window completely
root.iconbitmap(config.APP_ICON)

def center_window(window):
    window.update_idletasks()  # Actualizar la geometría de la ventana
    width_wnd = window.winfo_width()
    height_wnd = window.winfo_height()
    width_screen = window.winfo_screenwidth()
    height_screen = window.winfo_screenheight()
    x = (width_screen // 2) - (width_wnd // 2)
    y = (height_screen // 2) - (height_wnd // 2)
    window.geometry(f"+{x}+{y}")  # Establecer la posición de la ventana

center_window(root)

# Mostrar la ventana una vez centrada
root.deiconify()

# Resto del código (frame_tabla, tabla, scrollbar, etc.)
frame_process_table = tk.Frame(root)
frame_process_table.pack(expand=True, fill="both")

style = ttk.Style(root)
style.configure("Custom.Treeview",
                borderwidth=0,
                relief="flat",
                )

process_table = ttk.Treeview(frame_process_table, 
                    columns=(config.COLUMN_ID, config.COLUMN_PROCESS_NAME, config.COLUMN_STATUS, config.COLUMN_LOCATION),
                    show="headings", 
                    style="Custom.Treeview")
process_table.heading(config.COLUMN_ID, text=config.COLUMN_HEADERS[config.COLUMN_ID], anchor='w', command=lambda: sort_column(config.COLUMN_ID))
process_table.heading(config.COLUMN_PROCESS_NAME, text=config.COLUMN_HEADERS[config.COLUMN_PROCESS_NAME],anchor='w', command=lambda: sort_column(config.COLUMN_PROCESS_NAME))
process_table.heading(config.COLUMN_STATUS, text=config.COLUMN_HEADERS[config.COLUMN_STATUS], anchor='w', command=lambda: sort_column(config.COLUMN_STATUS))
process_table.heading(config.COLUMN_LOCATION, text=config.COLUMN_HEADERS[config.COLUMN_LOCATION], anchor='w', command=lambda: sort_column(config.COLUMN_LOCATION))
style.configure("Treeview.Heading", background="#B0E0E6", foreground="#0078D7", font=("TkDefaultFont", 10, "bold"))

process_table.column(config.COLUMN_ID, width=5, anchor="w", minwidth=75, stretch=True)
process_table.column(config.COLUMN_PROCESS_NAME, width=20, anchor="w", minwidth=120, stretch=True)
process_table.column(config.COLUMN_STATUS, width=10, anchor="w", minwidth=100, stretch=True)
process_table.column(config.COLUMN_LOCATION, width=150, anchor="w", minwidth=150, stretch=True)

scrollbar = tk.Scrollbar(frame_process_table, orient="vertical", command=process_table.yview)
scrollbar.pack(side="right", fill="y")

process_table.config(yscrollcommand=scrollbar.set)
process_table.pack(expand=True, fill="both")

orden_ascendente = {config.COLUMN_ID: True, config.COLUMN_PROCESS_NAME: True, config.COLUMN_STATUS: True, config.COLUMN_LOCATION: True}
all_processes = []

def update_table():
    global all_processes
    for row in process_table.get_children():
        process_table.delete(row)

    all_processes = []
    for p in psutil.process_iter(attrs=['pid', 'name', 'status']):
        try:
            pid = p.info['pid']
            name = p.info['name']
            status = p.info['status']
            location = psutil.Process(pid).exe()
            all_processes.append((pid, name, status, location))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    for pid, name, status, location in all_processes:
        process_table.insert("", tk.END, values=(pid, name, status, location))

    lbl_total.config(text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: {len(all_processes)}")

    process_table.heading(column=config.COLUMN_ID, text=f"{config.COLUMN_HEADERS[config.COLUMN_ID]} {config.SORT_DESC_ICON}")
    process_table.heading(column=config.COLUMN_PROCESS_NAME, text=config.COLUMN_HEADERS[config.COLUMN_PROCESS_NAME])
    process_table.heading(column=config.COLUMN_STATUS, text=config.COLUMN_HEADERS[config.COLUMN_STATUS])
    process_table.heading(column=config.COLUMN_LOCATION, text=config.COLUMN_HEADERS[config.COLUMN_LOCATION])

def sort_column(column):
    global orden_ascendente
    datos = [(process_table.item(row)["values"][0], process_table.item(row)["values"][1], process_table.item(row)["values"][2], process_table.item(row)["values"][3]) for row in process_table.get_children()]

    if column == config.COLUMN_ID:
        datos.sort(key=lambda x: int(x[0]), reverse=not orden_ascendente[config.COLUMN_ID])
        orden_ascendente[config.COLUMN_ID] = not orden_ascendente[config.COLUMN_ID]
    elif column == config.COLUMN_PROCESS_NAME:
        datos.sort(key=lambda x: x[1].lower(), reverse=not orden_ascendente[config.COLUMN_PROCESS_NAME])
        orden_ascendente[config.COLUMN_PROCESS_NAME] = not orden_ascendente[config.COLUMN_PROCESS_NAME]
    elif column == config.COLUMN_STATUS:
        datos.sort(key=lambda x: x[2].lower(), reverse=not orden_ascendente[config.COLUMN_STATUS])
        orden_ascendente[config.COLUMN_STATUS] = not orden_ascendente[config.COLUMN_STATUS]
    elif column == config.COLUMN_LOCATION:
        datos.sort(key=lambda x: x[3].lower(), reverse=not orden_ascendente[config.COLUMN_LOCATION])
        orden_ascendente[config.COLUMN_LOCATION] = not orden_ascendente[config.COLUMN_LOCATION]

    for row in process_table.get_children():
        process_table.delete(row)

    for pid, name, status, location in datos:
        process_table.insert("", "end", values=(pid, name, status, location))

    process_list = [config.COLUMN_ID, config.COLUMN_PROCESS_NAME, config.COLUMN_STATUS, config.COLUMN_LOCATION]
    for col in process_list:
        if col == column:
            symbol = config.SORT_ASC_ICON if orden_ascendente[col] else config.SORT_DESC_ICON
        else:
            symbol = ""
        text = config.COLUMN_HEADERS[config.COLUMN_ID] if col == config.COLUMN_ID else config.COLUMN_HEADERS[config.COLUMN_PROCESS_NAME] if col == config.COLUMN_PROCESS_NAME else config.COLUMN_HEADERS[config.COLUMN_STATUS] if col == config.COLUMN_STATUS else config.COLUMN_HEADERS[config.COLUMN_LOCATION]
        process_table.heading(col, text=f"{text} {symbol}")

def filter_process():
    text = entry_search.get().strip().lower()

    for row in process_table.get_children():
        process_table.delete(row)

    if text == "":
        filtered_data = all_processes
    else:
        filtered_data = [(pid, name, status, location) for pid, name, status, location in all_processes if text in name.lower()]

    for pid, name, status, location in filtered_data:
        process_table.insert("", "end", values=(pid, name, status, location))

    lbl_total.config(text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: {len(filtered_data)}")

def auto_adjust_columns():
    """Ajusta automáticamente el ancho de las columnas al mínimo necesario, respetando minwidth"""
    if auto_adjust_var.get():  # Solo ajustar si el checkbox está marcado
        process_table.update_idletasks()  # Actualizar la geometría de la tabla
        for col in process_table["columns"]:
            # Obtener el valor de minwidth de la columna
            min_width = int(process_table.column(col, option="minwidth"))

            # Obtener solo las filas visibles (las que están en la tabla después del filtro)
            visible_rows = process_table.get_children()

            # Calcular el ancho máximo de la columna basado en el contenido de las celdas visibles
            max_width = max(
                font.Font().measure(str(process_table.set(row, col)))  # Medir el ancho del texto
                for row in visible_rows  # Iterar solo sobre las filas visibles
            )

            # Asegurarse de que el ancho no sea menor que minwidth
            adjusted_width = max(max_width + 10, min_width)

            # Ajustar el ancho de la columna
            process_table.column(col, width=adjusted_width)

auto_adjust_var = tk.BooleanVar(value=True)  # Por defecto, el ajuste automático está habilitado
enable_dark_theme = tk.BooleanVar(value=False) # Tema oscuro

def open_settings_popup():
    """Abre un popup con opciones de configuración"""
    popup = tk.Toplevel(root)
    popup.title("Configuración")
    popup.geometry("320x140")
    popup.resizable(False, False)
    popup.attributes("-toolwindow", True)

    # Ocular temporalmente y mostrar recién cuando este centrada
    popup.withdraw()
    center_window(popup)
    popup.deiconify()

    frame_checks = tk.Frame(popup)
    frame_checks.pack( padx=10, pady=10,anchor="w")

    # Checkbox para habilitar/deshabilitar el ajuste automático de columnas
    auto_adjust_checkbox = tk.Checkbutton(frame_checks, text=config.SETTINGS_OPTIONS[config.CHECKBOX_ADJUST_AUTOMATIC_COLS], variable=auto_adjust_var)
    auto_adjust_checkbox.pack(anchor="w")

    enable_dark_theme_checkbox= tk.Checkbutton(frame_checks,text=config.SETTINGS_OPTIONS[config.CHECKBOX_DARK_THEME], variable=enable_dark_theme)
    enable_dark_theme_checkbox.pack( anchor="w")

    close_button = ttk.Button(popup, text=config.SETTINGS_OPTIONS[config.BUTTON_CLOSE_SETTINGS], command=popup.destroy)
    close_button.pack(pady=10)

# Variable para almacenar el ID del temporizador
resize_timer = None

def on_window_resize(event):
    """Función que se ejecuta cuando la ventana cambia de tamaño"""
    global resize_timer

    # Si ya hay un temporizador en marcha, cancelarlo
    if resize_timer:
        root.after_cancel(resize_timer)

    # Programar la ejecución de auto_adjust_columns después de 200 ms
    resize_timer = root.after(200, auto_adjust_columns)

# Vincular el evento de cambio de tamaño de la ventana a la función on_window_resize
root.bind("<Configure>", on_window_resize)

frame_controls = tk.Frame(root)
frame_controls.pack(pady=10, fill="x")

entry_search = tk.Entry(frame_controls, width=30)
entry_search.pack(side="left", padx=5, ipady=2)
entry_search.bind('<Return>', lambda event: filter_process())

btn_buscar = ttk.Button(frame_controls, text=config.BOTTOM_FRAME[config.BUTTON_SEARCH], command=filter_process)
btn_buscar.pack(side="left", padx=5)

btn_update = ttk.Button(frame_controls, text=config.BOTTOM_FRAME[config.BUTTON_UPDATE], command=update_table)
btn_update.pack(side="left", padx=5)

btn_settings = ttk.Button(frame_controls, text=config.BOTTOM_FRAME[config.BUTTON_SETTINGS], command=open_settings_popup)
btn_settings.pack(side="left", padx=5, ipadx=10)

lbl_total = tk.Label(frame_controls, text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: 0")
lbl_total.pack(side="left", padx=5)

update_table()

# Open main window
root.mainloop()