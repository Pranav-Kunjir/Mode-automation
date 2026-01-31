import winreg
import subprocess
import psutil
import sys
import time
import ctypes
import winreg

GLAZE_EXE = "glazewm.exe"
ZEBAR_EXE = "zebar.exe"

def set_activate_window_on_hover(enable: bool):
    value = 1 if enable else 0

    # Persist the setting
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Control Panel\Desktop",
        0,
        winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(
            key,
            "ActiveWndTrk",
            0,
            winreg.REG_SZ,
            str(value)
        )

    # Apply immediately (THIS is the critical part)
    SPI_SETACTIVEWINDOWTRACKING = 0x1001
    SPIF_SENDCHANGE = 0x02

    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETACTIVEWINDOWTRACKING,
        0,
        value,
        SPIF_SENDCHANGE
    )


def kill_process(name: str):
    for p in psutil.process_iter(["name"]):
        try:
            if p.info["name"] and name.lower() in p.info["name"].lower():
                p.kill()
        except psutil.NoSuchProcess:
            pass

def set_focus_follows_mouse(enable: bool):
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Control Panel\Desktop",
        0,
        winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(
            key,
            "ActiveWndTrk",
            0,
            winreg.REG_SZ,
            "1" if enable else "0"
        )

def set_focus_on_hover(enable: bool):
    value = "1" if enable else "0"
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Control Panel\Desktop",
        0,
        winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, "ActiveWndTrk", 0, winreg.REG_SZ, value)
        winreg.SetValueEx(key, "ActiveWndTrkZorder", 0, winreg.REG_SZ, value)



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

    subprocess.run(
        ["taskkill", "/f", "/im", "explorer.exe"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    subprocess.Popen("explorer.exe")

def stop_glaze_stack():
    kill_process(ZEBAR_EXE)
    kill_process(GLAZE_EXE)

def is_running(name: str) -> bool:
    for p in psutil.process_iter(["name"]):
        if p.info["name"] and name.lower() in p.info["name"].lower():
            return True
    return False

def start_glaze_stack():
    if not is_running(GLAZE_EXE):
        subprocess.Popen([GLAZE_EXE])

    if not is_running(ZEBAR_EXE):
        subprocess.Popen([ZEBAR_EXE])


def gaming_mode():
    stop_glaze_stack()
    set_activate_window_on_hover(False)
    set_taskbar_autohide(False)

def normal_mode():
    set_activate_window_on_hover(True)
    set_taskbar_autohide(True)

    time.sleep(2)
    start_glaze_stack()




if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: gaming_toggle.py on | off")
        sys.exit(1)

    if sys.argv[1] == "on":
        gaming_mode()
    elif sys.argv[1] == "off":
        normal_mode()
    else:
        print("Invalid argument")


def enable_gaming():
    gaming_mode()

def enable_normal():
    normal_mode()
