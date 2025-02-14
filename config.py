import ctypes


def get_dir_file(f):
    import os
    return os.path.dirname(os.path.abspath(f))


APP_TITLE = "Adminstrador de procesos"
APP_ICON = get_dir_file(__file__) + "/Icons/taskmgr.exe_14_107.ico"
# WINDOW_SIZE = "640x480"
WINDOW_SIZE = "800x600"

# IDs controls
COLUMN_ID = 101
COLUMN_PROCESS_NAME = 102
COLUMN_STATUS = 103
COLUMN_LOCATION = 1031
BUTTON_SEARCH = 104
BUTTON_UPDATE = 105
LABEL_TOTAL = 106
BUTTON_SETTINGS = 107
CHECKBOX_ADJUST_AUTOMATIC_COLS = 108
CHECKBOX_DARK_THEME = 110
BUTTON_CLOSE_SETTINGS = 109
WINDOW_SETTINGS = 111
TITLE_WND_SETTINGS = 112
SIZE_WND_SETTINGS = 113

COLUMN_HEADERS = {
    COLUMN_ID: "PID",
    COLUMN_PROCESS_NAME: "Nombre",
    COLUMN_STATUS: "Estado",
    COLUMN_LOCATION: "Ubicación"
}

BOTTOM_FRAME = {
    BUTTON_SEARCH: "Buscar",
    BUTTON_UPDATE: "Actualizar",
    BUTTON_SETTINGS: "Configuración",
    LABEL_TOTAL: "Total"
}

SETTINGS_OPTIONS = {
    TITLE_WND_SETTINGS: "Configuración",
    SIZE_WND_SETTINGS: "320x140",
    CHECKBOX_ADJUST_AUTOMATIC_COLS: "Ajuste automático de columna",
    CHECKBOX_DARK_THEME: "Activar tema oscuro (requiere reiniciar)",
    BUTTON_CLOSE_SETTINGS: "Cerrar"
}

SORT_ASC_ICON = "▲"
SORT_DESC_ICON = "▼"


# Colors
COLOR_WHITE0 = "#FFFFFF"
COLOR_WHITE1 = "#F0F0F0"  # color de controles por defecto
COLOR_WHITE2 = "#E0E0E0"
COLOR_WHITE3 = "#D0D0D0"
COLOR_WHITE4 = "#C0C0C0"
COLOR_BLACK0 = "#000000"
COLOR_BLACK1 = "#1E1E1E"
COLOR_BLACK2 = "#2E2E2E"
COLOR_BLACK3 = "#3E3E3E"  # no usado
COLOR_BLACK4 = "#4E4E4E"
COLOR_SKYBLUE0 = "#2980B9"
COLOR_SKYBLUE1 = "#3498DB"
COLOR_SKYBLUE2 = "#5DADE2"
COLOR_SKYBLUE3 = "#85C1E9"
COLOR_SKYBLUE4 = "#AED6F1"
COLOR_SKYBLUE5 = "#CDE8FF"  # ~taskmgr.exe row selected

THEME_LIGHT = 1000
THEME_DARK = 2000

# Colores bg/fg/bg2/fg2 son para controles contenedores por lo general

LIGHT_THEME = {
    "name": THEME_LIGHT,
    "bg": COLOR_WHITE0,  # background
    "fg": COLOR_BLACK0,  # foreground
    "bg2": COLOR_WHITE1,  # background
    "fg2": 0,  # foreground
    "frame_bg": COLOR_WHITE1,
    "frame_fg": COLOR_BLACK0,
    "label_bg": COLOR_WHITE1,
    "label_fg": COLOR_BLACK0,
    "entry_bg": COLOR_WHITE0,
    "entry_fg": COLOR_BLACK0,
    "entry_insertbackground": COLOR_BLACK0,  # color de cursor/caret
    "button_bg": COLOR_WHITE1,
    "button_fg": COLOR_BLACK0,
    "button_activeforeground": COLOR_BLACK0,  # color texto (al presionar)
    "button_activebackground": COLOR_WHITE1,  # color fondo (al presionar)
    "treeview_bg": COLOR_WHITE0,
    "treeview_fg": COLOR_BLACK0,
    "treeview_background_selected": COLOR_SKYBLUE5,  # color de fila seleccionada
    "treeview_background_!selected": COLOR_WHITE0,
    # Manteniendo el azul que ya tenías
    "treeview_foreground_selected": COLOR_BLACK0,
    "treeview_foreground_!selected": COLOR_BLACK0,
    "checkbox_bg": COLOR_WHITE1,
    "checkbox_fg": COLOR_BLACK0,
    "checkbox_selectcolor": COLOR_WHITE0,  # color fondo del checkbox
    "checkbox_activeforeground": COLOR_BLACK0,  # color texto (al presionar)
    "checkbox_activebackground": COLOR_WHITE1  # color fondo (al presionar)
}

DARK_THEME = {
    "name": THEME_DARK,
    "bg": COLOR_BLACK2,
    "fg": COLOR_WHITE0,
    "bg2": COLOR_BLACK3,
    "fg2": 0,
    "frame_bg": COLOR_BLACK3,
    "frame_fg": COLOR_WHITE0,
    "label_bg": COLOR_BLACK3,
    "label_fg": COLOR_WHITE0,
    "entry_bg": COLOR_BLACK2,
    "entry_fg": COLOR_WHITE0,
    "entry_insertbackground": COLOR_WHITE0,
    "button_bg": COLOR_BLACK3,
    "button_fg": COLOR_WHITE0,
    "button_activeforeground": COLOR_WHITE1,
    "button_activebackground": COLOR_SKYBLUE0,
    "treeview_bg": COLOR_BLACK2,
    "treeview_fg": COLOR_WHITE0,
    "treeview_background_selected": COLOR_BLACK1,
    "treeview_background_!selected": COLOR_BLACK2,
    "treeview_foreground_selected": COLOR_WHITE0,
    "treeview_foreground_!selected": COLOR_WHITE0,
    "checkbox_bg": COLOR_BLACK3,
    "checkbox_fg": COLOR_WHITE0,
    "checkbox_selectcolor": COLOR_SKYBLUE0,
    "checkbox_activeforeground": COLOR_WHITE1,
    "checkbox_activebackground": COLOR_SKYBLUE0
}


def adjust_dpi():
    # TODO Solucion DPI alto (controles borrosos)
    # Copiado de https://stackoverflow.com/questions/62794931/high-dpi-tkinter-re-scaling-when-i-run-it-in-spyder-and-when-i-run-it-direct-in
    import ctypes
    try:  # >= win 8.1
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except:  # win 8.0 or less
        ctypes.windll.user32.SetProcessDPIAware()


def set_bg_color_title_bar(window, color=THEME_LIGHT):
    # HACK solucion no convencional
    # https://stackoverflow.com/questions/23836000/can-i-change-the-title-bar-in-tkinter
    """
    MORE INFO:
    https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute
    """
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ctypes.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 0
    if color == THEME_LIGHT:
        value = 0  # blanco
    elif color == THEME_DARK:
        value = 2  # negro
    # TODO Valores 0,2 son internos de Window para colores (investigar)
    value = ctypes.c_int(value)
    set_window_attribute(hwnd, 20, ctypes.byref(value),
                         ctypes.sizeof(value))
