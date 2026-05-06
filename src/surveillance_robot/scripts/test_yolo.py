#!/usr/bin/env python3
from ultralytics import YOLO
import cv2

model = YOLO('yolov8n.pt')

# Ouvre la webcam (0 = webcam par défaut)
cap = cv2.VideoCapture(0)

print("Démarrage de la détection... Appuie sur Q pour quitter")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)
    annotated = results[0].plot()

    for result in results:
        for box in result.boxes:
            class_name = model.names[int(box.cls[0])]
            confidence = float(box.conf[0])
            if class_name == 'person' and confidence > 0.5:
                print(f'🚨 INTRUSION DÉTECTÉE : {class_name} ({confidence:.0%})')

    cv2.imshow('YOLOv8 Surveillance', annotated)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()