import tkinter as tk
from tkinter import ttk
import mysql.connector

def get_active_rooms():
    # Thực hiện kết nối đến MySQL
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="170801",
        database="karaoke"
    )

    cursor = connection.cursor()

    # Thực hiện truy vấn để lấy dữ liệu từ trường "name" của bảng "room" với điều kiện status = 'active'
    query = "SELECT name FROM room WHERE status = 'active'"
    cursor.execute(query)

    # Lấy tất cả các dòng kết quả
    active_rooms = [row[0] for row in cursor.fetchall()]

    # Đóng kết nối
    cursor.close()
    connection.close()

    return active_rooms

def get_room_service_info(room_name):
    # Thực hiện kết nối đến MySQL
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="170801",
        database="karaoke"
    )

    cursor = connection.cursor()

    # Thực hiện truy vấn để lấy thông tin từ các bảng liên quan
    query = f"""
        SELECT room.name as room_name, service.name as service_name, service_detail.quantity
        FROM room
        JOIN booking_room ON room.id = booking_room.id_room
        JOIN service_detail ON booking_room.id = service_detail.booking_room_id
        JOIN service ON service_detail.id_service = service.id
        WHERE room.name = '{room_name}'
    """
    cursor.execute(query)

    # Lấy tất cả các dòng kết quả
    room_service_info = cursor.fetchall()

    # Đóng kết nối
    cursor.close()
    connection.close()

    return room_service_info

def on_select(event):
    selected_room = room_combobox.get()
    print(f"Selected Room: {selected_room}")

    # Lấy thông tin từ các bảng liên quan
    info = get_room_service_info(selected_room)

    # Xóa dữ liệu cũ trên bảng (nếu có)
    for row in room_table.get_children():
        room_table.delete(row)

    # Hiển thị dữ liệu mới trên bảng
    for row in info:
        room_table.insert("", "end", values=row)

# Tạo cửa sổ tkinter
window = tk.Tk()
window.title("Select Box Example")

# Tạo Combobox
active_rooms = get_active_rooms()
room_combobox = ttk.Combobox(window, values=active_rooms)
room_combobox.pack(pady=10)
room_combobox.bind("<<ComboboxSelected>>", on_select)
d
# Tạo bảng để hiển thị thông tin
room_table = ttk.Treeview(window, columns=("Room Name", "Service Name", "Quantity"), show="headings")
room_table.heading("Room Name", text="Room Name")
room_table.heading("Service Name", text="Service Name")
room_table.heading("Quantity", text="Quantity")
room_table.pack(pady=10)

# Chạy ứng dụng
window.mainloop()
