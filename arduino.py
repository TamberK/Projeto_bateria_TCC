import serial

arduino = serial.Serial('COM13', 9600)  # ajuste a porta
arduino.timeout = 0.01

def ler_arduino():
    if arduino.in_waiting > 0:
        return arduino.readline().decode().strip()
    return None
