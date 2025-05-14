# realtime_test.py -----------------------------------------------------------
from ultralytics import YOLO
import cv2
import time

# ---------------------------------------------------------------------------
# 1)  CONFIG – edit these two lines if your paths or GPU id differ
# ---------------------------------------------------------------------------
WEIGHTS   = "/Users/ismail/Desktop/Firnas/Firnas/models/best2.pt"   # path to your trained model
DEVICE_ID = 0                                     # 0 = first CUDA GPU, -1 = CPU
CONF_TH   = 0.25                                  # confidence threshold

# ---------------------------------------------------------------------------
model = YOLO(WEIGHTS)
model.to("cpu")

cap = cv2.VideoCapture(0)        # 0 = default webcam
assert cap.isOpened(), "❌  Cannot open camera"

prev = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera read failed, exiting …")
        break

    # Run inference (resize handled internally, returns a Results list)
    results = model(frame, imgsz=640, conf=CONF_TH)

    # Plot the first (and only) result onto the original frame
    annotated_frame = results[0].plot()

    # -----------------------------------------------------------------------
    # FPS overlay
    now  = time.time()
    fps  = 1 / (now - prev)
    prev = now
    cv2.putText(annotated_frame, f"{fps:0.1f} FPS",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow("YOLOv8 real‑time", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):   # press 'q' to quit
        break

cap.release()
cv2.destroyAllWindows()