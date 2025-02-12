def get_dir_file(f):
    import os
    return os.path.dirname(os.path.abspath(f))

APP_TITLE = "Adminstrador de procesos"
APP_ICON = get_dir_file(__file__) + "/" + "taskmgr.exe_14_107.ico"
# WINDOW_SIZE = "640x480"
WINDOW_SIZE="800x600"

# IDs controls
COLUMN_ID = 101
COLUMN_PROCESS_NAME = 102
COLUMN_STATUS = 103
COLUMN_LOCATION = 1031
BUTTON_SEARCH = 104
BUTTON_UPDATE = 105
LABEL_TOTAL = 106
BUTTON_SETTINGS =107
CHECKBOX_ADJUST_AUTOMATIC_COLS=108
CHECKBOX_DARK_THEME=110
BUTTON_CLOSE_SETTINGS = 109
WINDOW_SETTINGS = 111
TITLE_WND_SETTINGS = 112
SIZE_WND_SETTINGS = 113

COLUMN_HEADERS = {
    COLUMN_ID : "Id",
    COLUMN_PROCESS_NAME : "Nombre",
    COLUMN_STATUS : "Estado",
    COLUMN_LOCATION: "Ubicación"
}

BOTTOM_FRAME = {
    BUTTON_SEARCH : "Buscar",
    BUTTON_UPDATE : "Actualizar",
    BUTTON_SETTINGS : "Configuración",
    LABEL_TOTAL : "Total"
}

SETTINGS_OPTIONS = {
    TITLE_WND_SETTINGS : "Configuración",
    SIZE_WND_SETTINGS: "320x140",
    CHECKBOX_ADJUST_AUTOMATIC_COLS: "Ajuste automático de columna",
    CHECKBOX_DARK_THEME: "Activar tema oscuro (requiere reiniciar)",
    BUTTON_CLOSE_SETTINGS: "Cerrar"
}

SORT_ASC_ICON = "▲"
SORT_DESC_ICON = "▼"

# Definir colores para el tema claro y oscuro
LIGHT_THEME = {
    "name": "light",
    "bg": "#FFFFFF",  # Fondo claro # deberia ser #F0F0F0 (fondo de controles por defecto)
    "fg": "#000000",  # Texto oscuro
    "button_bg": "#F0F0F0",  # Fondo de botones claro
    "button_fg": "#000000",  # Texto de botones oscuro
    "button_active_fg":"#000000", # idem 'button_fg
    "button_active_bg":"#F0F0F0", # idem 'button_bg
    "treeview_bg": "#FFFFFF",  # Fondo de Treeview claro
    "treeview_fg": "#000000",  # Texto de Treeview oscuro
    "treeview_heading_bg": "#CDE8FF",  # Fondo de encabezados (celeste claro)
    "treeview_heading_fg": "#000000",  # Manteniendo el azul que ya tenías
    "checkbox_bg":"#FFFFFF",
    "checkbox_active_fg":"#000000",
    "checkbox_active_bg":"#F0F0F0"
}
# TODO Pendiente (tema nocturno)
# Total Commander no cambia el color de selección de fila entre temas (tomar sugerencia ya que es mas visible)
DARK_THEME = {
    "name": "dark",
    "bg": "#2E2E2E",  # Fondo oscuro
    "fg": "#FFFFFF",  # Texto claro
    "button_bg": "#4E4E4E",  # Fondo de botones oscuro
    "button_fg": "#FFFFFF",  # Texto de botones claro
    "button_active_fg":"#F0F0F0", # idem 'button_fg
    "button_active_bg":"#2980B9", # idem 'button_bg
    "treeview_bg": "#2E2E2E",  # Fondo de Treeview oscuro
    "treeview_fg": "#FFFFFF",  # Texto de Treeview claro
    # "treeview_heading_bg": "#334F66",  # Fondo de encabezados de Treeview oscuro
    "treeview_heading_bg": "#1E1E1E",  # Fondo de encabezados de Treeview oscuro
    # "treeview_heading_fg": "#CDE8FF",  # Fondo de encabezados de Treeview oscuro
    "treeview_heading_fg": "#FFFFFF",  # Texto de encabezados de Treeview claro
    "checkbox_bg": "#2980B9",
    "checkbox_active_fg":"#F0F0F0",
    "checkbox_active_bg":"#2980B9"
}

def adjust_dpi():
    # TODO Solucion DPI alto (controles borrosos)
    # Copiado de https://stackoverflow.com/questions/62794931/high-dpi-tkinter-re-scaling-when-i-run-it-in-spyder-and-when-i-run-it-direct-in
    import ctypes
    try: # >= win 8.1
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except: # win 8.0 or less
        ctypes.windll.user32.SetProcessDPIAware()