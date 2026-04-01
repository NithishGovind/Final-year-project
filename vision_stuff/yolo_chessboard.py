from ultralytics import YOLO
import cv2

# load model
model = YOLO("/home/mil/Documents/Final year project/vision_stuff/best.pt")   # your weights

# open webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # inference
    results = model(frame, imgsz=416, conf=0.3)

    # draw detections
    annotated = results[0].plot()

    cv2.imshow("YOLO Chess Detection", annotated)

    if cv2.waitKey(1) & 0xFF == 27:   # press ESC to exit
        break

cap.release()
cv2.destroyAllWindows()