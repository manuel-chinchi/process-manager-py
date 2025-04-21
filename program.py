import tkinter as tk
from config import is_Windows, adjust_dpi_application
from core import avoid_thread_overflow
from process_manager import ProcessManager


def main():
    # requerido para crear el executable con PyInstaller!!!
    avoid_thread_overflow() 

    if is_Windows():
        adjust_dpi_application()

    window = tk.Tk()
    pm = ProcessManager(window=window)
    pm.start()


if __name__ == "__main__":
    main()
