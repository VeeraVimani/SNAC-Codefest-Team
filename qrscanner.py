import cv2
from pyzbar import pyzbar
import os

os.environ['PYZBAR_LIBRARY'] = '/opt/homebrew/opt/zbar/lib/libzbar.dylib'

from pyzbar import pyzbar

def scan_qr():
    cap = cv2.VideoCapture(0)  # Open default camera

    print("Scanning for QR codes. Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect QR codes in the frame
        decoded_objects = pyzbar.decode(frame)
        for obj in decoded_objects:
            qr_data = obj.data.decode("utf-8")
            qr_type = obj.type
            print(f"Detected {qr_type}: {qr_data}")

            # Draw rectangle around QR code
            (x, y, w, h) = obj.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, qr_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow("QR Scanner", frame)

        # Quit when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

scan_qr()
