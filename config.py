# archivo:      config.py
# descripción:  Este archivo contiene la configuración general del programa
#               que puede resumirse como:
#               - Ajustes para monitores con DPI alto
#               - Temas de colores a usar
#               - Rutas para archivos temporales 
#               - Iconos de la aplicación

import ctypes
import sys, os
from enum import unique


# def get_dir_file(f):
#     import os
#     return os.path.dirname(os.path.abspath(f))

def resource_path(relative_path):
    """ Obtiene la ruta absoluta del recurso, funcionando tanto en desarrollo como en producción """
    if getattr(sys, 'frozen', False):  # Si el programa está compilado con PyInstaller
        base_path = sys._MEIPASS  # Carpeta temporal donde PyInstaller extrae los archivos
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def adjust_dpi_application():
    """Ajusta el renderizado de la aplicación para pantallas con DPI alto (en sistemas Windows)"""
    import ctypes
    try:  # >= win 8.1
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except:  # win 8.0 or less
        ctypes.windll.user32.SetProcessDPIAware()


def set_bg_color_title_bar(window, color=1000):  # THEME_LIGHT (default)
    """
    Establece el color de la barra de título de la ventana del programa

    Mas informacíón: https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute
    """
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ctypes.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    # rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 0
    if color == ThemesResources.THEME_LIGHT:
        value = 0  # blanco
    elif color == ThemesResources.THEME_DARK:
        value = 2  # negro
    # TODO Valores 0,2 son internos de Window para colores (investigar)
    value = ctypes.c_int(value)
    set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value),
                         ctypes.sizeof(value))


def is_Windows():
    return os.name == 'nt'


class ThemesResources:
    """ Clase que contiene definiciones para temas y colores de la aplicación """
    # Colors
    COLOR_WHITE0 = "#FFFFFF"
    COLOR_WHITE1 = "#F0F0F0"  # color de controles por defecto
    COLOR_WHITE2 = "#E0E0E0"
    COLOR_WHITE3 = "#D0D0D0"
    COLOR_WHITE4 = "#C0C0C0"
    COLOR_BLACK0 = "#000000"
    COLOR_BLACK1 = "#1E1E1E"
    COLOR_BLACK2 = "#2E2E2E"
    COLOR_BLACK3 = "#3E3E3E"
    COLOR_BLACK4 = "#4E4E4E"
    COLOR_SKYBLUE0 = "#2980B9"
    COLOR_SKYBLUE1 = "#3498DB"
    COLOR_SKYBLUE2 = "#5DADE2"
    COLOR_SKYBLUE3 = "#85C1E9"
    COLOR_SKYBLUE4 = "#AED6F1"
    COLOR_SKYBLUE5 = "#CDE8FF"  # ~taskmgr.exe row selected
    COLOR_BLUE = "#0000ff"
    COLOR_YELLOW = "#ffff00"

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
        "treeview_foreground_selected": COLOR_BLACK0,
        "treeview_foreground_!selected": COLOR_BLACK0,
        "checkbox_bg": COLOR_WHITE1,
        "checkbox_fg": COLOR_BLACK0,
        "checkbox_selectcolor": COLOR_WHITE0,  # color fondo del checkbox
        "checkbox_activeforeground": COLOR_BLACK0,  # color texto (al presionar)
        "checkbox_activebackground": COLOR_WHITE1,  # color fondo (al presionar)
        "label_fg_hyperlink": COLOR_BLUE
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
        "checkbox_activebackground": COLOR_SKYBLUE0,
        "label_fg_hyperlink": COLOR_YELLOW
    }

class IconResources:
    APP_ICON = "ProcessManagerPy.ico"
    SORT_ASC_ICON = "▲"
    SORT_DESC_ICON = "▼"

class MainResources:
    TITLE = "Process Manager Py"
    SIZE = "800x600"
    VERSION = "1.0"
    # columns id's
    ID_COLUMN_PID = 101
    ID_COLUMN_PROCESS_NAME = 102
    ID_COLUMN_STATUS = 103
    ID_COLUMN_LOCATION = 1031
    # columns labels
    TEXT_COLUMN_PID = "PID"
    TEXT_COLUMN_PROCESS_NAME = "Nombre"
    TEXT_COLUMN_STATUS = "Estado"
    TEXT_COLUMN_LOCATION = "Ubicación"
    # bottom option panel
    TEXT_BUTTON_SEARCH = "Buscar"
    TEXT_BUTTON_UPDATE = "Actualizar"
    TEXT_BUTTON_SETTINGS = "Configuración"
    TEXT_LABEL_TOTAL = "Total"

    ID_CONTEXT_MENU = 1020
    ID_MENU_OPT_COPY_TO_CLIPBOARD = 1021
    ID_MENU_OPT_OPEN_LOCATION_PROCESS = 1022

    TEXT_COPY_TO_CLIPBOARD = "Copiar información al portapapeles"
    TEXT_OPEN_LOCATION_PROCESS = "Abrir ubicación del archivo"
    TEXT_PROPERTIES = "Propiedades"

    TEXT_SEARCH = "Buscar"
    TEXT_UPDATE = "Actualizar"
    TEXT_SETTINGS = "Configuración"
    TEXT_TOTAL = "Total"

    URL_REPOSITORY = "https://github.com/manuel-chinchi/process-manager-py"

class SettingsResources:
    TITLE = "Configuración"
    SIZE = "320x140"
    TEXT_ADJUST_WIDTH_COLS = "Ajuste automático de columna"
    TEXT_ENABLE_DARK_THEME = "Activar tema oscuro"
    TEXT_CLOSE = "Cerrar"
