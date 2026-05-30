import subprocess
import os
from pathlib import Path

def getUSB():
    """
    Detecta dispositius USB/discs externs connectats a l'ordinador que continguin la carpeta 'corpus_tesi'.
    Si no es troba cap USB amb la carpeta, retorna D:/corpus_tesi (si existeix D:), sinó C:/corpus_tesi.
    """
    usb_devices = []

    # Mètode 1: Usar wmic per detectar discs removibles
    try:
        result = subprocess.run(
            ['wmic', 'logicaldisk', 'get', 'name,driveType', '/format:csv'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:
                parts = line.split(',')
                if len(parts) >= 2:
                    letter = parts[0].strip()
                    drive_type = parts[1].strip()
                    if drive_type == '2' and letter and ':' in letter:
                        usb_devices.append(letter)
    except Exception:
        pass

    # Mètode 2: Powershell per USB removibles
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
    except Exception:
        pass

    # Mètode 3: Unitats disponibles si tot falla
    try:
        available_drives = []
        for letter in 'DEFGHIJKLMNOPQRSTUVWXYZ':
            drive = f"{letter}:"
            if os.path.exists(drive):
                available_drives.append(drive)

        if not usb_devices and available_drives:
            usb_devices = [d for d in available_drives if d.replace(':', '') not in 'CD']
    except Exception:
        pass

    # Eliminar duplicats i ordenar
    usb_devices = list(set(usb_devices))
    usb_devices.sort()

    # Comprovem quin USB té la carpeta 'corpus_tesi'
    for usb in usb_devices:
        corpus_path = os.path.join(usb, 'corpus_tesi')
        if os.path.isdir(corpus_path):
            return corpus_path

    return usb_devices[0]+'/corpus_tesi' if usb_devices else None


# Exemple d'ús
if __name__ == "__main__":
    usb_device = getUSB()
    print(f"Carpeta seleccionada: {usb_device}")
