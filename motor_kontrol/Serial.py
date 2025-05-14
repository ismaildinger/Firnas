import serial
import time

port = '/dev/cu.usbserial-11420'  # doğru portu kullan
baud = 9600

arduino = serial.Serial(port, baud, timeout=1)
time.sleep(2)
print("🔗 Arduino'ya bağlanıldı.")

print("🧪 Komutlar:")
print(" - r = sağa 1 adım")
print(" - l = sola 1 adım")
print(" - sX = X mikro saniye gecikme ile sağa adım (örnek: s800)")
print(" - q = çıkış\n")

while True:
    komut = input("➡️ Komut: ").strip()

    if komut == "q":
        print("🚪 Çıkılıyor...")
        break
    elif komut == "r":
        arduino.write(b"RIGHT\n")
    elif komut == "l":
        arduino.write(b"LEFT\n")
    elif komut.startswith("s"):
        try:
            gecikme = int(komut[1:])
            arduino.write(f"SET{gecikme}\n".encode())
        except:
            print("❌ Gecikme değeri hatalı.")
    else:
        print("⚠️ Bilinmeyen komut.")

    time.sleep(0.05)
    while arduino.in_waiting:
        print(arduino.readline().decode().strip())

arduino.close()
