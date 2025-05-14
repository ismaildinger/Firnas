import cv2

def kamera_ac():
    for i in range(3):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Kamera {i} acildi.")
            return cap
    raise RuntimeError("Kamera bulunamadi")
