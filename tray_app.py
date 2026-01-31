import threading
import pystray
from pystray import MenuItem as Item
from PIL import Image

import gaming_toggle

STATE = {"mode": "normal"}

def set_gaming(icon, item):
    gaming_toggle.enable_gaming()
    STATE["mode"] = "gaming"
    icon.update_menu()

def set_normal(icon, item):
    gaming_toggle.enable_normal()
    STATE["mode"] = "normal"
    icon.update_menu()

def quit_app(icon, item):
    icon.stop()

def is_gaming():
    return STATE["mode"] == "gaming"

def is_normal():
    return STATE["mode"] == "normal"

menu = pystray.Menu(
    Item("🎮 Gaming Mode", set_gaming, checked=lambda _: is_gaming()),
    Item("💻 Normal Mode", set_normal, checked=lambda _: is_normal()),
    pystray.Menu.SEPARATOR,
    Item("❌ Exit", quit_app)
)

def run_tray():
    image = Image.open("icon.png")
    icon = pystray.Icon("Glaze Toggle", image, "Mode Switcher", menu)
    icon.run()

if __name__ == "__main__":
    threading.Thread(target=run_tray, daemon=True).start()

    # Keep process alive
    import time
    while True:
        time.sleep(1)
