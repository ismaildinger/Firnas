from ultralytics import YOLO
import os

# Bu dosyanın bulunduğu dizine göre model yolunu belirle
base_dir = os.path.dirname(os.path.dirname(__file__))
model_path = os.path.join(base_dir, "models", "best.pt")

model = YOLO(model_path)

def tespit_et(frame):
    return model(frame, verbose=False)[0]
