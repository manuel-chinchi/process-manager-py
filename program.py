import tkinter as tk
from tkinter import ttk, font
import psutil
import config


config.adjust_dpi()

resize_timer = None


def refresh_window(window, sleep=1000):
    """Fuerza la actualización del marco superior"""
    window.update_idletasks()
    window.withdraw()  # Oculta la ventana temporalmente
    window.after(sleep, window.deiconify)  # La vuelve a mostrar


def center_window(window):
    window.update_idletasks()  # Actualizar la geometría de la ventana
    width_wnd = window.winfo_width()
    height_wnd = window.winfo_height()
    width_screen = window.winfo_screenwidth()
    height_screen = window.winfo_screenheight()
    x = (width_screen // 2) - (width_wnd // 2)
    y = (height_screen // 2) - (height_wnd // 2)
    window.geometry(f"+{x}+{y}")  # Establecer la posición de la ventana


class ProcessManager:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.style = ttk.Style(self.root)

        # Set values in root
        self.root.title(config.APP_TITLE)
        self.root.geometry(config.WINDOW_SIZE)
        self.root.withdraw()
        self.root.iconbitmap(config.APP_ICON)

        self.frm_main = tk.Frame(self.root)
        self.frm_main.pack(expand=True, fill="both")
        self.frm_main.propagate(False)

        # Antes de crear los controles defino el estilo (creo que va aca como minimo, sino despues puede no andar bien)
        self.style = ttk.Style(self.root)
        self.style.element_create(
            "Custom.Treeheading.border", "from", "default")
        self.style.layout("Custom.Treeview.Heading", [
            ("Custom.Treeheading.cell", {'sticky': 'nswe'}),
            ("Custom.Treeheading.border", {'sticky': 'nswe', 'children': [
                ("Custom.Treeheading.padding", {'sticky': 'nswe', 'children': [
                    ("Custom.Treeheading.image", {
                     'side': 'right', 'sticky': ''}),
                    ("Custom.Treeheading.text", {'sticky': 'we'})
                ]})
            ]}),
        ])
        self.style.configure("Custom.Treeview", borderwidth=0, relief="flat")

        self.tree_processes = ttk.Treeview(self.frm_main,
                                           columns=(config.COLUMN_ID, config.COLUMN_PROCESS_NAME,
                                                    config.COLUMN_STATUS, config.COLUMN_LOCATION),
                                           show="headings",
                                           style="Custom.Treeview")

        self.tree_processes.heading(
            config.COLUMN_ID, text=config.COLUMN_HEADERS[config.COLUMN_ID], anchor='w', command=lambda: self.sort_column(config.COLUMN_ID))
        self.tree_processes.heading(config.COLUMN_PROCESS_NAME,
                                    text=config.COLUMN_HEADERS[config.COLUMN_PROCESS_NAME], anchor='w', command=lambda: self.sort_column(config.COLUMN_PROCESS_NAME))
        self.tree_processes.heading(
            config.COLUMN_STATUS, text=config.COLUMN_HEADERS[config.COLUMN_STATUS], anchor='w', command=lambda: self.sort_column(config.COLUMN_STATUS))
        self.tree_processes.heading(config.COLUMN_LOCATION,
                                    text=config.COLUMN_HEADERS[config.COLUMN_LOCATION], anchor='w', command=lambda: self.sort_column(config.COLUMN_LOCATION))

        self.tree_processes.column(config.COLUMN_ID, width=5,
                                   anchor="w", minwidth=75, stretch=True)
        self.tree_processes.column(config.COLUMN_PROCESS_NAME, width=20,
                                   anchor="w", minwidth=180, stretch=True)
        self.tree_processes.column(config.COLUMN_STATUS, width=10,
                                   anchor="w", minwidth=100, stretch=True)
        self.tree_processes.column(config.COLUMN_LOCATION, width=150,
                                   anchor="w", minwidth=150, stretch=True)

        self.scb_tree = tk.Scrollbar(self.frm_main, orient="vertical",
                                     command=self.tree_processes.yview)
        self.scb_tree.pack(side="right", fill="y")

        # Cargo el scroolbar-v en el tree
        self.tree_processes.config(yscrollcommand=self.scb_tree.set)
        self.tree_processes.pack(expand=True, fill="both")

        # Popup window settings
        # self.popup = tk.Toplevel(self.root)
        # self.popup.title(config.SETTINGS_OPTIONS[config.TITLE_WND_SETTINGS])
        # self.popup.geometry(config.SETTINGS_OPTIONS[config.SIZE_WND_SETTINGS])
        # self.popup.resizable(False, False)
        # self.popup.attributes("-toolwindow", True)

        self.popup = None
        self.frm_checks = None
        self.chk_auto_adjust_cols = None
        self.chk_enable_dark_theme = None
        self.btn_close = None

        # Checkbox vars
        self.auto_adjust_cols = tk.BooleanVar(value=True)
        self.enable_dark_theme = tk.BooleanVar(
            value=False)  # Tema claro por defecto

        self.orden_ascendente = {config.COLUMN_ID: True, config.COLUMN_PROCESS_NAME: True,
                                 config.COLUMN_STATUS: True, config.COLUMN_LOCATION: True}
        self.all_processes = []

        self.root.bind("<Configure>", self.on_window_resize)

        # Frame inferior/controles
        self.frm_bottom_bar = tk.Frame(self.root)
        self.frm_bottom_bar.pack(pady=10, fill="x")

        self.inp_search = tk.Entry(self.frm_bottom_bar, width=30)
        self.inp_search.pack(side="left", padx=5, ipady=6)
        self.inp_search.bind('<Return>', lambda event: self.filter_process())

        self.btn_buscar = tk.Button(
            self.frm_bottom_bar, text=config.BOTTOM_FRAME[config.BUTTON_SEARCH], command=self.filter_process)
        self.btn_buscar.pack(side="left", padx=5, ipadx=20)

        self.btn_update = tk.Button(
            self.frm_bottom_bar, text=config.BOTTOM_FRAME[config.BUTTON_UPDATE], command=self.update_table)
        self.btn_update.pack(side="left", padx=2, ipadx=15)

        self.btn_settings = tk.Button(
            self.frm_bottom_bar, text=config.BOTTOM_FRAME[config.BUTTON_SETTINGS], command=self.open_settings_popup)
        self.btn_settings.pack(side="left", padx=5, ipadx=10)

        self.lbl_total = tk.Label(
            self.frm_bottom_bar, text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: 0")
        self.lbl_total.pack(side="left", padx=5)

        self.theme = None
        self.apply_theme(config.LIGHT_THEME)  # Se aplica el tema por defecto.

        self.update_table()  # Cargar datos la primera vez

    def open_settings_popup(self):
        # Solo crea la ventana si no ha sido creada antes o si ha sido destruida
        if self.popup is None or not self.popup.winfo_exists():
            self.popup = tk.Toplevel(self.root)
            self.popup.title(
                config.SETTINGS_OPTIONS[config.TITLE_WND_SETTINGS])
            self.popup.geometry(
                config.SETTINGS_OPTIONS[config.SIZE_WND_SETTINGS])
            self.popup.resizable(False, False)
            self.popup.attributes("-toolwindow", True)

            # Ocultar temporalmente y mostrar recién cuando esté centrada
            self.popup.withdraw()
            center_window(self.popup)
            self.popup.deiconify()

            # Crear los controles solo una vez
            self.frm_checks = tk.Frame(self.popup)
            self.frm_checks.pack(padx=10, pady=10, anchor="w")

            self.chk_auto_adjust_cols = tk.Checkbutton(
                self.frm_checks, text=config.SETTINGS_OPTIONS[config.CHECKBOX_ADJUST_AUTOMATIC_COLS], variable=self.auto_adjust_cols)
            self.chk_auto_adjust_cols.pack(anchor="w")

            self.chk_enable_dark_theme = tk.Checkbutton(
                self.frm_checks, text=config.SETTINGS_OPTIONS[config.CHECKBOX_DARK_THEME], variable=self.enable_dark_theme, command=self.toggle_theme)
            self.chk_enable_dark_theme.pack(anchor="w")

            self.btn_close = tk.Button(
                self.popup, text=config.SETTINGS_OPTIONS[config.BUTTON_CLOSE_SETTINGS], command=self.popup.destroy)
            self.btn_close.pack(pady=10, ipadx=35)
        else:
            # Si la ventana ya existe, solo la mostramos
            self.popup.deiconify()

        self.apply_theme(self.theme)

    def start(self):
        center_window(self.root)
        self.root.deiconify()
        self.root.mainloop()

    def apply_theme(self, theme):
        """Aplica un tema a la interfaz gráfica"""
        self.theme = theme

        config.set_bg_color_title_bar(self.root, color=self.theme["name"])
        # Configurar colores para widgets de tkinter
        self.root.config(bg=self.theme["bg2"])
        self.frm_main.config(bg=self.theme["frame_bg"])
        self.frm_bottom_bar.config(bg=self.theme["frame_bg"])
        self.lbl_total.config(
            bg=self.theme["label_bg"], fg=self.theme["label_fg"])
        self.inp_search.config(bg=self.theme["entry_bg"], fg=self.theme["entry_fg"],
                               insertbackground=self.theme["entry_insertbackground"])
        self.btn_buscar.config(bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                               activebackground=self.theme["button_activebackground"], activeforeground=self.theme["button_activeforeground"])
        self.btn_settings.config(bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                                 activebackground=self.theme["button_activebackground"], activeforeground=self.theme["button_activeforeground"])
        self.btn_update.config(bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                               activebackground=self.theme["button_activebackground"], activeforeground=self.theme["button_activeforeground"])
        if self.popup != None:
            config.set_bg_color_title_bar(self.popup, color=self.theme["name"])
            self.popup.config(bg=self.theme["bg2"])
        if self.frm_checks != None:
            self.frm_checks.config(bg=self.theme["bg2"])
        if self.btn_close != None:
            self.btn_close.config(bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                                  activebackground=self.theme["button_activebackground"], activeforeground=self.theme["button_activeforeground"])
        if self.chk_auto_adjust_cols != None:
            self.chk_auto_adjust_cols.config(bg=self.theme["checkbox_bg"], fg=self.theme["checkbox_fg"],
                                             selectcolor=self.theme["checkbox_selectcolor"], activebackground=self.theme[
                                                 "checkbox_activebackground"],
                                             activeforeground=self.theme["checkbox_activeforeground"])
        if self.chk_enable_dark_theme != None:
            self.chk_enable_dark_theme.config(bg=self.theme["checkbox_bg"], fg=self.theme["checkbox_fg"],
                                              selectcolor=self.theme["checkbox_selectcolor"], activebackground=self.theme[
                                                  "checkbox_activebackground"],
                                              activeforeground=self.theme["checkbox_activeforeground"])

        # Configurar estilos para widgets de ttk
        self.style.theme_use("clam")  # alt | classic
        self.style.map("Treeview.Heading",
                       background=[("active", config.COLOR_SKYBLUE0),
                                   # fondo cabecera
                                   ("!active", config.COLOR_SKYBLUE1)],
                       foreground=[("active", config.COLOR_WHITE0),
                                   # texto cabecera
                                   ("!active", config.COLOR_WHITE0)],
                       relief="flat")
        self.style.map("Custom.Treeview",
                       background=[("selected", self.theme["treeview_background_selected"]),
                                   # -> style.configure(background=theme["bg"])
                                   ("!selected", self.theme["treeview_background_!selected"])],
                       foreground=[("selected", self.theme["treeview_foreground_selected"]),
                                   # -> style.configure(foreground=theme["fg"])
                                   ("!selected", self.theme["treeview_foreground_!selected"])],
                       # style.configure(fieldbackground=theme["bg"])
                       fieldbackground=self.theme["bg"])

    def toggle_theme(self):
        """Alterna entre el tema claro y oscuro"""
        if self.theme == config.LIGHT_THEME:
            self.apply_theme(config.DARK_THEME)
        else:
            self.apply_theme(config.LIGHT_THEME)

        # FIXME Posicion de ventanas
        # Se pierde la ultima posicion de la ventana y es algo incomo que se recupere en la posicion y tamaño original
        # FIXME Marco de ventana popup
        # Si se cierra la ventana popup y luego se abre en modo oscuro el marco superior no se pinta correctamente
        refresh_window(self.root, sleep=1200)
        refresh_window(self.popup, sleep=1800)

    def sort_column(self, column):
        # global self.orden_ascendente
        data = [(self.tree_processes.item(row)["values"][0], self.tree_processes.item(row)["values"][1], self.tree_processes.item(
            row)["values"][2], self.tree_processes.item(row)["values"][3]) for row in self.tree_processes.get_children()]

        if column == config.COLUMN_ID:
            data.sort(key=lambda x: int(
                x[0]), reverse=not self.orden_ascendente[config.COLUMN_ID])
            self.orden_ascendente[config.COLUMN_ID] = not self.orden_ascendente[config.COLUMN_ID]
        elif column == config.COLUMN_PROCESS_NAME:
            data.sort(key=lambda x: x[1].lower(
            ), reverse=not self.orden_ascendente[config.COLUMN_PROCESS_NAME])
            self.orden_ascendente[config.COLUMN_PROCESS_NAME] = not self.orden_ascendente[config.COLUMN_PROCESS_NAME]
        elif column == config.COLUMN_STATUS:
            data.sort(key=lambda x: x[2].lower(
            ), reverse=not self.orden_ascendente[config.COLUMN_STATUS])
            self.orden_ascendente[config.COLUMN_STATUS] = not self.orden_ascendente[config.COLUMN_STATUS]
        elif column == config.COLUMN_LOCATION:
            data.sort(key=lambda x: x[3].lower(
            ), reverse=not self.orden_ascendente[config.COLUMN_LOCATION])
            self.orden_ascendente[config.COLUMN_LOCATION] = not self.orden_ascendente[config.COLUMN_LOCATION]

        for row in self.tree_processes.get_children():
            self.tree_processes.delete(row)

        for pid, name, status, location in data:
            self.tree_processes.insert(
                "", "end", values=(pid, name, status, location))

        process_list = [config.COLUMN_ID, config.COLUMN_PROCESS_NAME,
                        config.COLUMN_STATUS, config.COLUMN_LOCATION]
        for col in process_list:
            if col == column:
                symbol = config.SORT_ASC_ICON if self.orden_ascendente[col] else config.SORT_DESC_ICON
            else:
                symbol = ""
            text = config.COLUMN_HEADERS[config.COLUMN_ID] if col == config.COLUMN_ID else config.COLUMN_HEADERS[config.COLUMN_PROCESS_NAME] if col == config.COLUMN_PROCESS_NAME else config.COLUMN_HEADERS[
                config.COLUMN_STATUS] if col == config.COLUMN_STATUS else config.COLUMN_HEADERS[config.COLUMN_LOCATION]
            self.tree_processes.heading(col, text=f"{text} {symbol}")

    def auto_adjust_columns(self):
        """Ajusta automáticamente el ancho de las columnas al mínimo necesario, respetando minwidth"""
        if self.auto_adjust_cols.get():  # Solo ajustar si el checkbox está marcado
            self.tree_processes.update_idletasks()  # Actualizar la geometría de la tabla
            for col in self.tree_processes["columns"]:
                # Obtener el valor de minwidth de la columna
                min_width = int(self.tree_processes.column(
                    col, option="minwidth"))

                # Obtener solo las filas visibles (las que están en la tabla después del filtro)
                visible_rows = self.tree_processes.get_children()

                # Calcular el ancho máximo de la columna basado en el contenido de las celdas visibles
                # TODO Corregido parcialmente
                # Cuando no hay resultados al filtrar no debería reajustar las columnas porque la experiencia
                # de usuario se siente rara.
                max_width = max(
                    [font.Font().measure(str(self.tree_processes.set(row, col)))  # Medir el ancho del texto
                     # Iterar solo sobre las filas visibles
                     for row in visible_rows]
                    or
                    [min_width]
                )

                # Asegurarse de que el ancho no sea menor que minwidth
                adjusted_width = max(max_width + 10, min_width)

                # Ajustar el ancho de la columna
                self.tree_processes.column(col, width=adjusted_width)

    def filter_process(self):
        text = self.inp_search.get().strip().lower()

        for process in self.tree_processes.get_children():
            self.tree_processes.delete(process)

        if text == "":
            filtered_data = self.all_processes
        else:
            filtered_data = [(pid, name, status, location) for pid, name,
                             status, location in self.all_processes if text in name.lower()]

        for pid, name, status, location in filtered_data:
            self.tree_processes.insert(
                "", "end", values=(pid, name, status, location))

        self.lbl_total.config(
            text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: {len(filtered_data)}")

    def update_table(self):
        # global all_processes
        for process in self.tree_processes.get_children():
            self.tree_processes.delete(process)

        # all_processes = []
        self.all_processes.clear()
        for process in psutil.process_iter(attrs=['pid', 'name', 'status']):
            pid = None
            name = None
            status = None
            location = None
            try:
                pid = process.info['pid']
                name = process.info['name']
                status = process.info['status']
                location = psutil.Process(pid).exe()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                print(
                    f"> ERROR: Error al ejecutar psutil.process_iter en 'update_table'. pid:{pid}")
                pid = process.info['pid']
                name = process.info['name']
                status = "N/A"
                location = "N/A"

            self.all_processes.append(
                (pid, name or "-", status, location or "-"))

        for pid, name, status, location in self.all_processes:
            self.tree_processes.insert(
                "", tk.END, values=(pid, name, status, location))

        self.lbl_total.config(
            text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: {len(self.all_processes)}")

        self.tree_processes.heading(column=config.COLUMN_ID,
                                    text=f"{config.COLUMN_HEADERS[config.COLUMN_ID]} {config.SORT_DESC_ICON}")
        self.tree_processes.heading(column=config.COLUMN_PROCESS_NAME,
                                    text=config.COLUMN_HEADERS[config.COLUMN_PROCESS_NAME])
        self.tree_processes.heading(column=config.COLUMN_STATUS,
                                    text=config.COLUMN_HEADERS[config.COLUMN_STATUS])
        self.tree_processes.heading(column=config.COLUMN_LOCATION,
                                    text=config.COLUMN_HEADERS[config.COLUMN_LOCATION])

    def on_window_resize(self, event):
        """Función que se ejecuta cuando la ventana cambia de tamaño"""
        global resize_timer

        # Si ya hay un temporizador en marcha, cancelarlo
        if resize_timer:
            root.after_cancel(resize_timer)

        # Programar la ejecución de auto_adjust_columns después de 200 ms
        resize_timer = root.after(200, self.auto_adjust_columns)


if __name__ == "__main__":
    root = tk.Tk()
    pm = ProcessManager(root=root)
    pm.start()
