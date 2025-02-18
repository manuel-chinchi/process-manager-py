# Process Manager Py
A simple Process manager program made in Python + TKinter

This project uses Python 3.10.0 (32-bit).

## Libraries
The project requires the following libraries:

- diskcache 5.6.3
- psutil 7.0.0
- pyperclip 1.9.0
- pyinstaller 6.12.0 (and dependencies)

See all dependences in the `requirements.txt` file.

## Supported platforms

- Windows 7 SP1 (\*)
- Windows 10 (v22H2 c19045.5131)

(\*) Note: On Windows 7, you need to copy the file `api-ms-win-core-path-l1-1-0.dll` on the location `C:\Windows\SysWOW64\`. See [this](https://github.com/nalexandru/api-ms-win-core-path-HACK) repository for details.

## How modify this project?

1.  Create the virtual environment:
    ```
    python -m venv env
    ```
2.  Activate the virtual environment
    ```
    env/Scripts/Activate
    ```
3.  Install dependencies:
    ```
    python -m pip install -r requirements.txt
    ```
    (If an error occurs, install `pip` and `setuptools` first)
3.  Run PyInstaller to generate the executable:
    ```
    pyinstaller --onefile --noconsole --icon='ProcessManagerPy.ico' --add-data 'ProcessManagerPy.ico;.' program.py
    ```

## How to install this projec?

The folder `dist` contain the `setup.exe` installer made with InnoSetup directly to run.

## Screenshots

<br>
<p align="center">
    <img src=".resources\taskmanager_ligth_theme.png" width="642">
<p>
<br>
<p align="center">
    <img src=".resources\taskmanager_dark_theme.png" width="642">
<p>

## References

- [define custom styles TKinter](https://www.pythontutorial.net/tkinter/ttk-style/)
- [change bg color in tree TKinter](https://stackoverflow.com/questions/43816930/how-to-fully-change-the-background-color-on-a-tkinter-ttk-treeview)
- [hide TopLevel window TKinter](https://stackoverflow.com/questions/67590510/hide-or-close-top-level-window-when-main-window-isnt-visible)
- [change bg color control TKinter](https://stackoverflow.com/questions/58678381/is-it-possible-to-change-the-menu-border-color-in-tkinter)
- [icon not show pyinstaller TKinter](https://stackoverflow.com/questions/71006377/tkinter-icon-is-not-working-after-converting-to-exe)
- [Create exe from Win 10 SDK to Win 7 <-> pyinstaller](https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/)
- [crear exe multicompatible win7/win10](https://stackoverflow.com/questions/47155474/create-an-exe-compatible-with-all-versions-of-windows-64-bit-and-32-bit-even-if)
- [missing api-ms-win-core-path-l1-1-0.dll file pyinstaller](https://github.com/orgs/pyinstaller/discussions/6200)

<!-- software made in Argentina 🇦🇷-->
