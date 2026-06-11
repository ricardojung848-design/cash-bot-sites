import os
import sys
import platform

def run_modul():
    info = zeige_status()
    return f'=== SYSTEM UPDATER AKTIV ===\n\n{info}'

def zeige_status():
    status = f'OS: {platform.system()} ({platform.machine()})\n'
    status += f'Python: {platform.python_version()}\n'
    status += f'Pfad: {os.getcwd()}\n'
    return status
