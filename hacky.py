import ctypes

def refresh_window(window, sleep=1000):
    """Fuerza la actualización del marco superior"""
    window.update_idletasks()
    window.withdraw()  # Oculta la ventana temporalmente
    window.after(sleep, window.deiconify)  # La vuelve a mostrar

def set_bg_color_title_bar(window, color="light"):
    # ref
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
    if color=='light':
        value = 0 # blanco
    elif color=='dark':
        value = 2 # negro
    # TODO Valores 0,2 son internos de Window para colores (investigar)
    value = ctypes.c_int(value)
    set_window_attribute(hwnd, 20, ctypes.byref(value),
                         ctypes.sizeof(value))
