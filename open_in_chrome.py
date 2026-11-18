import subprocess
import time
import ctypes
import os

user32 = ctypes.windll.user32

# 1. Open Chrome with http://localhost:5173/ in a brand new window
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
url = "http://localhost:5173/"

print("Launching Chrome new window...")
subprocess.Popen([chrome_path, "--new-window", url])

time.sleep(1.5)

# 2. Enumerate windows to find the Chrome window for OceanEmbed or Chrome
SW_RESTORE = 9
SW_SHOWMAXIMIZED = 3

found_hwnds = []

def enum_windows_callback(hwnd, extra):
    if user32.IsWindowVisible(hwnd):
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value
            if "OceanEmbed" in title or "Chrome" in title or "localhost" in title:
                found_hwnds.append((hwnd, title))
    return True

EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)

print(f"Found candidate windows: {found_hwnds}")

for hwnd, title in found_hwnds:
    print(f"Activating: {title} (HWND: {hwnd})")
    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.SetForegroundWindow(hwnd)

print("Done.")
