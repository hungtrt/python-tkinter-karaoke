import os

import cv2
import mysql.connector
import qrcode
from pyzbar.pyzbar import decode
from unidecode import unidecode


def connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="170801",
        database="karaoke"
    )
    return conn


def getCustomerByPhone(phone):
    conn = connection()
    cursor = conn.cursor()
    query = "SELECT name_id, name, phone, address, type FROM customer where phone = %s"
    cursor.execute(query, (phone,))
    results = cursor.fetchall()
    conn.close()
    return results


def printQR(phone):
    data = getCustomerByPhone(phone)

    name = data[0][1]
    name_convert = name.split()
    first_name = name_convert[-1]
    last_name = name_convert[0]
    first_name_without_diacritics = ''.join(char for char in first_name if char.isalnum())
    last_name_without_diacritics = ''.join(char for char in last_name if char.isalnum())
    name_result = first_name_without_diacritics + last_name_without_diacritics
    name_result = unidecode(name_result)

    name_id = name_result + phone[-4:]

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(name_id)
    qr.make(fit=True)

    # Tạo ảnh QR
    img = qr.make_image(fill_color="black", back_color="white")

    # Lưu ảnh QR với tên file "sdt.png"
    folder_path = "E:\\python-tkinter-karaoke\\card\\QR Photos"
    img.save(os.path.join(folder_path, f"{name_id}.png"))

