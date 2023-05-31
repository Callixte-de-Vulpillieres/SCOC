import cv2
from pyzbar.pyzbar import decode
import time


def recognition():
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)
    fps = 10  # frame per second
    camera = True
    result = ""
    while camera:
        success, frame = cam.read()

        for barcode in decode(frame):
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type
            result = barcode_data
            print("Barcode Data:", result)
            return (result, True)
        #cv2.imshow("QR Code Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(1/fps)
    cam.release()
    # cv2.destroyAllWindows()


recognition()
