import subprocess
import os
import ctypes
from pathlib import Path


def getUSB():
    """
    Detecta dispositius USB/discs externs connectats a l'ordinador.
    Utilitza múltiples mètodes per major robustesa.
    Retorna una llista de lletres d'unitats (ex: ['E:', 'F:']).
    """
    usb_devices = []

    # Mètode 1: Usar wmic amb atribut DriveType per detectar discs removibles (DriveType=2)
    try:
        result = subprocess.run(
            ['wmic', 'logicaldisk', 'get', 'name,driveType', '/format:csv'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Salta la capçalera
                parts = line.split(',')
                if len(parts) >= 2:
                    letter = parts[0].strip()
                    drive_type = parts[1].strip()
                    # DriveType 2 = Removable, 3 = Fixed
                    if drive_type == '2' and letter and ':' in letter:
                        usb_devices.append(letter)
    except Exception as e:
        print(f"[Mètode 1 - wmic] Error: {e}")

    # Mètode 2: Usar powershell per detectar discs USB específicament
    try:
        ps_command = (
            "Get-Volume | Where-Object {$_.DriveType -eq 'Removable'} | Select-Object -ExpandProperty DriveLetter"
        )
        result = subprocess.run(
            ['powershell', '-NoProfile', '-Command', ps_command],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                letter = line.strip()
                if letter and letter not in usb_devices:
                    usb_devices.append(letter + ':')
    except Exception as e:
        print(f"[Mètode 2 - PowerShell] Error: {e}")

    # Mètode 3: Llistar totes les unitats disponibles i filtrar
    try:
        available_drives = []
        for letter in 'DEFGHIJKLMNOPQRSTUVWXYZ':
            drive = f"{letter}:"
            if os.path.exists(drive):
                available_drives.append(drive)

        # Si no tenim detecció per wmic, assumim que totes les unitats (excepte C:) són externes
        if not usb_devices and available_drives:
            usb_devices = [d for d in available_drives if d != 'C:']
    except Exception as e:
        print(f"[Mètode 3 - Llistat] Error: {e}")

    # Filtratge adicional: eliminar duplicats
    usb_devices = list(set(usb_devices))
    usb_devices.sort()

    if not usb_devices:
        print("Cap dispositiu USB/extern detectat")
        print("Unitats disponibles en el sistema:")
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if os.path.exists(f"{letter}:"):
                print(f"   {letter}:")
        return None

    return usb_devices[0]+'/tesi' if usb_devices else None


# Exemple d'ús
if __name__ == "__main__":
    usb_device = getUSB()
    if usb_device:
        print(f"Disc extern seleccionat: {usb_device}")
    else:
        print("No s'ha detectat cap dispositiu USB.")
