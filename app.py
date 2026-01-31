import winreg
import subprocess
import psutil
import ctypes
import time
import sys
import os

import pystray
from pystray import MenuItem as Item
from PIL import Image

# =========================================================
# CONFIG
# =========================================================
GLAZE_EXE = "glazewm.exe"
ZEBAR_EXE = "zebar.exe"
DETACHED_FLAGS = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

STATE = {"mode": "normal"}  # "gaming" | "normal"

# =========================================================
# PYINSTALLER RESOURCE HANDLING
# =========================================================
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# =========================================================
# PROCESS HELPERS
# =========================================================
def is_running(name: str) -> bool:
    for p in psutil.process_iter(["name"]):
        if p.info["name"] and name.lower() in p.info["name"].lower():
            return True
    return False

def kill_process(name: str):
    for p in psutil.process_iter(["name"]):
        try:
            if p.info["name"] and name.lower() in p.info["name"].lower():
                p.kill()
        except psutil.NoSuchProcess:
            pass

# =========================================================
# WINDOWS SETTINGS
# =========================================================
def set_activate_window_on_hover(enable: bool):
    value = 1 if enable else 0

    # Persist setting
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Control Panel\Desktop",
        0,
        winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, "ActiveWndTrk", 0, winreg.REG_SZ, str(value))

    # Apply immediately
    SPI_SETACTIVEWINDOWTRACKING = 0x1001
    SPIF_SENDCHANGE = 0x02

    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETACTIVEWINDOWTRACKING,
        0,
        value,
        SPIF_SENDCHANGE
    )

def set_taskbar_autohide(enable: bool):
    path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StuckRects3"
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        path,
        0,
        winreg.KEY_ALL_ACCESS
    ) as key:
        data, regtype = winreg.QueryValueEx(key, "Settings")
        data = bytearray(data)
        data[8] = 3 if enable else 2
        winreg.SetValueEx(key, "Settings", 0, regtype, bytes(data))

    # Restart Explorer (required)
    subprocess.run(
        ["taskkill", "/f", "/im", "explorer.exe"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    subprocess.Popen("explorer.exe")

# =========================================================
# GLAZEWM / ZEBAR
# =========================================================
def stop_glaze_stack():
    kill_process(ZEBAR_EXE)
    kill_process(GLAZE_EXE)

# def start_glaze_stack():
#     if not is_running(GLAZE_EXE):
#         subprocess.Popen([GLAZE_EXE])

#     if not is_running(ZEBAR_EXE):
#         subprocess.Popen([ZEBAR_EXE])

def start_glaze_stack():
    if not is_running(GLAZE_EXE):
        subprocess.Popen(
            [GLAZE_EXE],
            creationflags=DETACHED_FLAGS,
            close_fds=True
        )

    if not is_running(ZEBAR_EXE):
        subprocess.Popen(
            [ZEBAR_EXE],
            creationflags=DETACHED_FLAGS,
            close_fds=True
        )


# =========================================================
# MODES
# =========================================================
def gaming_mode():
    stop_glaze_stack()
    set_activate_window_on_hover(False)
    set_taskbar_autohide(False)
    STATE["mode"] = "gaming"

def normal_mode():
    set_activate_window_on_hover(True)
    set_taskbar_autohide(True)

    # Allow Explorer tray to stabilize (important for Zebar)
    time.sleep(2)

    start_glaze_stack()
    STATE["mode"] = "normal"

# =========================================================
# TRAY UI CALLBACKS
# =========================================================
def set_gaming(icon, item):
    gaming_mode()
    icon.update_menu()

def set_normal(icon, item):
    normal_mode()
    icon.update_menu()

def quit_app(icon, item):
    icon.stop()

# =========================================================
# TRAY MENU
# =========================================================
menu = pystray.Menu(
    Item(
        "🎮 Gaming Mode",
        set_gaming,
        checked=lambda _: STATE["mode"] == "gaming"
    ),
    Item(
        "💻 Normal Mode",
        set_normal,
        checked=lambda _: STATE["mode"] == "normal"
    ),
    pystray.Menu.SEPARATOR,
    Item("❌ Exit", quit_app)
)

# =========================================================
# TRAY ENTRY POINT
# =========================================================
def run_tray():
    image = Image.open(resource_path("icon.png"))
    icon = pystray.Icon(
        "GlazeWM Toggle",
        image,
        "Gaming / Normal Mode",
        menu
    )
    icon.run()  # MUST block

# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":
    run_tray()
