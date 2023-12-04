import cv2
import tkinter as tk
from tkinter import Entry, Canvas
from pyzbar.pyzbar import decode
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import Entry, Canvas
from PIL import Image, ImageTk
import cv2

def create_qr_scanner_app(root):
    root.title("QR Scanner")

    entry_var = tk.StringVar()
    entry = Entry(root, textvariable=entry_var, width=40)
    entry.pack(pady=10)

    start_scanning_button = tk.Button(root, text="Start Scanning", command=lambda: start_scanning(root, entry_var, canvas, cap))
    start_scanning_button.pack(pady=10)

    canvas = Canvas(root, width=640, height=480)
    canvas.pack()

    cap = cv2.VideoCapture(0)

    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(cap, root))

    return root, entry_var, entry, canvas, cap

def start_scanning(root, entry_var, canvas, cap):
    scanning = True
    root.after(10, lambda: scan(root, entry_var, canvas, cap, scanning))

def scan(root, entry_var, canvas, cap, scanning):
    if scanning:
        _, frame = cap.read()
        decoded_objects = decode(frame)

        for obj in decoded_objects:
            data = obj.data.decode("utf-8")
            entry_var.set(data)

        if _:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            photo = ImageTk.PhotoImage(image=image)
            canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            canvas.image = photo

        root.after(10, lambda: scan(root, entry_var, canvas, cap, scanning))

def on_closing(cap, root):
    cap.release()
    root.destroy()

# Ví dụ cách sử dụng
root = tk.Tk()
create_qr_scanner_app(root)
root.mainloop()

