import tkinter as tk
from tkinter import ttk, font
import config, pmcore # custom libs
import os
import subprocess
import pyperclip

config.adjust_dpi()

resize_timer = None


def refresh_window(window: tk.Tk, sleep: int = 1000):
    """Fuerza la actualización del marco superior"""
    window.update_idletasks()
    window.withdraw()
    window.after(sleep, window.deiconify)


def center_window_on_screen(window: tk.Tk):
    """Establece la posición de la ventana en el centro de la pantalla"""
    window.update_idletasks()
    width_wnd = window.winfo_width()
    height_wnd = window.winfo_height()
    width_screen = window.winfo_screenwidth()
    height_screen = window.winfo_screenheight()
    x = (width_screen // 2) - (width_wnd // 2)
    y = (height_screen // 2) - (height_wnd // 2)
    window.geometry(f"+{x}+{y}")


class ProcessManager:
    def __init__(self, root: tk.Tk):
        self._pid = os.getpid()
        self._root = root
        self._style = ttk.Style(self._root)

        # Main window ---------------------------------
        self._root.title(f"{config.APP_TITLE} [PID: {self._pid}]")
        self._root.geometry(config.WINDOW_SIZE)
        self._root.withdraw()
        self._root.iconbitmap(config.APP_ICON)
        self._root.bind("<Configure>", self._on_window_resize)

        self._frm_main = tk.Frame(self._root)
        self._frm_main.pack(expand=True, fill="both")
        self._frm_main.propagate(False)

        # Styles ---------------------------------
        self._style = ttk.Style(self._root)
        self._style.element_create(
            "Custom.Treeheading.border", "from", "default")
        self._style.layout("Custom.Treeview.Heading", [
            ("Custom.Treeheading.cell", {'sticky': 'nswe'}),
            ("Custom.Treeheading.border", {'sticky': 'nswe', 'children': [
                ("Custom.Treeheading.padding", {'sticky': 'nswe', 'children': [
                    ("Custom.Treeheading.image", {
                     'side': 'right', 'sticky': ''}),
                    ("Custom.Treeheading.text", {'sticky': 'we'})
                ]})
            ]}),
        ])
        self._style.configure("Custom.Treeview", borderwidth=0, relief="flat")

        self._tree_processes = ttk.Treeview(self._frm_main,
                                           columns=(config.COLUMN_ID, config.COLUMN_PROCESS_NAME,
                                                    config.COLUMN_STATUS, config.COLUMN_LOCATION),
                                           show="headings",
                                           style="Custom.Treeview")
        self._tree_processes.heading(
            config.COLUMN_ID, text=config.COLUMN_HEADERS[config.COLUMN_ID], anchor='w', command=lambda: self._sort_column(config.COLUMN_ID))
        self._tree_processes.heading(config.COLUMN_PROCESS_NAME,
                                    text=config.COLUMN_HEADERS[config.COLUMN_PROCESS_NAME], anchor='w', command=lambda: self._sort_column(config.COLUMN_PROCESS_NAME))
        self._tree_processes.heading(
            config.COLUMN_STATUS, text=config.COLUMN_HEADERS[config.COLUMN_STATUS], anchor='w', command=lambda: self._sort_column(config.COLUMN_STATUS))
        self._tree_processes.heading(config.COLUMN_LOCATION,
                                    text=config.COLUMN_HEADERS[config.COLUMN_LOCATION], anchor='w', command=lambda: self._sort_column(config.COLUMN_LOCATION))
        self._tree_processes.column(config.COLUMN_ID, width=5,
                                   anchor="w", minwidth=75, stretch=True)
        self._tree_processes.column(config.COLUMN_PROCESS_NAME, width=20,
                                   anchor="w", minwidth=180, stretch=True)
        self._tree_processes.column(config.COLUMN_STATUS, width=10,
                                   anchor="w", minwidth=100, stretch=True)
        self._tree_processes.column(config.COLUMN_LOCATION, width=150,
                                   anchor="w", minwidth=150, stretch=True)

        self._scb_tree = tk.Scrollbar(self._frm_main, orient="vertical",
                                     command=self._tree_processes.yview)
        self._scb_tree.pack(side="right", fill="y")

        # Scrollbar Y
        self._tree_processes.config(yscrollcommand=self._scb_tree.set)
        self._tree_processes.pack(expand=True, fill="both")

        # Menú contextual
        self._context_menu = tk.Menu(self._root, tearoff=0)
        self._context_menu.add_command(
            label=config.MENU_CONTEXT[config.MENU_OPT_COPY_TO_CLIPBOARD], command=self._copy_content_to_clipboard)
        self._context_menu.add_command(
            label=config.MENU_CONTEXT[config.MENU_OPT_OPEN_LOCATION_PROCESS], command=self._open_location_process)

        self._tree_processes.bind("<Button-3>", self._show_context_menu)

        # Config window ---------------------------------
        self._popup = None
        self._frm_checks = None
        self._check_flag_adjust_cols = None
        self._chk_flag_change_theme = None
        self._btn_close = None

        self._flag_adjust_cols = tk.BooleanVar(value=True)
        self._flag_change_theme = tk.BooleanVar(value=False)

        self._order_asc = {config.COLUMN_ID: False, config.COLUMN_PROCESS_NAME: True,
                                 config.COLUMN_STATUS: True, config.COLUMN_LOCATION: True}
        self._process_list = []

        # self.root.bind("<Configure>", self.on_window_resize)

        # Controls group ---------------------------------
        self._frm_bottom_bar = tk.Frame(self._root)
        self._frm_bottom_bar.pack(pady=10, fill="x")

        self._inp_search = tk.Entry(self._frm_bottom_bar, width=30)
        self._inp_search.pack(side="left", padx=5, ipady=6)
        self._inp_search.bind('<Return>', lambda event: self._filter_process_list())

        self._btn_buscar = tk.Button(
            self._frm_bottom_bar, text=config.BOTTOM_FRAME[config.BUTTON_SEARCH], command=self._filter_process_list)
        self._btn_buscar.pack(side="left", padx=5, ipadx=20)

        self._btn_update = tk.Button(
            self._frm_bottom_bar, text=config.BOTTOM_FRAME[config.BUTTON_UPDATE], command=self._update_process_list)
        self._btn_update.pack(side="left", padx=2, ipadx=15)

        self._btn_settings = tk.Button(
            self._frm_bottom_bar, text=config.BOTTOM_FRAME[config.BUTTON_SETTINGS], command=self._show_window_settings)
        self._btn_settings.pack(side="left", padx=5, ipadx=10)

        self._lbl_total = tk.Label(
            self._frm_bottom_bar, text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: 0")
        self._lbl_total.pack(side="left", padx=5)

        self._theme = None
        self._apply_theme(config.LIGHT_THEME)

        self._update_process_list()

    def _create_window_settings(self):
        self._popup = tk.Toplevel(self._root)
        self._popup.title(
            config.SETTINGS_OPTIONS[config.TITLE_WND_SETTINGS])
        self._popup.geometry(
            config.SETTINGS_OPTIONS[config.SIZE_WND_SETTINGS])
        self._popup.resizable(False, False)
        self._popup.attributes("-toolwindow", True)

        # Hacer la ventana tipo modal
        self._popup.grab_set()  # Bloquea la interacción con otras ventanas
        self._popup.transient(self._root)  # Asocia la ventana modal con la ventana principal

        # Bottom panel ---------------------------------
        self._frm_checks = tk.Frame(self._popup)
        self._frm_checks.pack(padx=10, pady=10, anchor="w")

        self._check_flag_adjust_cols = tk.Checkbutton(
            self._frm_checks, text=config.SETTINGS_OPTIONS[config.CHECKBOX_ADJUST_AUTOMATIC_COLS], variable=self._flag_adjust_cols)
        self._check_flag_adjust_cols.pack(anchor="w")

        self._chk_flag_change_theme = tk.Checkbutton(
            self._frm_checks, text=config.SETTINGS_OPTIONS[config.CHECKBOX_DARK_THEME], variable=self._flag_change_theme, command=self._toggle_theme)
        self._chk_flag_change_theme.pack(anchor="w")

        self._btn_close = tk.Button(
            self._popup, text=config.SETTINGS_OPTIONS[config.BUTTON_CLOSE_SETTINGS], command=self._close_window_settings)
        self._btn_close.pack(pady=10, ipadx=35)

    def _close_window_settings(self):
        """Cierra la ventana de configuración y libera el foco"""
        if self._popup and self._popup.winfo_exists():
            self._popup.grab_release()  # Libera el foco
            self._popup.destroy()

    def _open_window_settings(self, already_exists=True):
        """Abre la ventana de configuración"""
        if not already_exists:
            self._popup.withdraw()
            center_window_on_screen(self._popup)
            self._popup.deiconify()
        else:
            self._popup.deiconify()

    def _show_window_settings(self):
        """Muestra la ventana de configuración"""
        if self._popup is None or not self._popup.winfo_exists():
            self._create_window_settings()

            # Ocultar temporalmente y mostrar recién cuando esté centrada
            self._open_window_settings(False)
        else:
            self._open_window_settings()

        self._apply_theme(self._theme)

    def _apply_theme(self, theme):
        """Aplica el tema indicado a la interfaz gráfica de todas las ventanas y controles del programa"""
        self._theme = theme

        config.set_bg_color_title_bar(self._root, color=self._theme["name"])
        
        # Configuracion de colores para widgets de ttk
        self._root.config(bg=self._theme["bg2"])
        self._frm_main.config(bg=self._theme["frame_bg"])
        self._frm_bottom_bar.config(bg=self._theme["frame_bg"])
        self._lbl_total.config(
            bg=self._theme["label_bg"], fg=self._theme["label_fg"])
        self._inp_search.config(bg=self._theme["entry_bg"], fg=self._theme["entry_fg"],
                               insertbackground=self._theme["entry_insertbackground"])
        self._btn_buscar.config(bg=self._theme["button_bg"], fg=self._theme["button_fg"],
                               activebackground=self._theme["button_activebackground"], activeforeground=self._theme["button_activeforeground"])
        self._btn_settings.config(bg=self._theme["button_bg"], fg=self._theme["button_fg"],
                                 activebackground=self._theme["button_activebackground"], activeforeground=self._theme["button_activeforeground"])
        self._btn_update.config(bg=self._theme["button_bg"], fg=self._theme["button_fg"],
                               activebackground=self._theme["button_activebackground"], activeforeground=self._theme["button_activeforeground"])
        
        if self._popup != None:
            config.set_bg_color_title_bar(self._popup, color=self._theme["name"])
            self._popup.config(bg=self._theme["bg2"])
        if self._frm_checks != None:
            self._frm_checks.config(bg=self._theme["bg2"])
        if self._btn_close != None:
            self._btn_close.config(bg=self._theme["button_bg"], fg=self._theme["button_fg"],
                                  activebackground=self._theme["button_activebackground"], activeforeground=self._theme["button_activeforeground"])
        if self._check_flag_adjust_cols != None:
            self._check_flag_adjust_cols.config(bg=self._theme["checkbox_bg"], fg=self._theme["checkbox_fg"],
                                             selectcolor=self._theme["checkbox_selectcolor"], activebackground=self._theme[
                                                 "checkbox_activebackground"],
                                             activeforeground=self._theme["checkbox_activeforeground"])
        if self._chk_flag_change_theme != None:
            self._chk_flag_change_theme.config(bg=self._theme["checkbox_bg"], fg=self._theme["checkbox_fg"],
                                              selectcolor=self._theme["checkbox_selectcolor"], activebackground=self._theme[
                                                  "checkbox_activebackground"],
                                              activeforeground=self._theme["checkbox_activeforeground"])

        # Configuración de colores segun en eventos de widgets de ttk
        self._style.theme_use("clam")  # alt | classic
        self._style.map("Treeview.Heading",
                       background=[("active", config.COLOR_SKYBLUE0),
                                   # fondo cabecera
                                   ("!active", config.COLOR_SKYBLUE1)],
                       foreground=[("active", config.COLOR_WHITE0),
                                   # texto cabecera
                                   ("!active", config.COLOR_WHITE0)],
                       relief="flat")
        self._style.map("Custom.Treeview",
                       background=[("selected", self._theme["treeview_background_selected"]),
                                   # -> style.configure(background=theme["bg"])
                                   ("!selected", self._theme["treeview_background_!selected"])],
                       foreground=[("selected", self._theme["treeview_foreground_selected"]),
                                   # -> style.configure(foreground=theme["fg"])
                                   ("!selected", self._theme["treeview_foreground_!selected"])],
                       # style.configure(fieldbackground=theme["bg"])
                       fieldbackground=self._theme["bg"])
        
        # Menú contextual ---------------------------------
        self._context_menu.configure(bg=theme["bg2"], fg=theme["fg"])

    def _toggle_theme(self):
        """Alterna entre el tema claro y oscuro y luego reinicia la aplicación"""
        if self._theme == config.LIGHT_THEME:
            self._apply_theme(config.DARK_THEME)
        else:
            self._apply_theme(config.LIGHT_THEME)

        # TODO Posicion de ventanas
        # Se pierde la ultima posicion de la ventana y es algo incomo que se recupere en la posicion y tamaño original
        # TODO Marco de ventana popup
        # Si se cierra la ventana popup y luego se abre en modo oscuro el marco superior no se pinta correctamente
        # refresh_window(self._root, sleep=1200)
        # refresh_window(self._popup, sleep=1800)

    def _sort_column(self, column):
        data = [(self._tree_processes.item(row)["values"][0], self._tree_processes.item(row)["values"][1], self._tree_processes.item(
            row)["values"][2], self._tree_processes.item(row)["values"][3]) for row in self._tree_processes.get_children()]

        if column == config.COLUMN_ID:
            data.sort(key=lambda x: int(
                x[0]), reverse=not self._order_asc[config.COLUMN_ID])
            self._order_asc[config.COLUMN_ID] = not self._order_asc[config.COLUMN_ID]
        elif column == config.COLUMN_PROCESS_NAME:
            data.sort(key=lambda x: x[1].lower(
            ), reverse=not self._order_asc[config.COLUMN_PROCESS_NAME])
            self._order_asc[config.COLUMN_PROCESS_NAME] = not self._order_asc[config.COLUMN_PROCESS_NAME]
        elif column == config.COLUMN_STATUS:
            data.sort(key=lambda x: x[2].lower(
            ), reverse=not self._order_asc[config.COLUMN_STATUS])
            self._order_asc[config.COLUMN_STATUS] = not self._order_asc[config.COLUMN_STATUS]
        elif column == config.COLUMN_LOCATION:
            data.sort(key=lambda x: x[3].lower(
            ), reverse=not self._order_asc[config.COLUMN_LOCATION])
            self._order_asc[config.COLUMN_LOCATION] = not self._order_asc[config.COLUMN_LOCATION]

        for row in self._tree_processes.get_children():
            self._tree_processes.delete(row)

        for pid, name, status, location in data:
            self._tree_processes.insert(
                "", "end", values=(pid, name, status, location))

        column_headers = [config.COLUMN_ID, config.COLUMN_PROCESS_NAME,
                          config.COLUMN_STATUS, config.COLUMN_LOCATION]

        for col in column_headers:
            if col == column:
                symbol = config.SORT_ASC_ICON if self._order_asc[col] else config.SORT_DESC_ICON
            else:
                symbol = ""
            text = config.COLUMN_HEADERS[config.COLUMN_ID] if col == config.COLUMN_ID else config.COLUMN_HEADERS[config.COLUMN_PROCESS_NAME] if col == config.COLUMN_PROCESS_NAME else config.COLUMN_HEADERS[
                config.COLUMN_STATUS] if col == config.COLUMN_STATUS else config.COLUMN_HEADERS[config.COLUMN_LOCATION]
            self._tree_processes.heading(col, text=f"{text} {symbol}")

    def _auto_adjust_columns(self):
        """Ajusta automáticamente el ancho de las columnas al mínimo necesario, respetando minwidth"""
        if self._flag_adjust_cols.get():  # Solo ajustar si el checkbox está marcado

            self._tree_processes.update_idletasks()  # Actualizar la geometría de la tabla
            for col in self._tree_processes["columns"]:

                min_width = int(self._tree_processes.column(
                    col, option="minwidth"))

                visible_rows = self._tree_processes.get_children()

                # Calcular el ancho máximo de la columna basado en el contenido de las celdas visibles
                # TODO Corregido parcialmente
                # Cuando no hay resultados al filtrar no debería reajustar las columnas porque la experiencia
                # de usuario se siente rara.
                max_width = max(
                    [font.Font().measure(str(self._tree_processes.set(row, col)))  # Medir el ancho del texto
                     # Iterar solo sobre las filas visibles
                     for row in visible_rows]
                    or
                    [min_width]
                )

                # Asegurarse de que el ancho no sea menor que minwidth
                adjusted_width = max(max_width + 10, min_width)

                self._tree_processes.column(col, width=adjusted_width)

    def _filter_process_list(self):
        text = self._inp_search.get().strip().lower()

        for process in self._tree_processes.get_children():
            self._tree_processes.delete(process)

        if text == "":
            filtered_data = self._process_list
        else:
            filtered_data = [(pid, name, status, location) for pid, name,
                             status, location in self._process_list if text in name.lower()]

        for pid, name, status, location in filtered_data:
            self._tree_processes.insert(
                "", tk.END, values=(pid, name, status, location))

        self._lbl_total.config(
            text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: {len(filtered_data)}")

    def _update_process_list(self):
        # TODO refactorizar este metodo
        """Actualiza la lista de procesos"""
        for process in self._tree_processes.get_children():
            self._tree_processes.delete(process)

        self._process_list.clear()
        # for process in psutil.process_iter(attrs=['pid', 'name', 'status']):
        #     pid = None
        #     name = None
        #     status = None
        #     location = None
        #     try:
        #         pid = process.info['pid']
        #         name = process.info['name']
        #         status = process.info['status']
        #         location = psutil.Process(pid).exe()
        #     except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        #         print(
        #             f"> ERROR: Error al ejecutar psutil.process_iter en 'update_process_list'. pid:{pid}")
        #         pid = process.info['pid']
        #         name = process.info['name']
        #         status = "N/A"
        #         location = "N/A"

        #     self._process_list.append(
        #         (pid, name or "-", status, location or "-"))

        # for pid, name, status, location in self._process_list:
        #     self._tree_processes.insert("", tk.END, values=(pid, name, status, location))

        # NOTE Refactorización parcial, hasta implementar una version estable de 'pmcore'
        # se va a dejar la implementacion anterior. Ahora usa el nivel mas rapido para 
        # obtener los procesos.
        process_list = pmcore.get_process_list(pmcore.OPTIMIZED_LEVEL_2)

        for process in process_list:
            self._process_list.\
                append((
                    process[pmcore.COL_PID],
                    process[pmcore.COL_NAME],
                    process[pmcore.COL_STATUS],
                    process[pmcore.COL_EXE]
                ))
            self._tree_processes.\
                insert("", "end",
                       values=(process[pmcore.COL_PID],
                               process[pmcore.COL_NAME],
                               process[pmcore.COL_STATUS],
                               process[pmcore.COL_EXE]))

        self._lbl_total.config(
            text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: {len(self._process_list)}")

        # Lista ordenada por defecto por 'ID'
        self._tree_processes.heading(column=config.COLUMN_ID,
                                    text=f"{config.COLUMN_HEADERS[config.COLUMN_ID]} {config.SORT_DESC_ICON}")

    def _on_window_resize(self, event):
        """Se ejecuta cuando la ventana cambia de tamaño"""
        global resize_timer

        # Si ya hay un temporizador en marcha, cancelarlo
        if resize_timer:
            self._root.after_cancel(resize_timer)

        resize_timer = self._root.after(200, self._auto_adjust_columns)

    def _show_context_menu(self, event):
        """Muestra el menú contextual al hacer clic derecho."""
        item = self._tree_processes.identify_row(event.y)
        if item:
            self._tree_processes.selection_set(item)
            self._context_menu.post(event.x_root, event.y_root)

    def _copy_content_to_clipboard(self):
        selected = self._tree_processes.selection()
        if not selected:
            return

        pid = self._tree_processes.item(selected[0], "values")[0]
        name = self._tree_processes.item(selected[0], "values")[1]
        status = self._tree_processes.item(selected[0], "values")[2]
        exe = self._tree_processes.item(selected[0], "values")[3]  # path

        pyperclip.copy(f"{pid}\t{name}\t{status}\t{exe}")
        print(f"> Acción: Se copio el contenido de la fila al portapapeles")

    # def _kill_process(self):
    #     """Finaliza el proceso seleccionado."""
    #     selected = self._tree_processes.selection()
    #     if not selected:
    #         return

    #     pid = self._tree_processes.item(selected[0], "values")[0]

    #     result = pmcore.kill_process(int(pid))
    #     if result != None:
    #         print(f"> Salida: {result}")
    #         self._update_process_list()

    def _open_location_process(self):
        selected = self._tree_processes.selection()
        if not selected:
            return

        exe = self._tree_processes.item(selected[0], "values")[3]
        path = os.path.realpath(exe)

        if not os.path.exists(path):
            print(f"Archivo no encontrado: {path}")
            return

        try:
            subprocess.run(["explorer", "/select,", path], check=True)
        except Exception as e:
            # print(f"> Advertencia: La ruta '{e}' se encuentra en una carpeta privada del sistema")
            print(
                f"> Advertencia: La ruta '{path}' se encuentra en una carpeta privada del sistema")

    def start(self):
        """Inicia la aplicación"""
        center_window_on_screen(self._root)
        self._root.deiconify()
        self._root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    pm = ProcessManager(root=root)
    pm.start()
