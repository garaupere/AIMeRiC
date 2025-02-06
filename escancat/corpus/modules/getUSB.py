import subprocess


def getUSB():
    """Llista els dispositius USB connectats a l'ordinador."""
    try:
        # Executa la comanda 'wmic logicaldisk get caption,description' per obtenir informació dels dispositius
        result = subprocess.run(['wmic', 'logicaldisk', 'get', 'caption,description'], capture_output=True, text=True)
        output = result.stdout

        # Filtra les línies que contenen 'Removable Disk'
        usb_devices = [line.split()[0] for line in output.splitlines() if 'Removable Disk' in line]

        return usb_devices[0]
    except Exception as e:
        print(f"Error! No s'ha detectat cap memòria externa: {e}")
        return None


# Exemple d'ús
if __name__ == "__main__":
    usb_devices = getUSB()
    if usb_devices:
        print("Dispositius USB connectats:", usb_devices)
    else:
        print("No s'han detectat dispositius USB.")
