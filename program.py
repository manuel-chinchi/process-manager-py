import tkinter as tk
from config import is_Windows, adjust_app_DPI
from core import avoid_thread_overflow
from process_manager import ProcessManager


def main():
    # requerido para crear el executable con PyInstaller!!!
    avoid_thread_overflow() 

    if is_Windows():
        adjust_app_DPI()

    root = tk.Tk()
    pm = ProcessManager(window=root)
    pm.start()


if __name__ == "__main__":
    main()
