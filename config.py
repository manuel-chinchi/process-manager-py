APP_TITLE = "Adminstrador de procesos"
APP_ICON = "taskmgr.exe_14_107.ico"
WINDOW_SIZE = "640x480"

COLUMN_ID = "Id"
COLUMN_PROCESS_NAME = "ProcessName"
COLUMN_STATUS = "Status"
# COLUMN_DESCRIPTION = "Descripción"

COLUMN_HEADERS = {
    COLUMN_ID : "ID",
    COLUMN_PROCESS_NAME : "Nombre",
    COLUMN_STATUS : "Estado"
}

BUTTON_SEARCH = 100
BUTTON_UPDATE = 101
LABEL_TOTAL = 102
# BUTTON_SEARCH = ""
BOTTOM_FRAME = {
    BUTTON_SEARCH : "Buscar",
    BUTTON_UPDATE : "Actualizar",
    LABEL_TOTAL : "Total"
}

SORT_ASC_ICON = "▲"
SORT_DESC_ICON = "▼"

def adjust_dpi():
    # @TODO solucion DPI alto en pantallas https://stackoverflow.com/questions/62794931/high-dpi-tkinter-re-scaling-when-i-run-it-in-spyder-and-when-i-run-it-direct-in
    import ctypes
    try: # >= win 8.1
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except: # win 8.0 or less
        ctypes.windll.user32.SetProcessDPIAware()