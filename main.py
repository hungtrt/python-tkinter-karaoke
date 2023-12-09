import tkinter as tk
from abc import ABC, abstractmethod
from collections import OrderedDict
from tkinter import ttk, font

import cv2
import mysql.connector
from tkinter import messagebox
from datetime import datetime
from tkinter import StringVar
import locale
import pandas as pd

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from CheckoutFunction import get_incentives_percent
from card.PrintMemberCard import printCardMembership
from card.scan import start_scanning, on_closing
from clear import clear_textfields, clear_cobobox, clear_cobobox_and_textfield, clear_checkout_room, \
    clearNameServiceAndQuantity, clear_textfields_update
from connectionDB import connection
from customer_page import removeCustomerByPhone, add_customer, update_customer
from oop import readFileAndDisplay, deleteDataInFile, updateDataInFile, addPersonnel
from pdf.invoice_data import printFuncInvoice, id_room, id_booking_room
from room_calculation import total_for_frame_time_from_database
from service_page import returnProduct, removeProduct
from card.main import printQR


# Đọc dữ liệu bảng customer
def refreshTable(my_tree):
    for data in my_tree.get_children():
        my_tree.delete(data)

    new_data = read()

    for array in new_data:
        my_tree.insert(parent='', index='end', iid=array, text="", values=(array), tag="orow")

    my_tree.tag_configure('orow', background='#EEEEEE', font=('Arial', 12))


# Đọc dữ liệu trong bảng customer
def read():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name,name_id, phone, address, type, customer_incentives  FROM customer where name != 'Vãng Lai' order by customer_incentives desc")
    results = cursor.fetchall()
    conn.commit()
    conn.close()
    return results


# Ghi dữ liệu vào bảng customer
def add_customer_event(cus_table, nameEntry, phoneEntry, addressEntry, amountConsumedEntry, id_lb):
    add_customer(nameEntry, phoneEntry, addressEntry, amountConsumedEntry)
    phone = str(phoneEntry.get())
    printQR(phone)
    refreshTable(cus_table)
    clear_textfields(nameEntry, phoneEntry, addressEntry, amountConsumedEntry, id_lb)


def update_customer_event(cus_table, nameEntry, phoneEntry, addressEntry, id_lb):
    update_customer(nameEntry, phoneEntry, addressEntry, id_lb)
    refreshTable(cus_table)
    new_data = read()
    tuple_at_index_1 = new_data[1]
    element_at_index_1 = tuple_at_index_1[1]
    id_lb.config(text=element_at_index_1)
    phone = str(phoneEntry.get())
    printQR(phone)
    clear_textfields_update(nameEntry, phoneEntry, addressEntry, id_lb)


# Hàm setup cho frame nằm giữa màn hình khi khởi động
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")


# SỬ LÝ TRANG ĐẶT PHÒNG

# Đọc dữ liệu bảng room chưa xử dụng
def loadTableRoomNull(my_tree):
    for data in my_tree.get_children():
        my_tree.delete(data)

    new_data = read_room()

    for array in new_data:
        my_tree.insert(parent='', index='end', iid=array, text="", values=(array), tag="orow")

    my_tree.tag_configure('orow', background='#EEEEEE', font=('Arial', 12))


# Lấy thời gian hiện tại
def get_current_hour():
    return datetime.now().hour


# Khung giờ tiếp theo
def determine_time_slot():
    current_hour = datetime.now().hour

    if 6 <= current_hour < 17:
        return 1  # Khung giờ 1: từ 6h đến 16h59p
    elif 17 <= current_hour < 22:
        return 2  # Khung giờ 2: từ 17h đến 21h59p
    else:
        return 3  # Khung giờ 3: từ 22h đến 5h59p sáng hôm sau


# Đọc dữ liệu từ bảng phòng
def read_room():
    conn = connection()
    cursor = conn.cursor()

    query = """
        SELECT room.name, room.volume, room.description, room.type_room, room_rates.unit_price
        FROM room
        LEFT JOIN room_rates ON room.id = room_rates.id_room
        WHERE room.status = 'null'
          AND room_rates.time_slot = (
            CASE
              WHEN %s >= 6 AND %s < 17 THEN 1
              WHEN %s >= 17 AND %s < 22 THEN 2
              ELSE 3
            END
          )
        ORDER BY room_rates.unit_price DESC;
    """

    current_hour = get_current_hour()
    cursor.execute(query, (current_hour, current_hour, current_hour, current_hour))
    results_1 = cursor.fetchall()

    next_time_slot = determine_time_slot() + 1
    query = """
    SELECT room_rates.unit_price
        FROM room
        LEFT JOIN room_rates ON room.id = room_rates.id_room
        WHERE room.status = 'null'
          AND room_rates.time_slot = %s
        ORDER BY room_rates.unit_price DESC;
    """

    cursor.execute(query, (next_time_slot,))
    results_2 = cursor.fetchall()

    conn.close()

    result = []
    min_length = min(len(results_1), len(results_2))

    for i in range(min_length):
        result.append(results_1[i] + (results_2[i][0],))
    # print(results_1)
    # print(results_2)
    # print(result)
    return result


# Ghi dữ liệu vào bảng
def saveBookingRoom(booking_table, room_select_box, cus_select_box):
    room_name = room_select_box.get()
    customer_name = cus_select_box.get()
    created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not (room_name and customer_name):
        messagebox.showinfo("Error", "Bạn chưa nhập đủ thông tin!")
        return
    else:
        try:
            # Lấy id của phòng từ tên phòng
            conn = connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM room WHERE name = %s", (room_name,))
            result = cursor.fetchone()

            if result is not None:
                room_id = result[0]

                # Lấy id của khách hàng từ tên khách hàng
                cursor.execute("SELECT id FROM customer WHERE phone = %s or name_id = %s",
                               (customer_name, customer_name))
                result = cursor.fetchone()

                if result is not None:
                    customer_id = result[0]

                    # Lưu thông tin vào bảng booking_room
                    cursor.execute("INSERT INTO booking_room (id_room, id_customer, created_date) VALUES (%s, %s, %s)",
                                   (room_id, customer_id, created_date))

                    # Cập nhật trạng thái của phòng thành 'active'
                    cursor.execute("UPDATE room SET status = 'active' WHERE id = %s", (room_id,))

                    conn.commit()
                    messagebox.showinfo("Success", "Đặt Phòng Thành Công!")
                    clear_cobobox(room_select_box, cus_select_box)
                else:
                    messagebox.showinfo("Error", "Không tìm thấy thông tin khách hàng!")
            else:
                messagebox.showinfo("Error", "Không tìm thấy thông tin phòng!")

            conn.close()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            messagebox.showinfo("Error", "Vui lòng thử lại")
            return

        loadTableRoomNull(booking_table)


# KẾT THÚC XỬ LÝ TRANG ĐẶT PHÒNG

# BẮT ĐẦU XỬ LÝ TRANG QUẢN LÝ PHÒNG ĐANG SỬ DỤNG

# Đọc dữ liệu bảng customer
def loadDataRoomUsing(my_tree):
    for data in my_tree.get_children():
        my_tree.delete(data)

    new_data = read_data_room_using()

    if new_data is not None:
        for array in new_data:
            my_tree.insert(parent='', index='end', iid=array, text="", values=(array), tag="orow")

        my_tree.tag_configure('orow', background='#EEEEEE', font=('Arial', 12))
    else:
        print("Failed to load data.")


# Đọc dữ liệu
def read_data_room_using():
    try:
        conn = connection()
        cursor = conn.cursor()
        query = """
                    SELECT
                           room.name AS room_name,
                           customer.name AS customer_name,
                           booking_room.created_date,
                           TIMEDIFF(NOW(), booking_room.created_date) AS duration,
                           room.type_room
                       FROM
                           booking_room
                       JOIN room ON booking_room.id_room = room.id
                       JOIN customer ON booking_room.id_customer = customer.id
                       where booking_room.ended_time is null and room.status = 'active'
                       ORDER BY duration Desc;
                   """
        cursor.execute(query)
        booking_info = cursor.fetchall()
        conn.close()
        return booking_info
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


# XỬ LÝ TRANG DỊCH VỤ
def get_active_rooms():
    # Thực hiện kết nối đến MySQL
    conn = connection()
    cursor = conn.cursor()

    # Thực hiện truy vấn để lấy dữ liệu từ trường "name" của bảng "room" với điều kiện status = 'active'
    query = "SELECT name FROM room WHERE status = 'active'"
    cursor.execute(query)

    # Lấy tất cả các dòng kết quả
    active_rooms = [row[0] for row in cursor.fetchall()]

    # Đóng kết nối
    cursor.close()
    return active_rooms


