import tkinter as tk
from tkinter import ttk, font
import psutil
import config

config.adjust_dpi()

root = tk.Tk()
style = ttk.Style()

# TODO copiado de https://stackoverflow.com/questions/42708050/tkinter-treeview-heading-styling/42738716#42738716 
style.element_create("Custom.Treeheading.border", "from", "default")
style.layout("Custom.Treeview.Heading", [
    ("Custom.Treeheading.cell", {'sticky': 'nswe'}),
    ("Custom.Treeheading.border", {'sticky':'nswe', 'children': [
        ("Custom.Treeheading.padding", {'sticky':'nswe', 'children': [
            ("Custom.Treeheading.image", {'side':'right', 'sticky':''}),
            ("Custom.Treeheading.text", {'sticky':'we'})
        ]})
    ]}),
])
# style.theme_use("clam") # @FIXME Sin esto no anda el cambio de thema para Treeview.Heading
root.title(config.APP_TITLE)
root.geometry(config.WINDOW_SIZE)  # Ajustamos el tamaño para incluir más columnas

# Hidden window temporally
root.withdraw()
# TODO Carga de icono (advertencia)
# No colocar esta función antes de '.withdraw' de lo contrario, se produce un pequeño parpadeo antes de cargar la ventana por completo
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

# TODO Estilo original cabeceras
# style.configure("Treeview.Heading", background="#B0E0E6", foreground="#0078D7", font=("TkDefaultFont", 10, "bold"))
process_table = ttk.Treeview(frame_process_table, 
                    columns=(config.COLUMN_ID, config.COLUMN_PROCESS_NAME, config.COLUMN_STATUS, config.COLUMN_LOCATION),
                    show="headings", 
                    style="Custom.Treeview")
process_table.heading(config.COLUMN_ID, text=config.COLUMN_HEADERS[config.COLUMN_ID], anchor='w', command=lambda: sort_column(config.COLUMN_ID))
process_table.heading(config.COLUMN_PROCESS_NAME, text=config.COLUMN_HEADERS[config.COLUMN_PROCESS_NAME],anchor='w', command=lambda: sort_column(config.COLUMN_PROCESS_NAME))
process_table.heading(config.COLUMN_STATUS, text=config.COLUMN_HEADERS[config.COLUMN_STATUS], anchor='w', command=lambda: sort_column(config.COLUMN_STATUS))
process_table.heading(config.COLUMN_LOCATION, text=config.COLUMN_HEADERS[config.COLUMN_LOCATION], anchor='w', command=lambda: sort_column(config.COLUMN_LOCATION))

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

# FIXME Problema al cliquear controles (tema oscuro)
# En algunos controles como los botones o el texto de los checkbox al presionar se ve un parpadeo claro
# esto habría que cambiarlo en el tema oscuro o también configurar un color (si se puede).
# TODO Marco de ventana (tema oscuro)
# Averiguar si se puede cambiar el color del marco de la ventana
def apply_theme(theme):
    """Aplica un tema a la interfaz gráfica"""
    global current_theme
    current_theme = theme

    # Configurar colores para widgets de tkinter
    root.config(bg=theme["bg"])
    frame_process_table.config(bg=theme["bg"])
    frame_controls.config(bg=theme["bg"])
    lbl_total.config(bg=theme["bg"], fg=theme["fg"])
    entry_search.config(bg=theme["button_bg"], fg=theme["fg"], insertbackground=theme["fg"])
    btn_buscar.config(bg=theme["button_bg"], fg=theme["button_fg"])
    btn_settings.config(bg=theme["button_bg"], fg=theme["button_fg"])
    btn_update.config(bg=theme["button_bg"], fg=theme["button_fg"])
    if popup != None:
        popup.config(bg=theme["button_bg"])
    if frame_checks != None:
        frame_checks.config(bg=theme["button_bg"])
    if btn_close != None:
        btn_close.config(bg=theme["button_bg"],fg=theme["button_fg"])
    if chk_auto_adjust_cols != None:
        chk_auto_adjust_cols.config(bg=theme["button_bg"],fg=theme["button_fg"], selectcolor=theme["checkbox_bg"])
    if chk_enable_dark_theme != None:
        chk_enable_dark_theme.config(bg=theme["button_bg"],fg=theme["button_fg"], selectcolor=theme["checkbox_bg"])

    # Configurar estilos para widgets de ttk
    # style.configure("TButton", background=theme["button_bg"], foreground=theme["button_fg"])
    style.theme_use("clam")
    style.configure("Custom.Treeview", background=theme["treeview_bg"], foreground=theme["treeview_fg"], fieldbackground=theme["treeview_bg"])
    style.configure("Treeview.Heading", background=theme["treeview_heading_bg"], foreground=theme["treeview_heading_fg"], relief="flat")
    style.map("Treeview.Heading",
          background=[("active", "#2980B9"), ("!active", "#3498DB")],
          foreground=[("active", "white"), ("!active", "white")])
    style.map("Custom.Treeview", background=[("selected", theme["treeview_heading_bg"])], foreground=[("selected", theme["treeview_heading_fg"])])

    # Actualizar la tabla para reflejar los cambios
    # update_table()

