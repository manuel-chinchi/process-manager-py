import tkinter as tk
import config
import pmcore  # custom libs
from process_manager import ProcessManager

config.adjust_dpi_win32()


if __name__ == "__main__":
    # @NOTE ESTA SENTENCIA ES NECESARIA PARA PODER CREAR EL EJECUTABLE CON PYINSTALLER!!!
    pmcore.avoid_thread_overflow()

    root = tk.Tk()
    pm = ProcessManager(root=root)
    pm.start()
