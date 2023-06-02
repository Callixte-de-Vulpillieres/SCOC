import cv2
from pyzbar.pyzbar import decode
import time


def recognition(cam):
    success, frame = cam.read()
    codes = []
    for barcode in decode(frame):
        barcode_data = barcode.data.decode('utf-8')
        codes.append(barcode_data)
        print("Barcode Data:", barcode_data)

    # cv2.waitKey(1)
    if len(codes) > 0:
        return True, codes
    else:
        return False, None


if __name__ == '__main__':
    print(recognition())
