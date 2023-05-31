import cv2
from pyzbar.pyzbar import decode
import time

cam = cv2.VideoCapture(0)
cam.set(3, 640)
cam.set(4, 480)

camera = True
while camera:
    success, frame = cam.read()

    for barcode in decode(frame):
        barcode_data = barcode.data.decode('utf-8')
        barcode_type = barcode.type
        print("Barcode Data:", barcode_data)

    cv2.imshow("QR Code Scanner", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    time.sleep(1/10)

cam.release()
cv2.destroyAllWindows()
