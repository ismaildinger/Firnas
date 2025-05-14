import serial, time

class MotorKontrol:
    def __init__(self, port="/dev/cu.usbserial-11420", baud=9600):
        try:
            self.arduino = serial.Serial(port, baud, timeout=1)
            time.sleep(2)
            print("Arduino baglantisi basarili.")
        except Exception as e:
            print("Baglanti hatasi:", e)
            self.arduino = None

    def gonder(self, komut):
        if self.arduino and self.arduino.is_open:
            try:
                self.arduino.write((komut + "\n").encode())
                print(f"Gonderildi: {komut}")
            except Exception as e:
                print("Yazma hatasi:", e)
