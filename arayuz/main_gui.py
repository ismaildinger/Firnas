from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QComboBox, QFrame
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from yapay_zeka.yolo_model import tespit_et
from yapay_zeka.hedef_analiz import sapma_hesapla
from motor_kontrol.motor_serial import MotorKontrol
from utils.kamera import kamera_ac
import cv2, time

class DefenseUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hava Savunma Sistemi Arayüzü")
        self.setGeometry(100, 100, 1280, 750)

        self.motor = MotorKontrol()
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: #ffffff; font-size: 14px; font-family: 'Segoe UI'; }
            QPushButton { background-color: #2e2e2e; border: 1px solid #444; border-radius: 8px; padding: 12px; }
            QPushButton:hover { background-color: #444; }
            QLabel { font-weight: bold; }
            QComboBox { background-color: #2e2e2e; color: #ffffff; padding: 4px; border: 1px solid #444; border-radius: 4px; }
            QSlider::groove:horizontal { height: 8px; background: #333; border-radius: 4px; }
            QSlider::handle:horizontal { background: #00ff00; width: 15px; margin: -5px 0; border-radius: 7px; }
        """)

        self.camera_label = QLabel()
        self.camera_label.setFixedSize(1280, 720)
        self.camera_label.setStyleSheet("border: 2px solid #555;")

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

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.camera_label)
        main_layout.addSpacing(15)
        main_layout.addWidget(middle_frame)
        main_layout.addSpacing(15)
        main_layout.addWidget(right_frame)
        self.setLayout(main_layout)

        self.cap = kamera_ac()
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 60)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.status_label.setText("Kamera görüntüsü alınamıyor.")
            return

        height, width, _ = frame.shape
        results = tespit_et(frame)

        if results.boxes:
            best_box = max(results.boxes, key=lambda b: b.conf[0])
            x1, y1, x2, y2 = map(int, best_box.xyxy[0])
            komut, sapma = sapma_hesapla(width, x1, x2)
            self.motor.gonder(komut)
            self.status_label.setText(f"Hedef: {komut.strip()} ({sapma}px)")
        else:
            self.status_label.setText("Durum: Hedef tespit edilemedi...")

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qt_img = QImage(rgb.data, width, height, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        self.camera_label.setPixmap(pixmap.scaled(self.camera_label.size(), Qt.KeepAspectRatio))

    def start_tracking(self):
        self.status_label.setText("Takip başlatıldı...")

    def closeEvent(self, event):
        self.cap.release()
        if self.motor.arduino and self.motor.arduino.is_open:
            self.motor.arduino.close()
            print("🔌 Arduino bağlantısı kapatıldı.")
