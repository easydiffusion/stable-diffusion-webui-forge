# monitors and kills itself when the parent process dies. required when running Forge as a sub-process.
# modified version of https://stackoverflow.com/a/23587108

import os
import threading
import platform
import time


def _monitor_parent_posix(parent_pid):
    import psutil

    print(f"Monitoring parent pid: {parent_pid}")
    while True:
        if not psutil.pid_exists(parent_pid):
            print(f"Parent pid {parent_pid} died. Exiting.")
            os._exit(0)
        time.sleep(1)


def _monitor_parent_windows(parent_pid):
    from ctypes import WinDLL, WinError
    from ctypes.wintypes import DWORD, BOOL, HANDLE

    SYNCHRONIZE = 0x00100000  # Magic value from http://msdn.microsoft.com/en-us/library/ms684880.aspx
    kernel32 = WinDLL("kernel32.dll")
    kernel32.OpenProcess.argtypes = (DWORD, BOOL, DWORD)
    kernel32.OpenProcess.restype = HANDLE

    handle = kernel32.OpenProcess(SYNCHRONIZE, False, parent_pid)
    if not handle:
        raise WinError()

    # Wait until parent exits
    from ctypes import windll

    print(f"Monitoring parent pid: {parent_pid}")
    windll.kernel32.WaitForSingleObject(handle, -1)
    os._exit(0)


def start_monitor_thread(parent_pid):
    if platform.system() == "Windows":
        t = threading.Thread(target=_monitor_parent_windows, args=(parent_pid,), daemon=True)
    else:
        t = threading.Thread(target=_monitor_parent_posix, args=(parent_pid,), daemon=True)
    t.start()
