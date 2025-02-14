import tkinter as tk
from tkinter import ttk, font
import psutil
import config

config.adjust_dpi()

root = tk.Tk()
style = ttk.Style()

# NOTE Copiado de internet
# https://stackoverflow.com/questions/42708050/tkinter-treeview-heading-styling/42738716#42738716
style.element_create("Custom.Treeheading.border", "from", "default")
style.layout("Custom.Treeview.Heading", [
    ("Custom.Treeheading.cell", {'sticky': 'nswe'}),
    ("Custom.Treeheading.border", {'sticky': 'nswe', 'children': [
        ("Custom.Treeheading.padding", {'sticky': 'nswe', 'children': [
            ("Custom.Treeheading.image", {'side': 'right', 'sticky': ''}),
            ("Custom.Treeheading.text", {'sticky': 'we'})
        ]})
    ]}),
])
# style.theme_use("clam") # @FIXME Sin esto no anda el cambio de thema para Treeview.Heading
root.title(config.APP_TITLE)
# Ajustamos el tamaño para incluir más columnas
root.geometry(config.WINDOW_SIZE)

# Hidden window temporally
root.withdraw()
# NOTE Advertencia al cargar icono
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
frm_main = tk.Frame(root)
frm_main.pack(expand=True, fill="both")
# NOTE Permite achicar verticalmente el frame principal sin deformar el panel inferior
frm_main.propagate(False)

style = ttk.Style(root)
style.configure("Custom.Treeview", borderwidth=0, relief="flat")

tree_processes = ttk.Treeview(frm_main,
                              columns=(config.COLUMN_ID, config.COLUMN_PROCESS_NAME,
                                       config.COLUMN_STATUS, config.COLUMN_LOCATION),
                              show="headings",
                              style="Custom.Treeview")
tree_processes.heading(
    config.COLUMN_ID, text=config.COLUMN_HEADERS[config.COLUMN_ID], anchor='w', command=lambda: sort_column(config.COLUMN_ID))
tree_processes.heading(config.COLUMN_PROCESS_NAME,
                       text=config.COLUMN_HEADERS[config.COLUMN_PROCESS_NAME], anchor='w', command=lambda: sort_column(config.COLUMN_PROCESS_NAME))
tree_processes.heading(
    config.COLUMN_STATUS, text=config.COLUMN_HEADERS[config.COLUMN_STATUS], anchor='w', command=lambda: sort_column(config.COLUMN_STATUS))
tree_processes.heading(config.COLUMN_LOCATION,
                       text=config.COLUMN_HEADERS[config.COLUMN_LOCATION], anchor='w', command=lambda: sort_column(config.COLUMN_LOCATION))

tree_processes.column(config.COLUMN_ID, width=5,
                      anchor="w", minwidth=75, stretch=True)
tree_processes.column(config.COLUMN_PROCESS_NAME, width=20,
                      anchor="w", minwidth=180, stretch=True)
tree_processes.column(config.COLUMN_STATUS, width=10,
                      anchor="w", minwidth=100, stretch=True)
tree_processes.column(config.COLUMN_LOCATION, width=150,
                      anchor="w", minwidth=150, stretch=True)

scb_tree = tk.Scrollbar(frm_main, orient="vertical",
                        command=tree_processes.yview)
scb_tree.pack(side="right", fill="y")

tree_processes.config(yscrollcommand=scb_tree.set)
tree_processes.pack(expand=True, fill="both")

orden_ascendente = {config.COLUMN_ID: True, config.COLUMN_PROCESS_NAME: True,
                    config.COLUMN_STATUS: True, config.COLUMN_LOCATION: True}
all_processes = []


def refresh_window(window, sleep=1000):
    """Fuerza la actualización del marco superior"""
    window.update_idletasks()
    window.withdraw()  # Oculta la ventana temporalmente
    window.after(sleep, window.deiconify)  # La vuelve a mostrar


