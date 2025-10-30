import tkinter as tk
from tkinter import ttk, font
from core import Constants, get_process_list, get_datetime
import os
import subprocess
import pyperclip
from config import \
    MainResources, SettingsResources, ThemesResources, IconResources, \
    resource_path, set_bg_color_title_bar
import webbrowser

resize_timer = None

# @DEPRECATED
# def refresh_window(window: tk.Tk, sleep: int = 1000):
#     """Fuerza la actualización del marco superior"""
#     window.update_idletasks()
#     window.withdraw()
#     window.after(sleep, window.deiconify)


class ProcessManager:
    def __init__(self, window: tk.Tk):
        # Ventana principal ---------------------------------
        self._window = window
        self._pid = None
        self._style = None
        self._fra_main = None
        self._tree_processes = None
        self._scb_y_tree = None
        self._context_menu = None
        self._frm_bottom_bar = None
        self._inp_search = None
        self._btn_buscar = None
        self._btn_update = None
        self._btn_settings = None
        self._lbl_total = None
        self._create_main_window()

        # Ventana de configuración ---------------------------------
        self._wnd_settings = None
        self._frm_checks = None
        self._chk_adjust_cols = None
        self._chk_dark_theme = None
        self._btn_close = None
        self._flag_adjust_cols = tk.BooleanVar(value=True)
        self._flag_dark_theme = tk.BooleanVar(value=False)

        # Ventana acerca de ---------------------------------
        self._wnd_about = None
        self._lnk_repository = None
        self._lbl_title_about = None
        self._lbl_content_about = None
        self._btn_close_about = None

        # Otros ---------------------------------
        self._flag_fullscreen = tk.BooleanVar(value=False)
        self._create_menubar()

        # dict que se utiliza para indicar el orden de las columnas en '_sort_column'
        self._order_asc = {
            MainResources.ID_COLUMN_PID: False,
            MainResources.ID_COLUMN_PROCESS_NAME: True,
            MainResources.ID_COLUMN_STATUS: True,
            MainResources.ID_COLUMN_LOCATION: True
        }
        self._process_list = []
        self._update_process_list()

        self._theme = None
        self._apply_theme(ThemesResources.LIGHT_THEME)

    def _get_process_id(self):
        return os.getpid()

    def _create_main_window(self):
        """Crea la ventana principal del programa"""
        self._pid = self._get_process_id()
        self._style = ttk.Style(self._window)

        # Ventana principal ---------------------------------
        self._window.title(f"{MainResources.TITLE} v{MainResources.VERSION} [PID: {self._pid}]")
        self._window.geometry(MainResources.SIZE)
        self._window.withdraw()
        self._window.iconbitmap(resource_path(IconResources.APP_ICON))
        self._window.bind("<Configure>", self._on_window_resize)

        self._fra_main = tk.Frame(self._window)
        self._fra_main.pack(expand=True, fill="both")
        self._fra_main.propagate(False)

        # Estilos ---------------------------------
        self._style = ttk.Style(self._window)
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

        self._tree_processes = ttk.Treeview(self._fra_main,
                                            columns=(MainResources.ID_COLUMN_PID,
                                                     MainResources.ID_COLUMN_PROCESS_NAME,
                                                     MainResources.ID_COLUMN_STATUS,
                                                     MainResources.ID_COLUMN_LOCATION),
                                            show="headings",
                                            style="Custom.Treeview")
        self._tree_processes.heading(
            MainResources.ID_COLUMN_PID, text=MainResources.TEXT_COLUMN_PID, anchor='w', command=lambda: self._sort_column(MainResources.ID_COLUMN_PID))
        self._tree_processes.heading(
            MainResources.ID_COLUMN_PROCESS_NAME, text=MainResources.TEXT_COLUMN_PROCESS_NAME, anchor='w', command=lambda: self._sort_column(MainResources.ID_COLUMN_PROCESS_NAME))
        self._tree_processes.heading(
            MainResources.ID_COLUMN_STATUS, text=MainResources.TEXT_COLUMN_STATUS, anchor='w', command=lambda: self._sort_column(MainResources.ID_COLUMN_STATUS))
        self._tree_processes.heading(
            MainResources.ID_COLUMN_LOCATION, text=MainResources.TEXT_COLUMN_LOCATION, anchor='w', command=lambda: self._sort_column(MainResources.ID_COLUMN_LOCATION))

        self._tree_processes.column(
            MainResources.ID_COLUMN_PID, width=5, anchor="w", minwidth=75, stretch=True)
        self._tree_processes.column(
            MainResources.ID_COLUMN_PROCESS_NAME, width=20, anchor="w", minwidth=180, stretch=True)
        self._tree_processes.column(
            MainResources.ID_COLUMN_STATUS, width=10, anchor="w", minwidth=100, stretch=True)
        self._tree_processes.column(
            MainResources.ID_COLUMN_LOCATION, width=150, anchor="w", minwidth=150, stretch=True)

        self._scb_y_tree = tk.Scrollbar(self._fra_main, orient="vertical", command=self._tree_processes.yview)
        self._scb_y_tree.pack(side="right", fill="y")

        # Scrollbar Y
        self._tree_processes.config(yscrollcommand=self._scb_y_tree.set)
        self._tree_processes.pack(expand=True, fill="both")

        # Menú contextual
        self._context_menu = tk.Menu(self._window, tearoff=0)
        self._context_menu.add_command(label=MainResources.TEXT_COPY_TO_CLIPBOARD, command=self._copy_content_to_clipboard)
        self._context_menu.add_command(label=MainResources.TEXT_OPEN_LOCATION_PROCESS, command=self._open_location_process)
        self._context_menu.add_command(label=MainResources.TEXT_PROPERTIES, command=self._show_properties_of_file)

        self._tree_processes.bind("<Button-3>", self._show_context_menu)

        # self.root.bind("<Configure>", self.on_window_resize)

        # Grupo de controles ---------------------------------
        self._frm_bottom_bar = tk.Frame(self._window)
        self._frm_bottom_bar.pack(pady=10, fill="x")

        self._inp_search = tk.Entry(self._frm_bottom_bar, width=30)
        self._inp_search.pack(side="left", padx=5, ipady=6)
        self._inp_search.bind('<Return>', lambda event: self._filter_process_list())

        self._btn_buscar = tk.Button(self._frm_bottom_bar, text=MainResources.TEXT_SEARCH, command=self._filter_process_list)
        self._btn_buscar.pack(side="left", padx=5, ipadx=20)

        self._btn_update = tk.Button(self._frm_bottom_bar, text=MainResources.TEXT_UPDATE, command=self._update_process_list)
        self._btn_update.pack(side="left", padx=2, ipadx=15)

        self._btn_settings = tk.Button(self._frm_bottom_bar, text=MainResources.TEXT_SETTINGS, command=self._show_settings_window)
        self._btn_settings.pack(side="left", padx=5, ipadx=10)

        self._lbl_total = tk.Label(self._frm_bottom_bar, text=f"{MainResources.TEXT_TOTAL}: 0")
        self._lbl_total.pack(side="left", padx=5)

    def _close_main_window(self):
        self._window.destroy()

    def _create_menubar(self):
        """Crea la barra de menú principal de la aplicación """
        menu_bar = tk.Menu(self._window)

        menu_dropdown_file = tk.Menu(menu_bar, tearoff=False)
        menu_dropdown_file.add_command(
            label="Actualizar lista de procesos", accelerator="Ctrl+R", command=self._update_process_list
        )
        menu_dropdown_file.add_command(
            label="Salir", accelerator="Ctrl+E", command=self._close_main_window
        )
        menu_dropdown_config = tk.Menu(menu_bar, tearoff=False)
        menu_dropdown_config.add_command(
            label="Ajustes", accelerator="Ctrl+S", command=self._show_settings_window
        )
        menu_dropdown_view = tk.Menu(menu_bar, tearoff=False)
        menu_dropdown_view.add_checkbutton(
            label="Pantalla completa",
            accelerator="F11",
            variable=self._flag_fullscreen,
            command=self._toggle_fullscreen
        )
        menu_dropdown_config.add_checkbutton(
            label=SettingsResources.TEXT_ENABLE_DARK_THEME,
            accelerator="Ctrl+T",
            variable=self._flag_dark_theme,
            command=self._toggle_theme
        )
        menu_dropdown_help = tk.Menu(menu_bar, tearoff=False)
        menu_dropdown_help.add_command(
            label=f"Acerca de {MainResources.TITLE}...", command=self._show_about_window
        )
        menu_bar.add_cascade(menu=menu_dropdown_file, label="Archivo")
        menu_bar.add_cascade(menu=menu_dropdown_view, label="Ver")
        menu_bar.add_cascade(menu=menu_dropdown_config, label="Configuración")
        menu_bar.add_cascade(menu=menu_dropdown_help, label="Ayuda")

        self._window.config(menu=menu_bar)

        # enlazo atajo de tecla a eventos
        self._window.bind_all("<Control-e>", lambda event: self._close_main_window())
        self._window.bind_all("<Control-s>", lambda event: self._show_settings_window())
        self._window.bind_all("<Control-r>", lambda event: self._update_process_list())
        self._window.bind_all("<Control-t>", lambda event: self._flag_dark_theme.set(not self._flag_dark_theme.get()) or self._toggle_theme())
        self._window.bind_all("<F11>", lambda event: self._flag_fullscreen.set(not self._flag_fullscreen.get()) or self._toggle_fullscreen())

    def _toggle_fullscreen(self):
        """ Ajusta la aplicación a pantalla completa """
        is_fullscreen = self._window.attributes("-fullscreen")
        self._window.attributes("-fullscreen", not is_fullscreen)

    def _create_about_window(self):
        self._wnd_about = tk.Toplevel(self._window, padx=20, pady=20)
        self._wnd_about.title("Acerca de")
        # Ventana tipo popup
        self._wnd_about.resizable(False, False)
        self._wnd_about.attributes("-toolwindow", True)
        # Hacer la ventana tipo modal
        self._wnd_about.grab_set()
        self._wnd_about.transient(self._window)

        # self._top_about.configure()
        # Contenido
        content_about = f"Versión: {MainResources.VERSION}\nFecha: 13-Abr-25\nAutor: Manuel C.\nLicencia: MIT\n"
        # title_font = font.Font(family="Microsoft Tai Le", size=13) # opc1 similar a Microsoft Sans Serif
        # title_font = font.Font(family="Corbel", size=15) # opc2
        # title_font = font.Font(family="Segoe UI Light", size=20, weight="bold")  # opc3
        font_title = font.Font(family="Segoe UI", size=11, weight="bold")
        font_link = font.Font(underline=True, family="Segoe UI", size=9)

        # titulo
        self._lbl_title_about = tk.Label(
            self._wnd_about, text=f"{MainResources.TITLE}", 
            font=font_title, justify="left", anchor="w", width=27
        )
        self._lbl_title_about.pack()

        # contenido
        self._lbl_content_about = tk.Label(
            self._wnd_about, text=content_about, 
            justify="left", anchor="w", width=37
        )
        self._lbl_content_about.pack(pady=(10, 0))

        # link repo app
        self._lbl_repo_app = tk.Label(
            self._wnd_about, text="ir al repositorio de la aplicación", 
            font=font_link, cursor="hand2", justify="left", 
            anchor="w", width=37
        )
        self._lbl_repo_app.bind("<Button-1>", lambda event: self._open_link("https://github.com/manuel-chinchi/process-manager-py")) # evento click
        self._lbl_repo_app.pack(pady=(0, 50))

        # boton de cierre
        self._btn_close_about = tk.Button(
            self._wnd_about, text="Aceptar", 
            command=self._close_about_window, padx=25
        )
        self._btn_close_about.pack()

    def _show_about_window(self):
        """ Muestra la ventana 'Acerca de' """
        if self._wnd_about is None or not self._wnd_about.winfo_exists():
            self._create_about_window()

            self._open_about_window(False)
        else:
            self._open_about_window()

        self._apply_theme(self._theme)

    def _open_about_window(self, already_exists=False):
        if not already_exists:
            self._wnd_about.withdraw()
            self._center_window_on_screen(self._wnd_about)
            self._wnd_about.deiconify()
        else:
            self._wnd_about.deiconify()

    def _close_about_window(self):
        self._wnd_about.destroy()

    def _create_settings_window(self):
        """Crea la ventana de configuración"""
        self._wnd_settings = tk.Toplevel(self._window)
        self._wnd_settings.title(SettingsResources.TITLE)
        self._wnd_settings.geometry(SettingsResources.SIZE)
        self._wnd_settings.resizable(False, False)
        self._wnd_settings.attributes("-toolwindow", True)

        # Hacer la ventana tipo modal
        self._wnd_settings.grab_set()  # Bloquea la interacción con otras ventanas
        self._wnd_settings.transient(self._window)  # Asocia la ventana modal con la ventana principal

        # Panel de botones ---------------------------------
        self._frm_checks = tk.Frame(self._wnd_settings)
        self._frm_checks.pack(padx=10, pady=10, anchor="w")

        self._chk_adjust_cols = tk.Checkbutton(
            self._frm_checks, text=SettingsResources.TEXT_ADJUST_WIDTH_COLS, 
            variable=self._flag_adjust_cols)
        self._chk_adjust_cols.pack(anchor="w")

        self._chk_dark_theme = tk.Checkbutton(
            self._frm_checks, text=SettingsResources.TEXT_ENABLE_DARK_THEME, 
            variable=self._flag_dark_theme, command=self._toggle_theme)
        self._chk_dark_theme.pack(anchor="w")

        self._btn_close = tk.Button(
            self._wnd_settings, text=SettingsResources.TEXT_CLOSE, 
            command=self._close_settings_window)
        self._btn_close.pack(pady=10, ipadx=35)

    def _close_settings_window(self):
        """Cierra la ventana de configuración liberando el foco"""
        if self._wnd_settings and self._wnd_settings.winfo_exists():
            self._wnd_settings.grab_release()  # Libera el foco
            self._wnd_settings.destroy()

    def _open_settings_window(self, already_exists=True):
        """Abre la ventana de configuración"""
        if not already_exists:
            self._wnd_settings.withdraw()
            self._center_window_on_screen(self._wnd_settings)
            self._wnd_settings.deiconify()
        else:
            self._wnd_settings.deiconify()

    def _show_settings_window(self):
        """Muestra la ventana de configuración"""
        if self._wnd_settings is None or not self._wnd_settings.winfo_exists():
            self._create_settings_window()

            # Ocultar temporalmente y mostrar recién cuando esté centrada
            self._open_settings_window(False)
        else:
            self._open_settings_window()

        self._apply_theme(self._theme)

    def _apply_theme(self, theme):
        """Aplica el tema indicado a la interfaz gráfica de todas las ventanas y controles del programa"""
        self._theme = theme

        set_bg_color_title_bar(self._window, color=self._theme["name"])
        
        # Configuracion de colores para widgets de ttk
        self._window.config(bg=self._theme["bg2"])
        self._fra_main.config(bg=self._theme["frame_bg"])
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
        
        if self._wnd_settings != None and self._wnd_settings.winfo_exists():
            set_bg_color_title_bar(self._wnd_settings, color=self._theme["name"])
            self._wnd_settings.config(bg=self._theme["bg2"])
            self._frm_checks.config(bg=self._theme["bg2"])
            self._btn_close.config(bg=self._theme["button_bg"], fg=self._theme["button_fg"],
                                    activebackground=self._theme["button_activebackground"], activeforeground=self._theme["button_activeforeground"])
            self._chk_adjust_cols.config(bg=self._theme["checkbox_bg"], fg=self._theme["checkbox_fg"],
                                                selectcolor=self._theme["checkbox_selectcolor"], activebackground=self._theme[
                                                    "checkbox_activebackground"],
                                                activeforeground=self._theme["checkbox_activeforeground"])
            self._chk_dark_theme.config(bg=self._theme["checkbox_bg"], fg=self._theme["checkbox_fg"],
                                                selectcolor=self._theme["checkbox_selectcolor"], activebackground=self._theme[
                                                    "checkbox_activebackground"],
                                                activeforeground=self._theme["checkbox_activeforeground"])

        # Configuración de colores según eventos de widgets de ttk
        self._style.theme_use("clam")  # alt | classic
        self._style.map("Treeview.Heading",
                       background=[("active", ThemesResources.COLOR_SKYBLUE0),
                                   # fondo cabecera
                                   ("!active", ThemesResources.COLOR_SKYBLUE1)],
                       foreground=[("active", ThemesResources.COLOR_WHITE0),
                                   # texto cabecera
                                   ("!active", ThemesResources.COLOR_WHITE0)],
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

        # if self._top_about != None:
        #     print(f"---cambiar tema en ABOUT")
        #     set_bg_color_title_bar(self._top_about, color=self._theme["name"])
        #     self._top_about.config(bg=self._theme["bg2"])
        if self._wnd_about != None and self._wnd_about.winfo_exists():
            set_bg_color_title_bar(self._wnd_about, color=self._theme["name"])
            self._wnd_about.config(bg=self._theme["bg2"])
            self._lbl_title_about.config(bg=self._theme["bg2"], fg=self._theme["label_fg"])
            self._lbl_content_about.config(bg=self._theme["bg2"], fg=self._theme["label_fg"])
            self._lbl_repo_app.config(bg=self._theme["bg2"], fg=self._theme["label_fg_hyperlink"])
            self._btn_close_about.config(bg=self._theme["button_bg"], fg=self._theme["button_fg"],
                                    activebackground=self._theme["button_activebackground"], activeforeground=self._theme["button_activeforeground"])

    def _toggle_theme(self):
        """ Alterna entre el tema claro y oscuro de la aplicación"""
        if self._flag_dark_theme.get():
            self._apply_theme(ThemesResources.DARK_THEME)
        else:
            self._apply_theme(ThemesResources.LIGHT_THEME)

        # TODO Posicion de ventanas
        # Se pierde la ultima posicion de la ventana y es algo incomo que se recupere en la posicion y tamaño original
        # TODO Marco de ventana popup
        # Si se cierra la ventana popup y luego se abre en modo oscuro el marco superior no se pinta correctamente
        # refresh_window(self._root, sleep=1200)
        # refresh_window(self._top_settings, sleep=1800)

    def _sort_column(self, column):
        # TODO simplificar
        data = [(self._tree_processes.item(row)["values"][0], self._tree_processes.item(row)["values"][1], self._tree_processes.item(
            row)["values"][2], self._tree_processes.item(row)["values"][3]) for row in self._tree_processes.get_children()]

        if column == MainResources.ID_COLUMN_PID:
            data.sort(key=lambda x: int(
                x[0]), reverse=not self._order_asc[MainResources.ID_COLUMN_PID])
            self._order_asc[MainResources.ID_COLUMN_PID] = not self._order_asc[MainResources.ID_COLUMN_PID]
        elif column == MainResources.ID_COLUMN_PROCESS_NAME:
            data.sort(key=lambda x: x[1].lower(
            ), reverse=not self._order_asc[MainResources.ID_COLUMN_PROCESS_NAME])
            self._order_asc[MainResources.ID_COLUMN_PROCESS_NAME] = not self._order_asc[MainResources.ID_COLUMN_PROCESS_NAME]
        elif column == MainResources.ID_COLUMN_STATUS:
            data.sort(key=lambda x: x[2].lower(
            ), reverse=not self._order_asc[MainResources.ID_COLUMN_STATUS])
            self._order_asc[MainResources.ID_COLUMN_STATUS] = not self._order_asc[MainResources.ID_COLUMN_STATUS]
        elif column == MainResources.ID_COLUMN_LOCATION:
            data.sort(key=lambda x: x[3].lower(
            ), reverse=not self._order_asc[MainResources.ID_COLUMN_LOCATION])
            self._order_asc[MainResources.ID_COLUMN_LOCATION] = not self._order_asc[MainResources.ID_COLUMN_LOCATION]

        for row in self._tree_processes.get_children():
            self._tree_processes.delete(row)

        for pid, name, status, location in data:
            self._tree_processes.insert(
                "", "end", values=(pid, name, status, location))

        column_headers = [
            MainResources.ID_COLUMN_PID,
            MainResources.ID_COLUMN_PROCESS_NAME,
            MainResources.ID_COLUMN_STATUS,
            MainResources.ID_COLUMN_LOCATION
        ]

        text = ""
        symbol = ""
        for col in column_headers:
            if col == MainResources.ID_COLUMN_PID:
                text = MainResources.TEXT_COLUMN_PID
            elif col == MainResources.ID_COLUMN_PROCESS_NAME:
                text = MainResources.TEXT_COLUMN_PROCESS_NAME
            elif col == MainResources.ID_COLUMN_STATUS:
                text = MainResources.TEXT_COLUMN_STATUS
            elif col == MainResources.ID_COLUMN_LOCATION:
                text = MainResources.TEXT_COLUMN_LOCATION

            if col == column:
                if self._order_asc[col]:
                    symbol = IconResources.SORT_ASC_ICON
                else:
                    symbol = IconResources.SORT_DESC_ICON
            else:
                symbol = ""

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
            text=f"{MainResources.TEXT_TOTAL}: {len(filtered_data)}")

    def _update_process_list(self):
        # TODO refactorizar
        """ Actualiza la lista de procesos en la tabla principal """
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
        process_list = get_process_list(Constants.OPTIMIZED_LEVEL_2)

        for process in process_list:
            self._process_list.\
                append((
                    process[Constants.COL_PID],
                    process[Constants.COL_NAME],
                    process[Constants.COL_STATUS],
                    process[Constants.COL_EXE]
                ))
            self._tree_processes.\
                insert("", "end",
                       values=(process[Constants.COL_PID],
                               process[Constants.COL_NAME],
                               process[Constants.COL_STATUS],
                               process[Constants.COL_EXE]))

        self._lbl_total.config(
            text=f"{MainResources.TEXT_TOTAL}: {len(self._process_list)}")
        # Lista ordenada por defecto por 'ID'
        self._tree_processes.heading(column=MainResources.ID_COLUMN_PID,
                                     text=f"{MainResources.TEXT_COLUMN_PID} {IconResources.SORT_DESC_ICON}")

    def _on_window_resize(self, event):
        """Se ejecuta cuando la ventana cambia de tamaño"""
        global resize_timer

        # Si ya hay un temporizador en marcha, cancelarlo
        if resize_timer:
            self._window.after_cancel(resize_timer)

        resize_timer = self._window.after(200, self._auto_adjust_columns)

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

        pyperclip.copy(f"[{get_datetime()}]: PID={pid}, Name={name}, Status={status}, Location={exe}")
        print(f"> ACCIÓN: Se copio el contenido de la fila al portapapeles")

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
        """Abre una ventana del explorador de archivos con la ubicación del binario que ejecuta el proceso"""
        selected = self._tree_processes.selection()
        if not selected:
            return

        exe = self._tree_processes.item(selected[0], "values")[3]
        path = os.path.realpath(exe)

        if not os.path.exists(path):
            print(f"> ERROR: No se encontro el archivo '{path}'")
            return

        try:
            subprocess.run(["explorer", "/select,", path], check=True)
        except Exception as e:
            # print(f"> Advertencia: La ruta '{e}' se encuentra en una carpeta privada del sistema")
            print(
                f"> ADVERTENCIA: La ruta '{path}' se encuentra en una carpeta privada del sistema")

    def _center_window_on_screen(self, window: tk.Tk):
        """Establece la posición de la ventana en el centro de la pantalla"""
        window.update_idletasks()
        width_wnd = window.winfo_width()
        height_wnd = window.winfo_height()
        width_screen = window.winfo_screenwidth()
        height_screen = window.winfo_screenheight()
        x = (width_screen // 2) - (width_wnd // 2)
        y = (height_screen // 2) - (height_wnd // 2)
        window.geometry(f"+{x}+{y}")

    def start(self):
        """Inicia la aplicación"""
        self._center_window_on_screen(self._window)
        self._window.deiconify()
        self._window.mainloop()

    def _open_link(self, url: str):
        webbrowser.open_new(url)

    def _show_properties_of_file(self):
        """Muestra la ventana de propiedades asociada al .exe del proceso."""
        selected = self._tree_processes.selection()
        if not selected:
            return

        pid = self._tree_processes.item(selected[0], "values")[0]
        name = self._tree_processes.item(selected[0], "values")[1]
        status = self._tree_processes.item(selected[0], "values")[2]
        exe = self._tree_processes.item(selected[0], "values")[3]

        try:
            import win32com.client
            import pythoncom

            pythoncom.CoInitialize()
            shell = win32com.client.Dispatch("Shell.Application")
            dir = os.path.dirname(exe)
            file = os.path.basename(exe)
            folder = shell.NameSpace(dir)
            item = folder.ParseName(file)
            item.InvokeVerb("properties")

        except Exception as e:
            print(f"> ERROR: No se pudo abrir la ventana de propiedades del proceso asociado al archivo '{exe}'")
