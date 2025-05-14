import sys
import cv2
import serial
import time
from ultralytics import YOLO
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QSlider, QComboBox, QFrame
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap


class DefenseUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hava Savunma Sistemi Arayüzü")
        self.setGeometry(100, 100, 1280, 750)

        # Arduino bağlantısı (Mac için doğru port)
        try:
            self.arduino = serial.Serial('/dev/cu.usbserial-11420', 9600, timeout=1)
            time.sleep(2)
            print("✅ Arduino bağlantısı kuruldu.")
            print("🔌 Port açık mı:", self.arduino.is_open)
        except Exception as e:
            self.arduino = None
            print("❌ Arduino bağlantısı başarısız:", e)

        # Stil ayarları
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: #ffffff; font-size: 14px; font-family: 'Segoe UI'; }
            QPushButton { background-color: #2e2e2e; border: 1px solid #444; border-radius: 8px; padding: 12px; }
            QPushButton:hover { background-color: #444; }
            QLabel { font-weight: bold; }
            QComboBox { background-color: #2e2e2e; color: #ffffff; padding: 4px; border: 1px solid #444; border-radius: 4px; }
            QSlider::groove:horizontal { height: 8px; background: #333; border-radius: 4px; }
            QSlider::handle:horizontal { background: #00ff00; width: 15px; margin: -5px 0; border-radius: 7px; }
        """)

        # Kamera ekranı
        self.camera_label = QLabel()
        self.camera_label.setFixedSize(1280, 720)
        self.camera_label.setStyleSheet("border: 2px solid #555;")

        # Orta panel
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Manuel Mod", "Otonom Mod"])
        self.slider_label = QLabel("Atış Yasak Alanı (0°-180°):")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(180)
        self.slider.setValue(90)
        self.status_label = QLabel("Durum: Bekleniyor...")

        middle_panel = QVBoxLayout()
        middle_panel.addWidget(QLabel("Mod Seçimi:"))
        middle_panel.addWidget(self.mode_combo)
        middle_panel.addSpacing(20)
        middle_panel.addWidget(self.slider_label)
        middle_panel.addWidget(self.slider)
        middle_panel.addSpacing(30)
        middle_panel.addWidget(self.status_label)
        middle_frame = QFrame()
        middle_frame.setLayout(middle_panel)

        # Sağ panel
        self.start_button = QPushButton("🎯 Takip Et")
        self.start_button.clicked.connect(self.start_tracking)
        self.fire_button = QPushButton("🔥 Ateş Et")
        self.stop_button = QPushButton("⛔ Acil Durdur")
        right_panel = QVBoxLayout()
        right_panel.addWidget(self.start_button)
        right_panel.addWidget(self.fire_button)
        right_panel.addWidget(self.stop_button)
        right_panel.addStretch()
        right_frame = QFrame()
        right_frame.setLayout(right_panel)

        # Ana layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.camera_label)
        main_layout.addSpacing(15)
        main_layout.addWidget(middle_frame)
        main_layout.addSpacing(15)
        main_layout.addWidget(right_frame)
        self.setLayout(main_layout)

        # YOLO modeli yükle
        self.model = YOLO("/Users/ismail/Desktop/Firnas/Firnas/Arayüz/best.pt")

        # Kamera başlat
        self.cap = self.try_open_camera()
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 60)

        # Frame güncelleyici
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def try_open_camera(self):
        for index in range(3):
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                print(f"📷 Kamera {index} başarıyla açıldı.")
                return cap
        raise RuntimeError("Kamera açılamadı. Lütfen bağlantıyı kontrol edin.")

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.status_label.setText("Kamera görüntüsü alınamıyor.")
            print("❌ Kamera görüntüsü alınamadı.")
            return

        height, width, _ = frame.shape
        camera_center_x = width // 2
        results = self.model(frame, verbose=False)[0]

        if results.boxes:
            best_box = max(results.boxes, key=lambda b: b.conf[0])
            x1, y1, x2, y2 = map(int, best_box.xyxy[0])
            target_x = (x1 + x2) // 2
            sapma_px = target_x - camera_center_x

            if abs(sapma_px) < 20:
                komut = "STOP\n"
                yon = "✔ Ortada"
            elif sapma_px > 0:
                komut = "LEFT\n"
                yon = "➡ Sağ"
            else:
                komut = "RIGHT\n"
                yon = "⬅ Sol"

            print(f"[📸] Sapma: {sapma_px}px | Komut: {komut.strip()}")

            if self.arduino and self.arduino.is_open:
                try:
                    self.arduino.write(komut.encode())
                    print(f"[📤] Arduino'ya gönderildi: {komut.strip()}")
                except Exception as e:
                    print("❌ Arduino yazım hatası:", e)
            else:
                print("❌ Arduino bağlantısı yok veya kapalı!")

            self.status_label.setText(f"Hedef: {yon} ({sapma_px}px)")
        else:
            self.status_label.setText("Durum: Hedef tespit edilemedi...")
            print("🔍 Hedef bulunamadı.")

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qt_img = QImage(rgb.data, width, height, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        self.camera_label.setPixmap(pixmap.scaled(self.camera_label.size(), Qt.KeepAspectRatio))

    def start_tracking(self):
        self.status_label.setText("Takip başlatıldı...")

    def closeEvent(self, event):
        self.cap.release()
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
            print("🔌 Arduino bağlantısı kapatıldı.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DefenseUI()
    window.show()
    sys.exit(app.exec_())
