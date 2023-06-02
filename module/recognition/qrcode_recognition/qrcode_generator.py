import qrcode


def generate_qrcode(data, filename):
    qr = qrcode.QRCode(version=2,
                       error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=10,
                       border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)


# Example usage
data = "Hello, World!"
filename = "qrcode.png"
generate_qrcode(data, filename)
print(f"A QR code for '{data}' has been generated and saved as '{filename}'")
