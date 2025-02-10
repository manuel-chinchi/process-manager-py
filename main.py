import tkinter as tk
from tkinter import ttk
import psutil
import config

config.adjust_dpi()

root = tk.Tk()
style = ttk.Style()
root.title(config.APP_TITLE)
root.geometry(config.WINDOW_SIZE)  # Ajustamos el tamaño para incluir más columnas

# Hidden window temporally
root.withdraw()
# @TODO do not load this instruction before '.withdraw' otherwise a small blink occurs before loading the window completely
root.iconbitmap(config.APP_ICON)

def center_window(window):
    window.update_idletasks()  # Actualizar la geometría de la ventana
    width_wnd = window.winfo_width()
    height_wnd = window.winfo_height()
    width_screen = window.winfo_screenwidth()
    height_screen = window.winfo_screenheight()
    x = (width_screen // 2) - (width_wnd // 2)
    y = (height_screen // 2) - (height_wnd // 2)
    window.geometry(f"+{x}+{y}")  # Establecer la posición de la ventana

center_window(root)

# Mostrar la ventana una vez centrada
root.deiconify()

# Resto del código (frame_tabla, tabla, scrollbar, etc.)
frame_process_table = tk.Frame(root)
frame_process_table.pack(expand=True, fill="both")

style = ttk.Style(root)
style.configure("Custom.Treeview",
                borderwidth=0,
                relief="flat",
                )

process_table = ttk.Treeview(frame_process_table, 
                    columns=(config.COLUMN_ID, config.COLUMN_PROCESS_NAME, config.COLUMN_STATUS, config.COLUMN_LOCATION),
                    show="headings", 
                    style="Custom.Treeview")
process_table.heading(config.COLUMN_ID, text=config.COLUMN_HEADERS[config.COLUMN_ID], anchor='w', command=lambda: sort_column(config.COLUMN_ID))
process_table.heading(config.COLUMN_PROCESS_NAME, text=config.COLUMN_HEADERS[config.COLUMN_PROCESS_NAME],anchor='w', command=lambda: sort_column(config.COLUMN_PROCESS_NAME))
process_table.heading(config.COLUMN_STATUS, text=config.COLUMN_HEADERS[config.COLUMN_STATUS], anchor='w', command=lambda: sort_column(config.COLUMN_STATUS))
process_table.heading(config.COLUMN_LOCATION, text=config.COLUMN_HEADERS[config.COLUMN_LOCATION], anchor='w', command=lambda: sort_column(config.COLUMN_LOCATION))
style.configure("Treeview.Heading", background="#B0E0E6", foreground="#0078D7", font=("TkDefaultFont", 10, "bold"))

process_table.column(config.COLUMN_ID, width=75, anchor="w", stretch=True)
process_table.column(config.COLUMN_PROCESS_NAME, width=150, anchor="w", stretch=True)
process_table.column(config.COLUMN_STATUS, width=150, anchor="w", stretch=True)
process_table.column(config.COLUMN_LOCATION, width=150, anchor="w", stretch=True)

scrollbar = tk.Scrollbar(frame_process_table, orient="vertical", command=process_table.yview)
scrollbar.pack(side="right", fill="y")

process_table.config(yscrollcommand=scrollbar.set)
process_table.pack(expand=True, fill="both")

orden_ascendente = {config.COLUMN_ID: True, config.COLUMN_PROCESS_NAME: True, config.COLUMN_STATUS: True, config.COLUMN_LOCATION: True}
all_processes = []

def update_table():
    global all_processes
    for row in process_table.get_children():
        process_table.delete(row)

    all_processes = []
    for p in psutil.process_iter(attrs=['pid', 'name', 'status']):
        try:
            pid = p.info['pid']
            name = p.info['name']
            status = p.info['status']
            location = psutil.Process(pid).exe()
            all_processes.append((pid, name, status, location))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    for pid, name, status, location in all_processes:
        process_table.insert("", tk.END, values=(pid, name, status, location))

    lbl_total.config(text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: {len(all_processes)}")

    process_table.heading(column=config.COLUMN_ID, text=f"{config.COLUMN_HEADERS[config.COLUMN_ID]} {config.SORT_DESC_ICON}")
    process_table.heading(column=config.COLUMN_PROCESS_NAME, text=config.COLUMN_HEADERS[config.COLUMN_PROCESS_NAME])
    process_table.heading(column=config.COLUMN_STATUS, text=config.COLUMN_HEADERS[config.COLUMN_STATUS])
    process_table.heading(column=config.COLUMN_LOCATION, text=config.COLUMN_HEADERS[config.COLUMN_LOCATION])

def sort_column(column):
    global orden_ascendente
    datos = [(process_table.item(row)["values"][0], process_table.item(row)["values"][1], process_table.item(row)["values"][2], process_table.item(row)["values"][3]) for row in process_table.get_children()]

    if column == config.COLUMN_ID:
        datos.sort(key=lambda x: int(x[0]), reverse=not orden_ascendente[config.COLUMN_ID])
        orden_ascendente[config.COLUMN_ID] = not orden_ascendente[config.COLUMN_ID]
    elif column == config.COLUMN_PROCESS_NAME:
        datos.sort(key=lambda x: x[1].lower(), reverse=not orden_ascendente[config.COLUMN_PROCESS_NAME])
        orden_ascendente[config.COLUMN_PROCESS_NAME] = not orden_ascendente[config.COLUMN_PROCESS_NAME]
    elif column == config.COLUMN_STATUS:
        datos.sort(key=lambda x: x[2].lower(), reverse=not orden_ascendente[config.COLUMN_STATUS])
        orden_ascendente[config.COLUMN_STATUS] = not orden_ascendente[config.COLUMN_STATUS]
    elif column == config.COLUMN_LOCATION:
        datos.sort(key=lambda x: x[3].lower(), reverse=not orden_ascendente[config.COLUMN_LOCATION])
        orden_ascendente[config.COLUMN_LOCATION] = not orden_ascendente[config.COLUMN_LOCATION]

    for row in process_table.get_children():
        process_table.delete(row)

    for pid, name, status, location in datos:
        process_table.insert("", "end", values=(pid, name, status, location))

    process_list = [config.COLUMN_ID, config.COLUMN_PROCESS_NAME, config.COLUMN_STATUS, config.COLUMN_LOCATION]
    for col in process_list:
        if col == column:
            symbol = config.SORT_ASC_ICON if orden_ascendente[col] else config.SORT_DESC_ICON
        else:
            symbol = ""
        text = config.COLUMN_HEADERS[config.COLUMN_ID] if col == config.COLUMN_ID else config.COLUMN_HEADERS[config.COLUMN_PROCESS_NAME] if col == config.COLUMN_PROCESS_NAME else config.COLUMN_HEADERS[config.COLUMN_STATUS] if col == config.COLUMN_STATUS else config.COLUMN_HEADERS[config.COLUMN_LOCATION]
        process_table.heading(col, text=f"{text} {symbol}")

def filter_process():
    text = entry_search.get().strip().lower()

    for row in process_table.get_children():
        process_table.delete(row)

    if text == "":
        filtered_data = all_processes
    else:
        filtered_data = [(pid, name, status, location) for pid, name, status, location in all_processes if text in name.lower()]

    for pid, name, status, location in filtered_data:
        process_table.insert("", "end", values=(pid, name, status, location))

    lbl_total.config(text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: {len(filtered_data)}")

frame_controls = tk.Frame(root)
frame_controls.pack(pady=10, fill="x")

entry_search = tk.Entry(frame_controls, width=30)
entry_search.pack(side="left", padx=5, ipady=2)
entry_search.bind('<Return>', lambda event: filter_process())

btn_buscar = ttk.Button(frame_controls, text=config.BOTTOM_FRAME[config.BUTTON_SEARCH], command=filter_process)
btn_buscar.pack(side="left", padx=5)

btn_udpdate = ttk.Button(frame_controls, text=config.BOTTOM_FRAME[config.BUTTON_UPDATE], command=update_table)
btn_udpdate.pack(side="left", padx=5)

lbl_total = tk.Label(frame_controls, text=f"{config.BOTTOM_FRAME[config.LABEL_TOTAL]}: 0")
lbl_total.pack(side="left", padx=5)

update_table()

# Open main window
root.mainloop()