def toggle_theme():
    """Alterna entre el tema claro y oscuro"""
    if current_theme == config.LIGHT_THEME:
        apply_theme(config.DARK_THEME)
    else:
        apply_theme(config.LIGHT_THEME)

popup = None
frame_checks = None
chk_auto_adjust_cols = None
chk_enable_dark_theme = None
btn_close = None

def open_settings_popup():
    """Abre un popup con opciones de configuración"""
    global popup, frame_checks, chk_auto_adjust_cols, chk_enable_dark_theme, btn_close

    # Solo crea la ventana si no ha sido creada antes o si ha sido destruida
    if popup is None or not popup.winfo_exists():
        popup = tk.Toplevel(root)
        popup.title(config.SETTINGS_OPTIONS[config.TITLE_WND_SETTINGS])
        popup.geometry(config.SETTINGS_OPTIONS[config.SIZE_WND_SETTINGS])
        popup.resizable(False, False)
        popup.attributes("-toolwindow", True)

        # Ocultar temporalmente y mostrar recién cuando esté centrada
        popup.withdraw()
        center_window(popup)
        popup.deiconify()

        # Crear los controles solo una vez
        frame_checks = tk.Frame(popup)
        frame_checks.pack(padx=10, pady=10, anchor="w")

        chk_auto_adjust_cols = tk.Checkbutton(frame_checks, text=config.SETTINGS_OPTIONS[config.CHECKBOX_ADJUST_AUTOMATIC_COLS], variable=auto_adjust_var)
        chk_auto_adjust_cols.pack(anchor="w")

        chk_enable_dark_theme = tk.Checkbutton(frame_checks, text=config.SETTINGS_OPTIONS[config.CHECKBOX_DARK_THEME], variable=enable_dark_theme, command=toggle_theme)
        chk_enable_dark_theme.pack(anchor="w")

        btn_close = tk.Button(popup, text=config.SETTINGS_OPTIONS[config.BUTTON_CLOSE_SETTINGS], command=popup.destroy)
        btn_close.pack(pady=10, ipadx=35)
    else:
        # Si la ventana ya existe, solo la mostramos
        popup.deiconify()
    # TODO Posible mejora
    # refactorizar logica, ver si se puede mejorar esto y no hacer esta llamada
    apply_theme(current_theme)

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
entry_search.pack(side="left", padx=5, ipady=5)
entry_search.bind('<Return>', lambda event: filter_process())

btn_buscar = tk.Button(frame_controls, text=config.BOTTOM_FRAME[config.BUTTON_SEARCH], command=filter_process)
btn_buscar.pack(side="left", padx=5, ipadx=20)

btn_update = tk.Button(frame_controls, text=config.BOTTOM_FRAME[config.BUTTON_UPDATE], command=update_table)
btn_update.pack(side="left", padx=2, ipadx=15)

btn_settings = tk.Button(frame_controls, text=config.BOTTOM_FRAME[config.BUTTON_SETTINGS], command=open_settings_popup)
btn_settings.pack(side="left", padx=5, ipadx=10)

lbl_total = tk.Label(frame_controls, text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: 0")
lbl_total.pack(side="left", padx=5)

apply_theme(config.LIGHT_THEME)

update_table()

# Open main window
root.mainloop()