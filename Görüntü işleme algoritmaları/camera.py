import cv2

cap = cv2.VideoCapture(0)  # 0 = /dev/video0
while True:
    ret, frame = cap.read()
    if ret:
        cv2.imshow("USB Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