def update_table():
    global all_processes
    for process in tree_processes.get_children():
        tree_processes.delete(process)

    all_processes = []
    for process in psutil.process_iter(attrs=['pid', 'name', 'status']):
        pid=None
        name=None
        status=None
        location=None
        try:
            pid = process.info['pid']
            name = process.info['name']
            status = process.info['status']
            location = psutil.Process(pid).exe()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            print(f"> ERROR: Error al ejecutar psutil.process_iter en 'update_table'. pid:{pid}")
            pid = process.info['pid']
            name = process.info['name']
            status = "N/A"
            location = "N/A"

        all_processes.append((pid, name or "-", status, location or "-"))

    for pid, name, status, location in all_processes:
        tree_processes.insert("", tk.END, values=(pid, name, status, location))

    lbl_total.config(
        text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: {len(all_processes)}")

    tree_processes.heading(column=config.COLUMN_ID,
                           text=f"{config.COLUMN_HEADERS[config.COLUMN_ID]} {config.SORT_DESC_ICON}")
    tree_processes.heading(column=config.COLUMN_PROCESS_NAME,
                           text=config.COLUMN_HEADERS[config.COLUMN_PROCESS_NAME])
    tree_processes.heading(column=config.COLUMN_STATUS,
                           text=config.COLUMN_HEADERS[config.COLUMN_STATUS])
    tree_processes.heading(column=config.COLUMN_LOCATION,
                           text=config.COLUMN_HEADERS[config.COLUMN_LOCATION])


def sort_column(column):
    global orden_ascendente
    data = [(tree_processes.item(row)["values"][0], tree_processes.item(row)["values"][1], tree_processes.item(
        row)["values"][2], tree_processes.item(row)["values"][3]) for row in tree_processes.get_children()]

    if column == config.COLUMN_ID:
        data.sort(key=lambda x: int(
            x[0]), reverse=not orden_ascendente[config.COLUMN_ID])
        orden_ascendente[config.COLUMN_ID] = not orden_ascendente[config.COLUMN_ID]
    elif column == config.COLUMN_PROCESS_NAME:
        data.sort(key=lambda x: x[1].lower(
        ), reverse=not orden_ascendente[config.COLUMN_PROCESS_NAME])
        orden_ascendente[config.COLUMN_PROCESS_NAME] = not orden_ascendente[config.COLUMN_PROCESS_NAME]
    elif column == config.COLUMN_STATUS:
        data.sort(key=lambda x: x[2].lower(
        ), reverse=not orden_ascendente[config.COLUMN_STATUS])
        orden_ascendente[config.COLUMN_STATUS] = not orden_ascendente[config.COLUMN_STATUS]
    elif column == config.COLUMN_LOCATION:
        data.sort(key=lambda x: x[3].lower(
        ), reverse=not orden_ascendente[config.COLUMN_LOCATION])
        orden_ascendente[config.COLUMN_LOCATION] = not orden_ascendente[config.COLUMN_LOCATION]

    for row in tree_processes.get_children():
        tree_processes.delete(row)

    for pid, name, status, location in data:
        tree_processes.insert("", "end", values=(pid, name, status, location))

    process_list = [config.COLUMN_ID, config.COLUMN_PROCESS_NAME,
                    config.COLUMN_STATUS, config.COLUMN_LOCATION]
    for col in process_list:
        if col == column:
            symbol = config.SORT_ASC_ICON if orden_ascendente[col] else config.SORT_DESC_ICON
        else:
            symbol = ""
        text = config.COLUMN_HEADERS[config.COLUMN_ID] if col == config.COLUMN_ID else config.COLUMN_HEADERS[config.COLUMN_PROCESS_NAME] if col == config.COLUMN_PROCESS_NAME else config.COLUMN_HEADERS[
            config.COLUMN_STATUS] if col == config.COLUMN_STATUS else config.COLUMN_HEADERS[config.COLUMN_LOCATION]
        tree_processes.heading(col, text=f"{text} {symbol}")


def filter_process():
    text = inp_search.get().strip().lower()

    for process in tree_processes.get_children():
        tree_processes.delete(process)

    if text == "":
        filtered_data = all_processes
    else:
        filtered_data = [(pid, name, status, location) for pid, name,
                         status, location in all_processes if text in name.lower()]

    for pid, name, status, location in filtered_data:
        tree_processes.insert("", "end", values=(pid, name, status, location))

    lbl_total.config(
        text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: {len(filtered_data)}")


def auto_adjust_columns():
    """Ajusta automáticamente el ancho de las columnas al mínimo necesario, respetando minwidth"""
    if auto_adjust_cols.get():  # Solo ajustar si el checkbox está marcado
        tree_processes.update_idletasks()  # Actualizar la geometría de la tabla
        for col in tree_processes["columns"]:
            # Obtener el valor de minwidth de la columna
            min_width = int(tree_processes.column(col, option="minwidth"))

            # Obtener solo las filas visibles (las que están en la tabla después del filtro)
            visible_rows = tree_processes.get_children()

            # Calcular el ancho máximo de la columna basado en el contenido de las celdas visibles
            # #FIXME Error si hay 0 resultados
            # Si no hay resultados al filtrar se produce un error en esta linea
            max_width = max(
                font.Font().measure(str(tree_processes.set(row, col)))  # Medir el ancho del texto
                for row in visible_rows  # Iterar solo sobre las filas visibles
            )

            # Asegurarse de que el ancho no sea menor que minwidth
            adjusted_width = max(max_width + 10, min_width)

            # Ajustar el ancho de la columna
            tree_processes.column(col, width=adjusted_width)


# Por defecto, el ajuste automático está habilitado
auto_adjust_cols = tk.BooleanVar(value=True)
enable_dark_theme = tk.BooleanVar(value=False)  # Tema oscuro

def apply_theme(theme):
    """Aplica un tema a la interfaz gráfica"""
    global current_theme
    current_theme = theme

    config.set_bg_color_title_bar(root, color=theme["name"])
    # Configurar colores para widgets de tkinter
    root.config(bg=theme["bg2"])
    frm_main.config(bg=theme["frame_bg"])
    frm_bottom_bar.config(bg=theme["frame_bg"])
    lbl_total.config(bg=theme["label_bg"], fg=theme["label_fg"])
    inp_search.config(bg=theme["entry_bg"], fg=theme["entry_fg"],
                      insertbackground=theme["entry_insertbackground"])
    btn_buscar.config(bg=theme["button_bg"], fg=theme["button_fg"],
                      activebackground=theme["button_activebackground"], activeforeground=theme["button_activeforeground"])
    btn_settings.config(bg=theme["button_bg"], fg=theme["button_fg"],
                        activebackground=theme["button_activebackground"], activeforeground=theme["button_activeforeground"])
    btn_update.config(bg=theme["button_bg"], fg=theme["button_fg"],
                      activebackground=theme["button_activebackground"], activeforeground=theme["button_activeforeground"])
    if popup != None:
        config.set_bg_color_title_bar(popup, color=theme["name"])
        popup.config(bg=theme["bg2"])
    if frm_checks != None:
        frm_checks.config(bg=theme["bg2"])
    if btn_close != None:
        btn_close.config(bg=theme["button_bg"], fg=theme["button_fg"],
                         activebackground=theme["button_activebackground"], activeforeground=theme["button_activeforeground"])
    if chk_auto_adjust_cols != None:
        chk_auto_adjust_cols.config(bg=theme["checkbox_bg"], fg=theme["checkbox_fg"],
                                    selectcolor=theme["checkbox_selectcolor"], activebackground=theme["checkbox_activebackground"],
                                    activeforeground=theme["checkbox_activeforeground"])
    if chk_enable_dark_theme != None:
        chk_enable_dark_theme.config(bg=theme["checkbox_bg"], fg=theme["checkbox_fg"],
                                     selectcolor=theme["checkbox_selectcolor"], activebackground=theme["checkbox_activebackground"],
                                     activeforeground=theme["checkbox_activeforeground"])

    # Configurar estilos para widgets de ttk
    style.theme_use("clam")  # alt | classic
    style.map("Treeview.Heading",
              background=[("active", config.COLOR_SKYBLUE0),
                          ("!active", config.COLOR_SKYBLUE1)],  # fondo cabecera
              foreground=[("active", config.COLOR_WHITE0),
                          ("!active", config.COLOR_WHITE0)],  # texto cabecera
              relief="flat")
    style.map("Custom.Treeview",
              background=[("selected", theme["treeview_background_selected"]),
                          # -> style.configure(background=theme["bg"])
                          ("!selected", theme["treeview_background_!selected"])],
              foreground=[("selected", theme["treeview_foreground_selected"]),
                          # -> style.configure(foreground=theme["fg"])
                          ("!selected", theme["treeview_foreground_!selected"])],
              # style.configure(fieldbackground=theme["bg"])
              fieldbackground=theme["bg"])


def toggle_theme():
    """Alterna entre el tema claro y oscuro"""
    if current_theme == config.LIGHT_THEME:
        apply_theme(config.DARK_THEME)
    else:
        apply_theme(config.LIGHT_THEME)

    # FIXME Posicion de ventanas
    # Se pierde la ultima posicion de la ventana y es algo incomo que se recupere en la posicion y tamaño original
    # FIXME Marco de ventana popup
    # Si se cierra la ventana popup y luego se abre en modo oscuro el marco superior no se pinta correctamente
    refresh_window(root, sleep=1200)
    refresh_window(popup, sleep=1800)


popup = None
frm_checks = None
chk_auto_adjust_cols = None
chk_enable_dark_theme = None
btn_close = None


def open_settings_popup():
    """Abre un popup con opciones de configuración"""
    global popup, frm_checks, chk_auto_adjust_cols, chk_enable_dark_theme, btn_close

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
        frm_checks = tk.Frame(popup)
        frm_checks.pack(padx=10, pady=10, anchor="w")

        chk_auto_adjust_cols = tk.Checkbutton(
            frm_checks, text=config.SETTINGS_OPTIONS[config.CHECKBOX_ADJUST_AUTOMATIC_COLS], variable=auto_adjust_cols)
        chk_auto_adjust_cols.pack(anchor="w")

        chk_enable_dark_theme = tk.Checkbutton(
            frm_checks, text=config.SETTINGS_OPTIONS[config.CHECKBOX_DARK_THEME], variable=enable_dark_theme, command=toggle_theme)
        chk_enable_dark_theme.pack(anchor="w")

        btn_close = tk.Button(
            popup, text=config.SETTINGS_OPTIONS[config.BUTTON_CLOSE_SETTINGS], command=popup.destroy)
        btn_close.pack(pady=10, ipadx=35)
    else:
        # Si la ventana ya existe, solo la mostramos
        popup.deiconify()

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

frm_bottom_bar = tk.Frame(root)
frm_bottom_bar.pack(pady=10, fill="x")

inp_search = tk.Entry(frm_bottom_bar, width=30)
inp_search.pack(side="left", padx=5, ipady=6)
inp_search.bind('<Return>', lambda event: filter_process())

btn_buscar = tk.Button(
    frm_bottom_bar, text=config.BOTTOM_FRAME[config.BUTTON_SEARCH], command=filter_process)
btn_buscar.pack(side="left", padx=5, ipadx=20)

btn_update = tk.Button(
    frm_bottom_bar, text=config.BOTTOM_FRAME[config.BUTTON_UPDATE], command=update_table)
btn_update.pack(side="left", padx=2, ipadx=15)

btn_settings = tk.Button(
    frm_bottom_bar, text=config.BOTTOM_FRAME[config.BUTTON_SETTINGS], command=open_settings_popup)
btn_settings.pack(side="left", padx=5, ipadx=10)

lbl_total = tk.Label(
    frm_bottom_bar, text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: 0")
lbl_total.pack(side="left", padx=5)

apply_theme(config.LIGHT_THEME)

update_table()

# Open main window
root.mainloop()