# Show dữ liệu khi chọn vào combobox
def get_room_service_info(room_name):
    # Thực hiện kết nối đến MySQL
    conn = connection()

    cursor = conn.cursor()

    # Thực hiện truy vấn để lấy thông tin từ các bảng liên quan
    query = f"""
        SELECT room.name as room_name, service.name as service_name, service_detail.quantity, service_detail.unit
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
    return room_service_info


def on_select(event, room_combobox, ser_table):
    selected_room = room_combobox.get()

    # Lấy thông tin từ các bảng liên quan
    info = get_room_service_info(selected_room)

    # Xóa dữ liệu cũ trên bảng (nếu có)
    for row in ser_table.get_children():
        ser_table.delete(row)

    # Hiển thị dữ liệu mới trên bảng
    for row in info:
        ser_table.insert("", "end", values=row)


# Lưu service
def update_table(ser_table, room_combobox):
    selected_room = room_combobox.get()

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="170801",
        database="karaoke"
    )

    cursor = conn.cursor()
    # Truy vấn thông tin từ các bảng tương ứng
    query = """
            SELECT room.name, service.name, service.unit, service_detail.quantity
            FROM room
            JOIN booking_room ON room.id = booking_room.id_room
            JOIN service_detail ON booking_room.id = service_detail.booking_room_id
            JOIN service ON service_detail.id_service = service.id
            WHERE room.name = %s and booking_room.ended_time is null
        """
    cursor.execute(query, (selected_room,))
    data = cursor.fetchall()

    # Xóa dữ liệu cũ trên Treeview
    ser_table.delete(*ser_table.get_children())

    # Hiển thị dữ liệu mới
    for row in data:
        ser_table.insert("", "end", values=row)


def saveService(booking_table, room_select_box, service_select_box, quantity_entry):
    room_name = room_select_box.get()
    service_name = service_select_box.get()
    quantity = int(quantity_entry.get()) if quantity_entry.get() else 0
    created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not (room_name and service_name and quantity_entry):
        messagebox.showinfo("Error", "Bạn chưa nhập đủ thông tin!")
        return
    else:
        try:
            # Tìm Id của Phòng trong bảng room
            conn = connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM room WHERE name = %s", (room_name,))
            result = cursor.fetchone()

            if result is not None:
                room_id = result[0]

                # Tìm Id của Phòng trong bảng booking_room
                cursor.execute(
                    "SELECT id, id_room, created_date, ended_time FROM booking_room WHERE id_room = %s AND ended_time IS NULL",
                    (room_id,))
                result = cursor.fetchone()

                if result is not None:
                    booking_room_id = result[0]

                    # Tìm Id của Dịch vụ trong bảng service
                    cursor.execute("SELECT id FROM service WHERE name = %s", (service_name,))
                    result = cursor.fetchone()

                    if result is not None:
                        service_id = result[0]

                        cursor.execute(
                            "select quantity from service_detail where booking_room_id = %s and id_service = %s",
                            (booking_room_id, service_id))
                        result = cursor.fetchone()
                        if result is not None:
                            quantity_total = result[0] + quantity
                            cursor.execute(
                                "UPDATE service_detail SET quantity = %s where booking_room_id = %s and id_service = %s",
                                (quantity_total, booking_room_id, service_id))
                        else:
                            # Lưu thông tin vào bảng service_detail
                            cursor.execute(
                                "INSERT INTO service_detail (id_service, booking_room_id, quantity, created_date) VALUES (%s, %s, %s, %s)",
                                (service_id, booking_room_id, quantity, created_date))

                        # Cập nhật updated_date của booking room
                        cursor.execute(
                            "UPDATE booking_room SET updated_date = NOW() WHERE id = %s AND updated_date IS NULL",
                            (booking_room_id,))
                        conn.commit()
                        messagebox.showinfo("Success", "Thêm Dịch Vụ Thành Công!")
                        clearNameServiceAndQuantity(service_select_box, quantity_entry)
                    else:
                        messagebox.showinfo("Error", "Không tìm thấy thông tin dịch vụ!")
                else:
                    messagebox.showinfo("Error", "Không tìm thấy thông tin phòng!")
            else:
                messagebox.showinfo("Error", "Không tìm thấy thông tin phòng!")

            conn.close()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            messagebox.showinfo("Error", "Vui lòng thử lại")
            return

        update_table(booking_table, room_select_box)


# KẾT THÚC XỬ LÝ TRANG QUẢN LÝ PHÒNG ĐANG SỬ DỤNG


root = tk.Tk()
# root.geometry('1000x600')
root.title('Đào Tươi Karaoke')

window_width = 1200
window_height = 680
root.geometry(f"{window_width}x{window_height}")

center_window(root, window_width, window_height)


# Hàm Đặt Phòng
def handle_click_table_booking(cus_table, combobox_room):
    global current_id
    item = cus_table.selection()[0]
    data = cus_table.item(item, 'values')
    current_id = data[0]
    combobox_room.delete(0, tk.END)
    combobox_room.insert(0, data[0])


def booking_page():
    booking_frame = tk.Frame(main_frame)

    head_frame = tk.Frame(booking_frame, bg='#ffffff')

    heading_lb = tk.Label(booking_frame, text="Quản Lý Đặt Phòng", font=('Bold', 22), bg='#3a7ca5', fg='white')
    heading_lb.pack(fill=tk.X, pady=0)

    # Label Tên Phòng Trống
    customer_name_lb = tk.Label(head_frame, text='Tên Phòng: ', font=('Bold', 12), bg="#e7d7c1")
    customer_name_lb.place(x=20, y=25, width=160, height=30)
    # Select box
    connection = mysql.connector.connect(host='localhost', user='root',
                                         password='170801', database='karaoke')
    c = connection.cursor()
    c.execute("SELECT name FROM `room` where status = 'null'")
    options = [row[0] for row in c.fetchall()]
    selected_room = StringVar(head_frame)
    combobox_room = ttk.Combobox(head_frame, textvariable=selected_room, values=options,
                                 font=('verdana', 13))
    combobox_room.place(x=200, y=25, width=350, height=30)

    # Label Khách Hàng
    customer_phone_lb = tk.Label(head_frame, text='Khách Hàng: ', font=('Bold', 12), bg="#e7d7c1")
    customer_phone_lb.place(x=20, y=75, width=160, height=30)
    canvas = tk.Canvas(root, width=640, height=480)
    canvas.pack()
    cap = cv2.VideoCapture(0)
    # Select box
    c.execute("SELECT name_id FROM `customer` order by type desc")
    options = [row[0] for row in c.fetchall()]
    selected_cus = StringVar(head_frame)
    combobox_cus = ttk.Combobox(head_frame, textvariable=selected_cus, values=options,
                                font=('verdana', 13))
    combobox_cus.place(x=200, y=75, width=350, height=30)

    # Nút lưu thông tin
    save_btn = tk.Button(head_frame, text='Lưu', font=('Bold', 12), bg='#3a7ca5', fg='white',
                         command=lambda: saveBookingRoom(cus_table, combobox_room, combobox_cus))
    save_btn.place(x=570, y=70, width=80, height=40)
    # Nút clear thông tin
    clear_btn = tk.Button(head_frame, text='Làm sạch', font=('Bold', 12), bg='#3a7ca5', fg='white',
                          command=lambda: clear_cobobox(
                              combobox_cus,
                              combobox_room))
    clear_btn.place(x=660, y=70, width=80, height=40)
    # Quét Qr
    scan_btn = tk.Button(head_frame, text='Quét Mã', font=('Bold', 12), bg='#3a7ca5', fg='white',
                         command=lambda: start_scanning(root, combobox_cus, canvas, cap))
    scan_btn.place(x=750, y=70, width=80, height=40)

    head_frame.pack(pady=0)
    head_frame.pack_propagate(False)
    head_frame.configure(width=1038, height=120)

    # Frame mới cho nút tìm kiếm
    search_bar_frame = tk.Frame(booking_frame, bg='#3a7ca5')
    search_lb = tk.Label(search_bar_frame, text="Danh sách Phòng Trống", font=('Bold', 12))
    search_lb.place(x=20, y=2, height=30)

    search_bar_frame.pack(pady=0)
    search_bar_frame.pack_propagate(False)
    search_bar_frame.configure(width=1038, height=40)

    # Frame mới cho bảng thông tin đặt phòng
    table_cus_frame = tk.Frame(booking_frame, bg='white')

    cus_table = ttk.Treeview(table_cus_frame)
    cus_table.place(x=0, y=10, width=1000, height=360)

    cus_table['column'] = ['Name', 'Volume', 'Description', 'Status', 'CurrentPrice', 'NextPrice']
    cus_table.column('#0', anchor=tk.W, width=0, stretch=tk.NO)

    cus_table.column('Name', anchor=tk.W, width=60)
    cus_table.column('Volume', anchor=tk.W, width=50)
    cus_table.column('Description', anchor=tk.W, width=310)
    cus_table.column('Status', anchor=tk.W, width=30)
    cus_table.column('CurrentPrice', anchor=tk.W, width=40)
    cus_table.column('NextPrice', anchor=tk.W, width=120)

    heading_font = ("Arial", 11, "bold")
    style = ttk.Style()
    style.configure("Treeview.Heading", font=heading_font)
    cus_table.heading('Name', text='Tên Phòng', anchor=tk.W)
    cus_table.heading('Volume', text='Lượng người', anchor=tk.W)
    cus_table.heading('Description', text='Mô Tả Phòng', anchor=tk.W)
    cus_table.heading('Status', text='Loại Phòng', anchor=tk.W)
    cus_table.heading('CurrentPrice', text='Giá Hiện tại', anchor=tk.W)
    cus_table.heading('NextPrice', text='Giá Khung Giờ Kế Tiếp', anchor=tk.W)

    cus_table.bind('<ButtonRelease-1>', lambda event: handle_click_table_booking(cus_table, combobox_room))

    # đọc ra dữ liệu từ hàm loadTableRoomNull()
    loadTableRoomNull(cus_table)

    table_cus_frame.pack(pady=5)
    table_cus_frame.pack_propagate(False)
    table_cus_frame.configure(width=1038, height=420, padx=20)
    # kết thúc
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(cap, root))
    booking_frame.pack(pady=0)


# Hàm Phòng Đang Sử Dụng


def on_combobox_checkout_select(event, room_combobox,
                                room_checkout_result_label,
                                money_service_label,
                                incentives_label,
                                incentives_percent_label,
                                total_label,
                                final_label):
    selected_index = room_combobox.get()

    if selected_index != -1:
        selected_room_id = get_room_id(selected_index)
        result_service = get_total_service(selected_index)
        result_incentives = get_incentives_percent(selected_index)
        result_total = get_result_total(selected_index)
        incentives = get_incentives(selected_index)
        final = get_final_price(selected_index)

        result_service = format_currency(result_service)
        result_price_room = format_currency(selected_room_id)
        result_total_price = format_currency(result_total)
        result_incentives_price = format_currency(incentives)
        result_final = format_currency(final)

        room_checkout_result_label.config(text=result_price_room)
        incentives_percent_label.config(text=result_incentives)
        money_service_label.config(text=result_service)
        total_label.config(text=result_total_price)
        incentives_label.config(text=result_incentives_price)
        final_label.config(text=result_final)


def get_final_price(selected_index):
    total = get_result_total(selected_index) - get_incentives(selected_index)
    # total = round(total, -3)
    return total


def get_incentives(selected_index):
    incentives = (get_result_total(selected_index) * get_incentives_percent(selected_index)) / 100
    return incentives


def format_currency(amount):
    locale.setlocale(locale.LC_ALL, 'vi_VN.UTF-8')  # Đặt locale thành vi_VN để sử dụng dấu phân cách ","
    formatted_amount = locale.format_string('%d', amount, grouping=True)
    return f"{formatted_amount} Đồng"


def get_room_id(selected_index):
    # print(selected_index)
    result = total_for_frame_time_from_database(selected_index)
    return result


def get_total_service(selected_index):
    # Thực hiện kết nối đến MySQL
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="170801",
        database="karaoke"
    )

    try:
        cursor = connection.cursor()

        # Thực hiện truy vấn để lấy dữ liệu từ trường "id_room" của bảng "booking_room" với điều kiện status = 'active'
        cursor.execute("SELECT id FROM room WHERE name = %s", (selected_index,))
        selected_room_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM booking_room WHERE id_room = %s and ended_time is null",
                       (selected_room_id,))
        selected_id = cursor.fetchone()[0]

        cursor.execute("SELECT id_service, quantity FROM service_detail WHERE booking_room_id = %s", (selected_id,))
        service_details = cursor.fetchall()
        total_price = 0

        # Duyệt qua mỗi dòng trong service_details
        for service_id, quantity in service_details:
            # Lấy giá và tên của service từ bảng service
            cursor.execute("SELECT name, unit_price FROM service WHERE id = %s", (service_id,))
            service_info = cursor.fetchone()

            if service_info:
                service_name, unit_price = service_info
                # Tính giá của dịch vụ (giá * số lượng) và cộng vào tổng giá
                service_total_price = unit_price * quantity
                total_price += service_total_price

        return total_price

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Đóng kết nối
        connection.close()


def get_result_total(selected_index):
    total = get_room_id(selected_index) + get_total_service(selected_index)
    return total


def checkout(room_combobox, cus_table):
    try:
        name_room = room_combobox.get()
        if not name_room:
            messagebox.showinfo("Error", "Bạn chưa nhập đủ thông tin!")
            return

        conn = connection()
        with conn.cursor() as cursor:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # ... (the rest of your code)
            # Lấy id phòng từ tên phòng
            cursor.execute("SELECT id FROM room WHERE name = %s", (name_room,))
            room_id = cursor.fetchone()[0]

            # Lấy id booking room từ id_room
            cursor.execute("SELECT id FROM booking_room WHERE id_room = %s and ended_time is null", (room_id,))
            booking_room_id = cursor.fetchone()[0]

            # Lấy id customer room từ bảng ghi booking_room
            cursor.execute("SELECT id_customer FROM booking_room WHERE id = %s", (booking_room_id,))
            customer_id = cursor.fetchone()[0]

            # Lấy tiền thanh toán
            cursor.execute("SELECT amount_consumed FROM customer WHERE id = %s", (customer_id,))
            amount_consumed_db = cursor.fetchone()[0]
            amount_consumed = get_final_price(name_room)
            total_amount_consumed = amount_consumed_db + amount_consumed

            # Cập nhật giờ kết thúc trong bảng booking_room
            # cursor.execute("UPDATE booking_room SET ended_time = %s WHERE id = %s", (now, booking_room_id))

            # Cập nhật trạng thái phòng (trống)
            cursor.execute("UPDATE room SET status = 'null' WHERE id = %s", (room_id,))

            # Cập nhật số tiền tiêu thụ, cập nhật phần trăm, loại khách hàng của khách hàng
            # Nếu là khách vãng lai thì không làm gì
            # Nếu là khách hàng thân thiết thì xử lý
            cursor.execute("SELECT type FROM customer WHERE id = %s", (customer_id,))
            type_customer = cursor.fetchone()[0]

            if type_customer != 'Visiting':
                cursor.execute("UPDATE customer SET amount_consumed = %s WHERE id = %s",
                               (total_amount_consumed, customer_id))
                if total_amount_consumed >= 5000000:
                    cursor.execute("UPDATE customer SET type = 'Vip3', customer_incentives = 10 WHERE id = %s",
                                   (customer_id,))
                elif total_amount_consumed >= 3000000:
                    cursor.execute("UPDATE customer SET type = 'Vip2', customer_incentives = 8 WHERE id = %s",
                                   (customer_id,))
                elif total_amount_consumed >= 1500000:
                    cursor.execute("UPDATE customer SET type = 'Vip1', customer_incentives = 5 WHERE id = %s",
                                   (customer_id,))
            else:
                pass

            # Lưu bảng ghi vào bảng bill
            cursor.execute(
                "INSERT INTO bill (id_booking_room, created_date) VALUES (%s, %s)",
                (booking_room_id, now))

        conn.commit()
        messagebox.showinfo("Success", "Thanh Toán Thành Công!")
        loadDataRoomUsing(cus_table)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        messagebox.showinfo("Error", "Vui lòng thử lại")
    finally:
        conn.close()


def printInvoice(room_combobox):
    room_name = room_combobox.get()
    printFuncInvoice(room_name)

    conn = connection()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    id_room_data = id_room(room_name)
    id_booking_room_data = id_booking_room(id_room_data)
    cursor.execute("UPDATE booking_room SET ended_time = %s WHERE id = %s", (now, id_booking_room_data))
    conn.commit()
    messagebox.showinfo("Success", "Xuất Hóa Đơn Thành Công!")


def exportFileEvent(customer_phone_text_field):
    phone = customer_phone_text_field.get()
    printCardMembership(phone)


def room_page():
    room_frame = tk.Frame(main_frame)

    head_frame = tk.Frame(room_frame, bg='#ffffff')

    heading_lb = tk.Label(room_frame, text="THANH TOÁN PHÒNG", font=('Bold', 22), bg='#3a7ca5', fg='white')
    heading_lb.pack(fill=tk.X, pady=0)

    # Label và textfields 
    customer_name_lb = tk.Label(head_frame, text='Chọn Phòng: ', font=('Bold', 12), bg="#e7d7c1")
    customer_name_lb.place(x=20, y=25, width=160, height=30)
    # Tạo Combobox
    active_rooms = get_active_rooms()
    room_combobox = ttk.Combobox(head_frame, values=active_rooms, font=('verdana', 13))
    room_combobox.place(x=200, y=25, width=200, height=30)
    room_combobox.bind("<<ComboboxSelected>>",
                       lambda event: on_combobox_checkout_select
                       (event, room_combobox, room_checkout_result_label, money_service_label, incentives_label,
                        incentives_percent_label, total_label, final_label))

    room_checkout_lb = tk.Label(head_frame, text='Tiền Phòng: ', font=('Bold', 12), bg="#e7d7c1")
    room_checkout_lb.place(x=20, y=75, width=160, height=30)
    room_checkout_result_label = tk.Label(head_frame, font=('Bold', 12), bg="#e7d7c1")
    room_checkout_result_label.place(x=200, y=75, width=200, height=30)

    money_service_lb = tk.Label(head_frame, text='Tiền Dịch Vụ: ', font=('Bold', 12), bg="#e7d7c1")
    money_service_lb.place(x=20, y=125, width=160, height=30)
    money_service_label = tk.Label(head_frame, font=('Bold', 12), bg="#e7d7c1")
    money_service_label.place(x=200, y=125, width=200, height=30)

    incentives_percent_lb = tk.Label(head_frame, text='Ưu Đãi Khách Hàng: ', font=('Bold', 12), bg="#e7d7c1")
    incentives_percent_lb.place(x=20, y=175, width=160, height=30)
    incentives_percent_label = tk.Label(head_frame, font=('Bold', 12), bg="#e7d7c1")
    incentives_percent_label.place(x=200, y=175, width=200, height=30)

    total_lb = tk.Label(head_frame, text='Tổng Thanh Toán: ', font=('Bold', 12), bg="#e7d7c1")
    total_lb.place(x=500, y=25, width=160, height=30)
    total_label = tk.Label(head_frame, font=('Bold', 12), bg="#e7d7c1")
    total_label.place(x=680, y=25, width=250, height=30)

    incentives_lb = tk.Label(head_frame, text='Khấu Trừ Ưu Đãi: ', font=('Bold', 12), bg="#e7d7c1")
    incentives_lb.place(x=500, y=75, width=160, height=30)
    incentives_label = tk.Label(head_frame, font=('Bold', 12), bg="#e7d7c1")
    incentives_label.place(x=680, y=75, width=250, height=30)

    final_lb = tk.Label(head_frame, text='Thành Tiền: ', font=('Bold', 12), bg="#e7d7c1")
    final_lb.place(x=500, y=125, width=160, height=30)
    final_label = tk.Label(head_frame, font=('Bold', 12), bg="#e7d7c1")
    final_label.place(x=680, y=125, width=250, height=30)

    # Nút lưu thông tin 
    save_btn = tk.Button(head_frame, text='Thanh Toán', font=('Bold', 12), bg='#3a7ca5', fg='white',
                         command=lambda: checkout(room_combobox, cus_table))
    save_btn.place(x=500, y=175, width=100, height=40)
    # Nút cập nhật thông tin 
    update_btn = tk.Button(head_frame, text='In Hóa Đơn', font=('Bold', 12), bg='#3a7ca5', fg='white',
                           command=lambda: printInvoice(room_combobox))
    update_btn.place(x=610, y=175, width=100, height=40)
    # Nút lÀM Sạch
    delete_btn = tk.Button(head_frame, text='Làm sạch', font=('Bold', 12), bg='#3a7ca5', fg='white',
                           command=lambda: clear_checkout_room(
                               room_combobox,
                               room_checkout_result_label,
                               money_service_label,
                               total_label,
                               incentives_percent_label,
                               incentives_label,
                               final_label
                           ))
    delete_btn.place(x=720, y=175, width=110, height=40)

    head_frame.pack(pady=0)
    head_frame.pack_propagate(False)
    head_frame.configure(width=1038, height=265)

    # Frame mới cho nút tìm kiếm
    search_bar_frame = tk.Frame(room_frame, bg='#3a7ca5')
    search_lb = tk.Label(search_bar_frame, text="Danh Sách Phòng Đang Được Sử Dụng", font=('Bold', 12))
    search_lb.place(x=20, y=10, height=30)

    search_bar_frame.pack(pady=0)
    search_bar_frame.pack_propagate(False)
    search_bar_frame.configure(width=1038, height=50)

    # Frame mới cho bảng thông tin phòng đang sử dụng
    table_cus_frame = tk.Frame(room_frame, bg='white')

    cus_table = ttk.Treeview(table_cus_frame)
    cus_table.place(x=0, y=0, width=1000, height=280)

    cus_table['column'] = ['Room', 'Customer', 'Description', 'Duration', 'Status']
    cus_table.column('#0', anchor=tk.W, width=0, stretch=tk.NO)

    cus_table.column('Room', anchor=tk.W, width=120)
    cus_table.column('Customer', anchor=tk.W, width=120)
    cus_table.column('Description', anchor=tk.W, width=120)
    cus_table.column('Duration', anchor=tk.W, width=80)
    cus_table.column('Status', anchor=tk.W, width=80)

    heading_font = ("Arial", 11, "bold")
    style = ttk.Style()
    style.configure("Treeview.Heading", font=heading_font)
    cus_table.heading('Room', text='Tên Phòng', anchor=tk.W)
    cus_table.heading('Customer', text='Tên Khách Hàng', anchor=tk.W)
    cus_table.heading('Description', text='Giờ Bắt Đầu', anchor=tk.W)
    cus_table.heading('Duration', text='Thời Lượng Sử Dụng', anchor=tk.W)
    cus_table.heading('Status', text='Loại Phòng', anchor=tk.W)

    # đọc ra dữ liệu từ hàm refreshTable()
    loadDataRoomUsing(cus_table)

    table_cus_frame.pack(pady=5)
    table_cus_frame.pack_propagate(False)
    table_cus_frame.configure(width=1038, height=320, padx=20)
    # kết thúc

    room_frame.pack(pady=0)


def employee_page():
    manager_frame = tk.Frame(main_frame)

    head_frame = tk.Frame(manager_frame, bg='#ffffff')

    heading_lb = tk.Label(manager_frame, text="Quản Lý Nhân Sự", font=('Bold', 22), bg='#3a7ca5', fg='white')
    heading_lb.pack(fill=tk.X, pady=0)

    # Label và textfields
    personnel_name_lb = tk.Label(head_frame, text='Tên: ', font=('Bold', 12), bg="#e7d7c1")
    personnel_name_lb.place(x=20, y=25, width=160, height=30)
    personnel_name_text_field = tk.Entry(head_frame, font=('Bold', 12), bg="#e7d7c1")
    personnel_name_text_field.place(x=200, y=25, width=350, height=30)

    personnel_phone_lb = tk.Label(head_frame, text='Số điện thoại: ', font=('Bold', 12), bg="#e7d7c1")
    personnel_phone_lb.place(x=20, y=75, width=160, height=30)
    personnel_phone_text_field = tk.Entry(head_frame, font=('Bold', 12), bg="#e7d7c1")
    personnel_phone_text_field.place(x=200, y=75, width=350, height=30)

    personnel_address_lb = tk.Label(head_frame, text='Địa chỉ: ', font=('Bold', 12), bg="#e7d7c1")
    personnel_address_lb.place(x=20, y=125, width=160, height=30)
    personnel_address_text_field = tk.Entry(head_frame, font=('Bold', 12), bg="#e7d7c1")
    personnel_address_text_field.place(x=200, y=125, width=350, height=30)

    position_lb = tk.Label(head_frame, text='Chức vụ: ', font=('Bold', 12), bg="#e7d7c1")
    position_lb.place(x=20, y=175, width=160, height=30)
    selected_position = tk.StringVar()
    combo_position = ttk.Combobox(head_frame, font=('Bold', 12), state="readonly", values=["Quản lý", "Nhân viên"],
                                  textvariable=selected_position)
    combo_position.place(x=200, y=175, width=350, height=30)

    salary_lb = tk.Label(head_frame, text='Lương: ', font=('Bold', 12), bg="#e7d7c1")
    salary_lb.place(x=570, y=25, width=160, height=30)
    salary_text_field = tk.Entry(head_frame, font=('Bold', 12), bg="#e7d7c1")
    salary_text_field.place(x=750, y=25, width=350, height=30)

    work_time_lb = tk.Label(head_frame, text='Giờ làm: ', font=('Bold', 12), bg="#e7d7c1")
    work_time_lb.place(x=570, y=75, width=160, height=30)
    work_time_text_field = tk.Entry(head_frame, font=('Bold', 12), bg="#e7d7c1")
    work_time_text_field.place(x=750, y=75, width=350, height=30)

    bonus_lb = tk.Label(head_frame, text='Ca Làm Việc: ', font=('Bold', 12), bg="#e7d7c1")
    bonus_lb.place(x=570, y=125, width=160, height=30)
    bonus_text_field = tk.Entry(head_frame, font=('Bold', 12), bg="#e7d7c1")
    bonus_text_field.place(x=750, y=125, width=350, height=30)

    # Nút lưu thông tin
    save_btn = tk.Button(head_frame, text='Lưu', font=('Bold', 12), bg='#3a7ca5', fg='white',
                         command=lambda: addPersonnel(cus_table, personnel_name_text_field.get(),
                                                      personnel_phone_text_field.get(),
                                                      personnel_address_text_field.get(), selected_position.get(),
                                                      salary_text_field.get(), work_time_text_field.get(),
                                                      bonus_text_field.get()))
    save_btn.place(x=570, y=170, width=80, height=40)
    # Nút cập nhật thông tin
    update_btn = tk.Button(head_frame, text='Cập nhật', font=('Bold', 12), bg='#3a7ca5', fg='white',
                           command=lambda: updateDataInFile(cus_table, current_id, personnel_name_text_field.get(),
                                                            personnel_phone_text_field.get(),
                                                            personnel_address_text_field.get(), selected_position.get(),
                                                            salary_text_field.get(), work_time_text_field.get(),
                                                            bonus_text_field.get()))
    update_btn.place(x=660, y=170, width=80, height=40)
    # Nút xóa thông tin
    delete_btn = tk.Button(head_frame, text='Xóa', font=('Bold', 12), bg='#3a7ca5', fg='white',
                           command=lambda: deleteDataInFile(cus_table, current_id))
    delete_btn.place(x=750, y=170, width=80, height=40)
    # Nút clear thông tin
    clear_btn = tk.Button(head_frame, text='Làm sạch', font=('Bold', 12), bg='#3a7ca5', fg='white',
                          command=lambda: refreshInput())
    clear_btn.place(x=840, y=170, width=80, height=40)
    # Nút sắp xếp thông tin theo tên
    clear_btn = tk.Button(head_frame, text='Sắp xếp', font=('Bold', 12), bg='#3a7ca5', fg='white',
                          command=lambda: readFileAndDisplay(cus_table, True))
    clear_btn.place(x=930, y=170, width=80, height=40)

    head_frame.pack(pady=0)
    head_frame.pack_propagate(False)
    head_frame.configure(width=1038, height=225)

    # Frame mới cho bảng nhân sự

    table_cus_frame = tk.Frame(manager_frame, bg='white')

    cus_table = ttk.Treeview(table_cus_frame)
    cus_table.place(x=0, y=0, width=1000, height=320)

    cus_table['column'] = ['ID', 'Name', 'Phone', 'Address', 'Position', 'Salary', 'Work Time', 'Ca']
    cus_table.column('#0', anchor=tk.W, width=0, stretch=tk.NO)
    cus_table.column('ID', anchor=tk.W, width=0)
    cus_table.column('Name', anchor=tk.W, width=160)
    cus_table.column('Phone', anchor=tk.W, width=80)
    cus_table.column('Address', anchor=tk.W, width=200)
    cus_table.column('Position', anchor=tk.W, width=60)
    cus_table.column('Salary', anchor=tk.W, width=60)
    cus_table.column('Work Time', anchor=tk.W, width=60)
    cus_table.column('Ca', anchor=tk.W, width=60)

    heading_font = ("Arial", 11, "bold")
    style = ttk.Style()
    style.configure("Treeview.Heading", font=heading_font)
    cus_table.heading('ID', text='ID', anchor=tk.W)
    cus_table.heading('Name', text='Tên', anchor=tk.W)
    cus_table.heading('Phone', text='Số Điện Thoại', anchor=tk.W)
    cus_table.heading('Address', text='Địa Chỉ', anchor=tk.W)
    cus_table.heading('Position', text='Chức vụ', anchor=tk.W)
    cus_table.heading('Salary', text='Lương', anchor=tk.W)
    cus_table.heading('Work Time', text='Giờ Làm', anchor=tk.W)
    cus_table.heading('Ca', text='Ca làm việc', anchor=tk.W)
    # đọc ra dữ liệu từ hàm readFileAndDisplay()
    readFileAndDisplay(cus_table, False)
    cus_table.bind('<ButtonRelease-1>', lambda event: handle_click())
    table_cus_frame.pack(pady=5)
    table_cus_frame.pack_propagate(False)
    table_cus_frame.configure(width=1038, height=320, padx=20)

    # kết thúc

    def handle_click():
        global current_id
        item = cus_table.selection()[0]
        data = cus_table.item(item, 'values')
        current_id = data[0]
        if data[4] == 'Quản lý':
            combo_position.current(0)
        else:
            combo_position.current(1)
        personnel_name_text_field.delete(0, tk.END)
        personnel_name_text_field.insert(0, data[1])
        personnel_address_text_field.delete(0, tk.END)
        personnel_address_text_field.insert(0, data[3])
        personnel_phone_text_field.delete(0, tk.END)
        personnel_phone_text_field.insert(0, data[2])
        salary_text_field.delete(0, tk.END)
        salary_text_field.insert(0, int(data[5]) - int(data[7]))
        work_time_text_field.delete(0, tk.END)
        work_time_text_field.insert(0, data[6])
        bonus_text_field.delete(0, tk.END)
        bonus_text_field.insert(0, data[7])

    def refreshInput():
        personnel_name_text_field.delete(0, tk.END)
        personnel_address_text_field.delete(0, tk.END)
        personnel_phone_text_field.delete(0, tk.END)
        salary_text_field.delete(0, tk.END)
        work_time_text_field.delete(0, tk.END)
        bonus_text_field.delete(0, tk.END)

    manager_frame.pack(pady=0)


def draw_pie_chart(data, title, x, y):
    size = (2.45, 1.55)
    fig = Figure(figsize=size)
    ax = fig.add_axes([0, 0, 1, 1], aspect=1)
    wedges, texts, autotexts = ax.pie(data.values(), labels=data.keys(), autopct='%1.1f%%', startangle=90)

    colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    for i, wedge in enumerate(wedges):
        wedge.set_color(colors[i % len(colors)])

    for text, autotext in zip(texts, autotexts):
        text.set_color('black')
        autotext.set_color('white')

    canvas = FigureCanvasTkAgg(fig, master=main_frame)
    canvas.draw()
    canvas.get_tk_widget().place(x=x, y=y)
    ax.set_title(title)

    return fig


def draw_double_bar_chart(data, title, x, y, width=5.2, height=2.7):
    fig, ax = plt.subplots(figsize=(width, height))
    canvas = FigureCanvasTkAgg(fig, master=main_frame)
    canvas.draw()
    canvas.get_tk_widget().place(x=x, y=y)

    # Return the fig object

    categories = list(data.keys())
    values1 = [data[category]['Phòng'] for category in categories]
    values2 = [data[category]['Dịch vụ'] for category in categories]

    # Convert x-axis categories to numerical indices
    indices = np.arange(len(categories))

    bar_width = 0.4
    bar1 = ax.bar(indices, values1, bar_width, label='Phòng', color='blue')
    bar2 = ax.bar(indices + bar_width, values2, bar_width, label='Dịch vụ', color='orange')

    ax.set_title(title)
    ax.set_xlabel('Ngày')
    ax.set_ylabel('Doanh Thu')

    ax.set_xticks(indices + bar_width / 2)
    ax.set_xticklabels(categories)

    ax.legend()

    # Add labels on top of the bars
    # for bar in [bar1, bar2]:
    #     for rect in bar:
    #         height = rect.get_height()
    #         ax.annotate('{}'.format(height),
    #                     xy=(rect.get_x() + rect.get_width() / 2, height),
    #                     xytext=(0, 3),  # 3 points vertical offset
    #                     textcoords="offset points",
    #                     ha='center', va='bottom')

    canvas = FigureCanvasTkAgg(fig, master=main_frame)
    canvas.draw()
    canvas.get_tk_widget().place(x=x, y=y)

    # Return the fig object
    return fig


def draw_line_chart(data, title, x, y, width=5.2, height=2.7):
    fig, ax = plt.subplots(figsize=(width, height))
    days = list(data.keys())
    revenue = list(data.values())
    ax.plot(days, revenue, marker='o', color='blue', linestyle='-')

    ax.set_title(title)
    ax.set_xlabel('Days of the Week')
    ax.set_ylabel('Doanh Thu')

    canvas = FigureCanvasTkAgg(fig, master=main_frame)
    canvas.draw()
    canvas.get_tk_widget().place(x=x, y=y)

    # Return the fig object
    return fig


def draw_stacked_bar_chart(data, title, x, y, width=5, height=2.7):
    fig, ax = plt.subplots(figsize=(width, height))

    categories = list(data.keys())
    values1 = [data[category]['Khách Vip'] for category in categories]
    values2 = [data[category]['Membership'] for category in categories]
    values3 = [data[category]['Vãng Lai'] for category in categories]

    ax.bar(categories, values1, label='Khách Vip', color='blue')
    ax.bar(categories, values2, label='Membership', color='orange', bottom=values1)
    ax.bar(categories, values3, label='Vãng Lai', color='green', bottom=[i + j for i, j in zip(values1, values2)])

    ax.set_title(title)
    ax.set_xlabel('Ngày')
    ax.set_ylabel('Doanh Thu')

    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=main_frame)
    canvas.draw()
    canvas.get_tk_widget().place(x=x, y=y)

    # Return the fig object
    return fig


def totalRevenue():
    df = pd.read_csv('data.csv')
    totalRevenue = df['Tổng doanh thu'].sum()
    return totalRevenue


def totalRooms():
    df = pd.read_csv('data.csv')
    totalRooms = df['Tổng tiền Phòng'].sum()
    return totalRooms


def totalServices():
    df = pd.read_csv('data.csv')
    totalServices = df['Tổng dịch vụ'].sum()
    return totalServices

def totalRoomVip():
    df = pd.read_csv('data.csv')
    totalRoomVip = df['Doanh thu Theo Phòng Vip'].sum()
    return totalRoomVip

def totalRoomNormal():
    df = pd.read_csv('data.csv')
    totalRoomNormal = df['Doanh thu Theo Phòng Thường'].sum()
    return totalRoomNormal

def totalCusVip():
    df = pd.read_csv('data.csv')
    totalRoomNormal = df['Doanh Thu Theo Khách Vip'].sum()
    return totalRoomNormal

def totalCusMember():
    df = pd.read_csv('data.csv')
    totalRoomNormal = df['Doanh Thu theo Membership'].sum()
    return totalRoomNormal

def totalCusNormal():
    df = pd.read_csv('data.csv')
    totalRoomNormal = df['Doanh thu theo khách Vãng lai'].sum()
    return totalRoomNormal

def static_page():
    df = pd.read_csv('data.csv')
    static_frame = tk.Frame(main_frame)
    head_frame = tk.Frame(static_frame, bg='#F4F5F4')
    head_frame.pack(pady=0)
    head_frame.pack_propagate(False)
    head_frame.configure(width=1038, height=680)

    heading_lb = tk.Label(head_frame, text="Thống Kê Doanh Thu Trong Tuần", font=('Bold', 22), bg='#3a7ca5', fg='white')
    heading_lb.pack(fill=tk.X, pady=0)

    width_lb = 155
    height_lb = 110
    x_location = 10
    y_location = 50
    bold_font = font.Font(family="Helvetica", size=11, weight="bold")
    bold_font_2 = font.Font(family="Helvetica", size=13, weight="bold")

    totalRevenu = format_currency(totalRevenue())
    totalService = format_currency(totalServices())
    totalRoom = format_currency(totalRooms())

    id_name_lb = tk.Label(head_frame, text='Tổng Doanh Thu\n ', font=bold_font, bg="white")
    id_name_lb.place(x=x_location, y=y_location, width=width_lb, height=height_lb)
    id_name_lb = tk.Label(head_frame, text=totalRevenu, font=bold_font_2, bg="#e7d7c1", fg="#38669C")
    id_name_lb.place(x=20, y=110, width=140, height=28)

    id_name_lb = tk.Label(head_frame, text='Doanh Thu Phòng\n ', font=bold_font, bg="white")
    id_name_lb.place(x=x_location + 165, y=y_location, width=width_lb, height=height_lb)
    id_name_lb = tk.Label(head_frame, text=totalRoom, font=bold_font_2, bg="#e7d7c1", fg="#38669C")
    id_name_lb.place(x=45 + 140, y=110, width=140, height=28)

    id_name_lb = tk.Label(head_frame, text='Tổng Dịch Vụ\n ', font=bold_font, bg="white")
    id_name_lb.place(x=x_location + 328, y=y_location, width=width_lb, height=height_lb)
    id_name_lb = tk.Label(head_frame, text=totalService, font=bold_font_2, bg="#e7d7c1", fg="#38669C")
    id_name_lb.place(x=50 + 300, y=110, width=140, height=28)

    # Biêu đồ tròn
    servicePercent = totalServices() * 100 / totalRevenue()
    roomPercent = totalRooms() * 100 / totalRevenue()
    data1 = {'Phòng': roomPercent, 'Dịch Vụ': servicePercent}
    fig1 = draw_pie_chart(data1, 'Tổng Doanh Thu', x_location, y_location + 120)

    # roomVipPercent = totalRoomVip() * 100 / totalRevenue()
    # roomNormalPercent = totalRoomNormal() * 100 / totalRevenue()
    # data2 = {'Phòng VIP': roomVipPercent, 'Phòng Thường': roomNormalPercent}
    # fig2 = draw_pie_chart(data2, 'Doanh Thu Phòng', x_location + 165, y_location + 120)

    cusVipPercent = totalCusVip() * 100 / totalRevenue()
    cusMemberPercent = totalCusMember() * 100 / totalRevenue()
    cusNormalPercent = totalCusNormal() * 100 / totalRevenue()
    data3 = {'VIP': cusVipPercent, 'Membership': cusMemberPercent, 'Vãng Lai': cusNormalPercent}
    fig3 = draw_pie_chart(data3, 'Tổng Dịch Vụ', x_location + 250, y_location + 120)

    # Biều đồ đường
    revenueSet = list(OrderedDict.fromkeys(df['Tổng doanh thu']))
    sorted_days = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ Nhật']
    daily_revenue_column = dict(zip(sorted_days, revenueSet))
    draw_line_chart(daily_revenue_column, 'Doanh Thu Hàng Ngày Trong Tuần', x_location, y_location + 300)

    # Dữ liệu cho biểu đồ cột đôi
    roomSet = list(OrderedDict.fromkeys(df['Tổng tiền Phòng']))
    serviceSet = list(OrderedDict.fromkeys(df['Tổng dịch vụ']))
    daily_revenue = {
        'Thứ 2': {'Phòng': roomSet[0], 'Dịch vụ': serviceSet[0]},
        'Thứ 3': {'Phòng': roomSet[1], 'Dịch vụ': serviceSet[1]},
        'Thứ 4': {'Phòng': roomSet[2], 'Dịch vụ': serviceSet[2]},
        'Thứ 5': {'Phòng': roomSet[3], 'Dịch vụ': serviceSet[3]},
        'Thứ 6': {'Phòng': roomSet[4], 'Dịch vụ': serviceSet[4]},
        'Thứ 7': {'Phòng': roomSet[5], 'Dịch vụ': serviceSet[5]},
        'Chủ Nhật': {'Phòng': roomSet[6], 'Dịch vụ': serviceSet[6]}
    }
    draw_double_bar_chart(daily_revenue, 'Doanh Thu Phòng và Dịch Vụ', x_location + 490, y_location)

    # Dữ liệu cho biểu đồ cột dung lượng
    cusVip = list(OrderedDict.fromkeys(df['Doanh Thu Theo Khách Vip']))
    cusMember = list(OrderedDict.fromkeys(df['Doanh Thu theo Membership']))
    cusNormal = list(OrderedDict.fromkeys(df['Doanh thu theo khách Vãng lai']))

    daily_revenue = {
        'Thứ 2': {'Khách Vip': cusVip[0], 'Membership': cusMember[0], 'Vãng Lai': cusNormal[0]},
        'Thứ 3': {'Khách Vip': cusVip[1], 'Membership': cusMember[1], 'Vãng Lai': cusNormal[1]},
        'Thứ 4': {'Khách Vip': cusVip[2], 'Membership': cusMember[2], 'Vãng Lai': cusNormal[2]},
        'Thứ 5': {'Khách Vip': cusVip[3], 'Membership': cusMember[3], 'Vãng Lai': cusNormal[3]},
        'Thứ 6': {'Khách Vip': cusVip[4], 'Membership': cusMember[4], 'Vãng Lai': cusNormal[4]},
        'Thứ 7': {'Khách Vip': cusVip[5], 'Membership': cusMember[5], 'Vãng Lai': cusNormal[5]},
        'Chủ Nhật': {'Khách Vip': cusVip[6], 'Membership': cusMember[6], 'Vãng Lai': cusNormal[6]}
    }

    draw_stacked_bar_chart(daily_revenue, 'Doanh Thu Theo Loại Phòng', x_location + 500, y_location + 300)
    static_frame.pack(pady=0)


# Hàm Trang Khách Hàng
def handle_click(cus_table, customer_name_entry, customer_phone_entry, customer_address_entry, id_lb):
    global current_id
    item = cus_table.selection()[0]
    data = cus_table.item(item, 'values')
    current_id = data[0]
    customer_name_entry.delete(0, tk.END)
    customer_name_entry.insert(0, data[0])
    customer_phone_entry.delete(0, tk.END)
    customer_phone_entry.insert(0, data[2])
    customer_address_entry.delete(0, tk.END)
    customer_address_entry.insert(0, data[3])
    id_lb.config(text=data[1])


def customer_page():
    customer_frame = tk.Frame(main_frame)

    head_frame = tk.Frame(customer_frame, bg='#ffffff')

    heading_lb = tk.Label(customer_frame, text="Khách Hàng Thân Thiết", font=('Bold', 22), bg='#3a7ca5', fg='white')
    heading_lb.pack(fill=tk.X, pady=0)

    # Label và textfields
    id_name_lb = tk.Label(head_frame, text='Name ID: ', font=('Bold', 12), bg="#e7d7c1")
    id_name_lb.place(x=570, y=125, width=80, height=30)
    id_lb = tk.Label(head_frame, font=('Bold', 12), bg="#e7d7c1")
    id_lb.place(x=660, y=125, width=170, height=30)

    customer_name_lb = tk.Label(head_frame, text='Tên Khách Hàng: ', font=('Bold', 12), bg="#e7d7c1")
    customer_name_lb.place(x=20, y=25, width=160, height=30)
    customer_name_text_field = tk.Entry(head_frame, font=('Bold', 12), bg="#e7d7c1", highlightthickness=1,
                                        highlightcolor="#e7d7c1")
    customer_name_text_field.place(x=200, y=25, width=350, height=30)

    customer_phone_lb = tk.Label(head_frame, text='Số điện thoại: ', font=('Bold', 12), bg="#e7d7c1")
    customer_phone_lb.place(x=20, y=75, width=160, height=30)
    customer_phone_text_field = tk.Entry(head_frame, font=('Bold', 12), bg="#e7d7c1", highlightthickness=1,
                                         highlightcolor="#e7d7c1")
    customer_phone_text_field.place(x=200, y=75, width=350, height=30)

    customer_address_lb = tk.Label(head_frame, text='Địa chỉ: ', font=('Bold', 12), bg="#e7d7c1")
    customer_address_lb.place(x=20, y=125, width=160, height=30)
    customer_address_text_field = tk.Entry(head_frame, font=('Bold', 12), bg="#e7d7c1", highlightthickness=1,
                                           highlightcolor="#e7d7c1")
    customer_address_text_field.place(x=200, y=125, width=350, height=30)

    amount_consumed_lb = tk.Label(head_frame, text='Thanh Toán Lần Đầu: ', font=('Bold', 12), bg="#e7d7c1")
    amount_consumed_lb.place(x=20, y=175, width=160, height=30)
    amount_consumed_text_field = tk.Entry(head_frame, font=('Bold', 12), bg="#e7d7c1", highlightthickness=1,
                                          highlightcolor="#e7d7c1")
    amount_consumed_text_field.place(x=200, y=175, width=350, height=30)

    # Nút lưu thông tin 
    save_btn = tk.Button(head_frame, text='Lưu', font=('Bold', 12), bg='#3a7ca5', fg='white',
                         command=lambda: add_customer_event(cus_table_main, customer_name_text_field,
                                                            customer_phone_text_field,
                                                            customer_address_text_field, amount_consumed_text_field,
                                                            id_lb))
    save_btn.place(x=570, y=170, width=80, height=40)

    save_btn = tk.Button(head_frame, text='Cập Nhật', font=('Bold', 12), bg='#3a7ca5', fg='white',
                         command=lambda: update_customer_event(cus_table_main,
                                                               customer_name_text_field,
                                                               customer_phone_text_field,
                                                               customer_address_text_field,
                                                               id_lb))
    save_btn.place(x=660, y=170, width=80, height=40)

    delete_btn = tk.Button(head_frame, text='Xóa', font=('Bold', 12), bg='#3a7ca5', fg='white',
                           command=lambda: removeCustomerByPhoneEvent(cus_table_main,
                                                                      customer_name_text_field,
                                                                      customer_phone_text_field,
                                                                      customer_address_text_field,
                                                                      amount_consumed_text_field,
                                                                      id_lb
                                                                      ))
    delete_btn.place(x=750, y=170, width=80, height=40)
    # Nút clear thông tin
    clear_btn = tk.Button(head_frame, text='Làm sạch', font=('Bold', 12), bg='#3a7ca5', fg='white',
                          command=lambda: clear_textfields(
                              customer_name_text_field,
                              customer_phone_text_field,
                              customer_address_text_field,
                              amount_consumed_text_field,
                              id_lb
                          ))
    clear_btn.place(x=840, y=170, width=80, height=40)

    # Nút xuat file
    export_csv = tk.Button(head_frame, text='In Thẻ', font=('Bold', 12), bg='#3a7ca5', fg='white',
                           command=lambda: exportFileEvent(customer_phone_text_field))
    export_csv.place(x=930, y=170, width=80, height=40)

    head_frame.pack(pady=0)
    head_frame.pack_propagate(False)
    head_frame.configure(width=1038, height=225)

    # Frame mới cho nút tìm kiếm
    search_bar_frame = tk.Frame(customer_frame, bg='#3a7ca5')
    search_lb = tk.Label(search_bar_frame, text="Tìm kiếm khách hàng bằng SĐT", font=('Bold', 12))
    search_lb.place(x=20, y=10, height=30)

    global search_entry
    search_entry = tk.Entry(search_bar_frame, font=('Bold', 12), bg="white", highlightthickness=1,
                            highlightcolor="white")
    search_entry.place(x=260, y=10, height=30, width=290)
    search_entry.bind("<KeyRelease>", search_customer_by_phone)

    search_bar_frame.pack(pady=0)
    search_bar_frame.pack_propagate(False)
    search_bar_frame.configure(width=1038, height=50)

    # Frame mới cho bảng thông tin khách hàng

    table_cus_frame = tk.Frame(customer_frame, bg='white')
    global cus_table_main
    cus_table_main = ttk.Treeview(table_cus_frame)
    cus_table_main.place(x=0, y=0, width=1000, height=320)

    cus_table_main['column'] = ['Name', 'NameId', 'Phone', 'Address', 'Type', 'Incentives']
    cus_table_main.column('#0', anchor=tk.W, width=0, stretch=tk.NO)

    cus_table_main.column('Name', anchor=tk.W, width=80)
    cus_table_main.column('NameId', anchor=tk.W, width=80)
    cus_table_main.column('Phone', anchor=tk.W, width=80)
    cus_table_main.column('Address', anchor=tk.W, width=250)
    cus_table_main.column('Type', anchor=tk.W, width=70)
    cus_table_main.column('Incentives', anchor=tk.W, width=60)

    heading_font = ("Arial", 11, "bold")
    style = ttk.Style()
    style.configure("Treeview.Heading", font=heading_font)
    cus_table_main.heading('Name', text='Tên Khách Hàng', anchor=tk.W)
    cus_table_main.heading('NameId', text='Tên Định Danh', anchor=tk.W)
    cus_table_main.heading('Phone', text='Số Điện Thoại', anchor=tk.W)
    cus_table_main.heading('Address', text='Địa Chỉ', anchor=tk.W)
    cus_table_main.heading('Type', text='Loại khách Hàng', anchor=tk.W)
    cus_table_main.heading('Incentives', text='Mức Ưu đãi (%)', anchor=tk.W)

    # đọc ra dữ liệu từ hàm refreshTable()
    refreshTable(cus_table_main)
    cus_table_main.bind('<ButtonRelease-1>', lambda event: handle_click(cus_table_main, customer_name_text_field,
                                                                        customer_phone_text_field,
                                                                        customer_address_text_field,
                                                                        id_lb))

    table_cus_frame.pack(pady=5)
    table_cus_frame.pack_propagate(False)
    table_cus_frame.configure(width=1038, height=320, padx=20)
    # kết thúc

    customer_frame.pack(pady=0)


def search_customer_by_phone(event):
    conn = connection()
    cursor = conn.cursor()

    # Xóa dữ liệu cũ trong bảng
    for row in cus_table_main.get_children():
        cus_table_main.delete(row)

    # Lấy số điện thoại từ Entry
    phone_number = search_entry.get()

    # Truy vấn cơ sở dữ liệu
    query = "SELECT name,name_id, phone, address, type, customer_incentives FROM customer WHERE phone LIKE %s order by customer_incentives desc "
    cursor.execute(query, ('%' + phone_number + '%',))
    result = cursor.fetchall()

    # Hiển thị kết quả truy vấn trong bảng
    for row in result:
        cus_table_main.insert(parent='', index='end', iid=row, text="", values=(row), tag="orow")

    cus_table_main.tag_configure('orow', background='#EEEEEE', font=('Arial', 12))


# Hàm Trang Dịch Vụ
def update_info(event, room_combobox, ser_table):
    selected_room = room_combobox.get()
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="170801",
        database="karaoke"
    )

    cursor = conn.cursor()
    # Truy vấn thông tin từ các bảng tương ứng
    query = """
        SELECT room.name, service.name, service.unit, service_detail.quantity
        FROM room
        JOIN booking_room ON room.id = booking_room.id_room
        JOIN service_detail ON booking_room.id = service_detail.booking_room_id
        JOIN service ON service_detail.id_service = service.id
        WHERE room.name = %s and booking_room.ended_time is null
    """
    cursor.execute(query, (selected_room,))
    data = cursor.fetchall()

    # Xóa dữ liệu cũ trên Treeview
    ser_table.delete(*ser_table.get_children())

    # Hiển thị dữ liệu mới
    for row in data:
        ser_table.insert("", "end", values=row)


def returnProductEvent(room_combobox, combobox_service, customer_quantity_text_field, ser_table):
    returnProduct(room_combobox, combobox_service, customer_quantity_text_field, ser_table)
    clearNameServiceAndQuantity(combobox_service, customer_quantity_text_field)
    update_table(ser_table, room_combobox)


def removeProductEvent(room_combobox, combobox_service, ser_table):
    removeProduct(room_combobox, combobox_service)
    update_table(ser_table, room_combobox)


def removeCustomerByPhoneEvent(cus_table,
                               customer_name_text_field,
                               customer_phone_text_field,
                               customer_address_text_field,
                               amount_consumed_text_field,
                               id_lb):
    removeCustomerByPhone(customer_phone_text_field)
    refreshTable(cus_table)
    clear_textfields(customer_name_text_field, customer_phone_text_field, customer_address_text_field,
                     amount_consumed_text_field, id_lb)


def handle_click_table_service(ser_table, combobox_service, customer_quantity_text_field):
    global current_id
    item = ser_table.selection()[0]
    data = ser_table.item(item, 'values')
    current_id = data[0]
    combobox_service.delete(0, tk.END)
    combobox_service.insert(0, data[1])
    customer_quantity_text_field.delete(0, tk.END)
    customer_quantity_text_field.insert(0, data[3])


def service_page():
    service_frame = tk.Frame(main_frame)

    head_frame = tk.Frame(service_frame, bg='#ffffff')

    heading_lb = tk.Label(service_frame, text=" Dịch Vụ Phòng KARAOKE", font=('Bold', 22), bg='#3a7ca5', fg='white')
    heading_lb.pack(fill=tk.X, pady=0)

    # Label tên phòng đang sử dụng
    customer_name_lb = tk.Label(head_frame, text='Tên Phòng: ', font=('Bold', 12), bg="#e7d7c1")
    customer_name_lb.place(x=20, y=25, width=160, height=30)
    # Select box
    connection = mysql.connector.connect(host='localhost', user='root',
                                         password='170801', database='karaoke')
    c = connection.cursor()

    # Tạo Combobox
    active_rooms = get_active_rooms()
    room_combobox = ttk.Combobox(head_frame, values=active_rooms, font=('verdana', 13))
    room_combobox.place(x=200, y=25, width=350, height=30)

    # gọi hàm sử lý khi click
    room_combobox.bind("<<ComboboxSelected>>",
                       lambda event: update_info(event, room_combobox, ser_table))

    # Label tên sản phẩm
    customer_phone_lb = tk.Label(head_frame, text='Tên Sản Phẩm: ', font=('Bold', 12), bg="#e7d7c1")
    customer_phone_lb.place(x=20, y=75, width=160, height=30)
    # Select box
    c.execute("SELECT name FROM `service` order by unit_price desc")
    options = [row[0] for row in c.fetchall()]
    selected_cus = StringVar(head_frame)
    combobox_service = ttk.Combobox(head_frame, textvariable=selected_cus, values=options,
                                    font=('verdana', 13))
    combobox_service.place(x=200, y=75, width=350, height=30)

    customer_quantity_lb = tk.Label(head_frame, text='Số Lượng: ', font=('Bold', 12), bg="#e7d7c1")
    customer_quantity_lb.place(x=20, y=125, width=160, height=30)
    customer_quantity_text_field = tk.Entry(head_frame, font=('Bold', 12), bg="#e7d7c1", highlightthickness=1,
                                            highlightcolor="#e7d7c1")
    customer_quantity_text_field.place(x=200, y=125, width=350, height=30)

    # Nút lưu thông tin
    save_btn = tk.Button(head_frame, text='Thêm', font=('Bold', 12), bg='#3a7ca5', fg='white',
                         command=lambda: saveService(ser_table, room_combobox, combobox_service,
                                                     customer_quantity_text_field))
    save_btn.place(x=20, y=170, width=80, height=40)
    # Nút cập nhật thông tin
    update_btn = tk.Button(head_frame, text='Trả Hàng', font=('Bold', 12), bg='#3a7ca5', fg='white',
                           command=lambda: returnProductEvent(room_combobox,
                                                              combobox_service,
                                                              customer_quantity_text_field,
                                                              ser_table))
    update_btn.place(x=110, y=170, width=80, height=40)
    # Nút xóa thông tin 
    delete_btn = tk.Button(head_frame, text='Xóa', font=('Bold', 12), bg='#3a7ca5', fg='white',
                           command=lambda: removeProductEvent(room_combobox,
                                                              combobox_service,
                                                              ser_table))
    delete_btn.place(x=200, y=170, width=80, height=40)
    # Nút clear thông tin
    clear_btn = tk.Button(head_frame, text='Làm sạch', font=('Bold', 12), bg='#3a7ca5', fg='white',
                          command=lambda: clear_cobobox_and_textfield(
                              room_combobox,
                              combobox_service,
                              customer_quantity_text_field,
                              ser_table
                          ))
    clear_btn.place(x=290, y=170, width=80, height=40)

    head_frame.pack(pady=0)
    head_frame.pack_propagate(False)
    head_frame.configure(width=1038, height=225)

    # Frame mới cho nút tìm kiếm
    search_bar_frame = tk.Frame(service_frame, bg='#3a7ca5')
    search_lb = tk.Label(search_bar_frame, text="Danh Sách Dịch Vụ Của Phòng", font=('Bold', 12))
    search_lb.place(x=20, y=10, height=30)

    search_bar_frame.pack(pady=0)
    search_bar_frame.pack_propagate(False)
    search_bar_frame.configure(width=1038, height=50)

    # Frame mới cho bảng thông tin dịch v
    table_ser_frame = tk.Frame(service_frame, bg='white')

    ser_table = ttk.Treeview(table_ser_frame)
    ser_table.place(x=0, y=0, width=1000, height=280)

    ser_table['column'] = ['Room', 'NameService', 'Unit', 'Quantity']
    ser_table.column('#0', anchor=tk.W, width=0, stretch=tk.NO)

    style = ttk.Style()
    style.configure("Treeview", background="#EEEEEE", font=('Arial', 12))

    ser_table.column('Room', anchor=tk.W, width=120)
    ser_table.column('NameService', anchor=tk.W, width=120)
    ser_table.column('Unit', anchor=tk.W, width=60)
    ser_table.column('Quantity', anchor=tk.W, width=60)

    heading_font = ("Arial", 11, "bold")

    style.configure("Treeview.Heading", font=heading_font)
    ser_table.heading('Room', text='Tên Phòng', anchor=tk.W)
    ser_table.heading('Unit', text='Đơn Vị Tính', anchor=tk.W)
    ser_table.heading('NameService', text='Tên Dịch Vụ', anchor=tk.W)
    ser_table.heading('Quantity', text='Số Lượng', anchor=tk.W)

    # đọc ra dữ liệu từ hàm refreshTable()
    # loadDataRoomUsing(ser_table)
    ser_table.bind('<ButtonRelease-1>',
                   lambda event: handle_click_table_service(ser_table, combobox_service, customer_quantity_text_field))

    table_ser_frame.pack(pady=5)
    table_ser_frame.pack_propagate(False)
    table_ser_frame.configure(width=1038, height=320, padx=20)
    # kết thúc

    service_frame.pack(pady=0)


# Hàm ẩn thanh hoạt động
def hide_indicators():
    booking_indicate.config(bg='#20C563')
    room_indicate.config(bg='#20C563')
    customer_indicate.config(bg='#20C563')
    manage_indicate.config(bg='#20C563')
    employee_indicate.config(bg='#20C563')
    static_indicate.config(bg='#20C563')


# Hàm xóa frame khác khi chọn vào 1 frame được chọn
def delete_pages():
    for frame in main_frame.winfo_children():
        frame.destroy()


# Hàm tạo thanh hoạt động
def indicate(lb, page):
    hide_indicators()
    lb.config(bg='#4B7CC4')
    delete_pages()
    page()


options_frame = tk.Frame(root, bg='#FAC4AB')

booking_btn = tk.Button(options_frame, text='Đặt Phòng', font=('Bold', 15), fg='#158aff', bd=0, bg='#FFFDFF',
                        command=lambda: indicate(booking_indicate, booking_page))
booking_btn.place(x=10, y=30, width=140)
booking_indicate = tk.Label(options_frame, text='', bg='#20C563')
booking_indicate.place(x=3, y=30, width=5, height=40)

room_btn = tk.Button(options_frame, text='Thanh Toán', font=('Bold', 15), fg='#158aff', bd=0, bg='#FFFDFF',
                     command=lambda: indicate(room_indicate, room_page))
room_btn.place(x=10, y=90, width=140)
room_indicate = tk.Label(options_frame, text='', bg='#20C563')
room_indicate.place(x=3, y=90, width=5, height=40)

manage_btn = tk.Button(options_frame, text='Dịch Vụ', font=('Bold', 15), fg='#158aff', bd=0, bg='#FFFDFF',
                       command=lambda: indicate(manage_indicate, service_page))
manage_btn.place(x=10, y=150, width=140)
manage_indicate = tk.Label(options_frame, text='', bg='#20C563')
manage_indicate.place(x=3, y=150, width=5, height=40)

customer_btn = tk.Button(options_frame, text='Khách Hàng', font=('Bold', 15), fg='#158aff', bd=0, bg='#FFFDFF',
                         command=lambda: indicate(customer_indicate, customer_page))
customer_btn.place(x=10, y=210, width=140)
customer_indicate = tk.Label(options_frame, text='', bg='#20C563')
customer_indicate.place(x=3, y=210, width=5, height=40)

employee_btn = tk.Button(options_frame, text='Nhân Viên', font=('Bold', 15), fg='#158aff', bd=0, bg='#FFFDFF',
                         command=lambda: indicate(employee_indicate, employee_page))
employee_btn.place(x=10, y=270, width=140)
employee_indicate = tk.Label(options_frame, text='', bg='#20C563')
employee_indicate.place(x=3, y=270, width=5, height=40)

static_btn = tk.Button(options_frame, text='Thống Kê', font=('Bold', 15), fg='#158aff', bd=0, bg='#FFFDFF',
                       command=lambda: indicate(static_indicate, static_page))
static_btn.place(x=10, y=330, width=140)
static_indicate = tk.Label(options_frame, text='', bg='#20C563')
static_indicate.place(x=3, y=330, width=5, height=40)

options_frame.pack(side=tk.LEFT)
options_frame.pack_propagate(False)
options_frame.configure(width=160, height=680)

main_frame = tk.Frame(root, bg='#ffffff', highlightbackground='#FFFDFF', highlightthickness=2)
main_frame.pack(side=tk.LEFT)
main_frame.pack_propagate(False)
main_frame.configure(width=1038, height=680)


def insert_image(frame):
    image_path = "E:\\New folder\\python-tkinter-karaoke\\public\\peach.png"

    image = tk.PhotoImage(file=image_path)

    image_label = tk.Label(frame, image=image, bg='#ffffff')
    image_label.image = image  # Đảm bảo giữ tham chiếu đến ảnh để ngăn Python thu giữ nó

    image_label.pack()


class Person(ABC):
    __id = 0

    def __init__(self, id, name, phone, address):
        self.__id = id if id is not None else Person.count_id()
        self.__name = name
        self.__phone = phone
        self.__address = address

    @classmethod
    def count_id(cls):
        cls.__id += 1
        return cls.__id

    @classmethod
    def set_id(cls, value):
        cls.__id = value

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def phone(self):
        return self.__phone

    @property
    def address(self):
        return self.__address

    @name.setter
    def name(self, value):
        self.__name = value

    @phone.setter
    def phone(self, value):
        self.__phone = value

    @address.setter
    def address(self, value):
        self.__address = value

    @abstractmethod
    def get_salary(self):
        pass

    def get_position(self):
        pass

    def get_work_time(self):
        pass


class Manager(Person):
    def __init__(self, name, phone, address, position, salary, work_time, bonus, id):
        super().__init__(id, name, phone, address)
        self.__position = position
        self.__salary = salary
        self.__worktime = work_time
        self.__bonus = bonus

    def get_salary(self):
        return int(self.__salary) + int(self.__bonus)

    def get_position(self):
        return self.__position

    def get_work_time(self):
        return self.__worktime

    @property
    def position(self):
        return self.__position

    @property
    def salary(self):
        return self.__salary

    @property
    def worktime(self):
        return self.__worktime

    @property
    def bonus(self):
        return self.__bonus

    @position.setter
    def position(self, value):
        self.__position = value

    @salary.setter
    def salary(self, value):
        self.__salary = value

    @worktime.setter
    def worktime(self, value):
        self.__worktime = value

    @bonus.setter
    def bonus(self, value):
        self.__worktime = value


class Employee(Person):
    def __init__(self, name, phone, address, position, salary, work_time, id):
        super().__init__(id, name, phone, address)
        self.__position = position
        self.__salary = salary
        self.__worktime = work_time

    def get_salary(self):
        return self.__salary

    def get_position(self):
        return self.__position

    def get_work_time(self):
        return self.__worktime

    @property
    def position(self):
        return self.__position

    @property
    def salary(self):
        return self.__salary

    @property
    def worktime(self):
        return self.__worktime

    @position.setter
    def position(self, value):
        self.__position = value

    @salary.setter
    def salary(self, value):
        self.__salary = value

    @worktime.setter
    def worktime(self, value):
        self.__worktime = value
    # Hàm trang nhân sự


insert_image(main_frame)
root.mainloop()
