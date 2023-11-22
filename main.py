import tkinter as tk
from tkinter import ttk
import mysql.connector
from tkinter import messagebox
from datetime import datetime
from tkinter import StringVar


# Kết nối database
def connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="170801",
        database="karaoke"
    )
    return conn


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
        "SELECT name, phone, address, type, customer_incentives  FROM customer where name != 'Vãng Lai' order by customer_incentives desc")
    results = cursor.fetchall()
    conn.commit()
    conn.close()
    return results


# Ghi dữ liệu vào bảng customer
def add_customer(cus_table, nameEntry, phoneEntry, addressEntry, amountConsumedEntry):
    name = str(nameEntry.get())
    phone = str(phoneEntry.get())
    address = str(addressEntry.get())
    amount_consumed = int(amountConsumedEntry.get()) if amountConsumedEntry.get() else 0

    # Các trường tự động cập nhật
    # Cập nhật ưu đãi và loại khách hàng dựa trên số tiền đã tiêu
    if amount_consumed < 1000000:
        customer_incentives = 3
        type = str('Membership')
    elif 1000000 <= amount_consumed < 3000000:
        customer_incentives = 5
        type = str('Vip1')
    elif 3000000 <= amount_consumed < 5000000:
        customer_incentives = 8
        type = str('Vip2')
    else:
        customer_incentives = 10
        type = str('Vip3')

    created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not (name and phone and address):
        messagebox.showinfo("Error", "Bạn chưa nhập đủ thông tin!")
        return
    else:
        try:
            conn = connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO customer (name, phone, address, type, customer_incentives, amount_consumed, created_date) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (name, phone, address, type, customer_incentives, amount_consumed, created_date))
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            messagebox.showinfo("Error", "Vui lòng thử lại")
            return
    refreshTable(cus_table)


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


# Đọc dữ liệu từ bảng phòng
def read_room():
    conn = connection()
    cursor = conn.cursor()

    query = """
        SELECT room.name, room.volume, room.description, room.status, room_rates.unit_price
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
        ORDER BY room_rates.unit_price;
    """

    current_hour = get_current_hour()
    cursor.execute(query, (current_hour, current_hour, current_hour, current_hour))
    results = cursor.fetchall()
    conn.close()

    return results


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
                cursor.execute("SELECT id FROM customer WHERE name = %s", (customer_name,))
                result = cursor.fetchone()

                if result is not None:
                    customer_id = result[0]

                    # Lưu thông tin vào bảng booking_room
                    cursor.execute("INSERT INTO booking_room (id_room, id_customer, created_date) VALUES (%s, %s, %s)",
                                   (room_id, customer_id, created_date))

                    # Cập nhật trạng thái của phòng thành 'active'
                    cursor.execute("UPDATE room SET status = 'active' WHERE id = %s", (room_id,))

                    conn.commit()
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
                           room.status
                       FROM
                           booking_room
                       JOIN room ON booking_room.id_room = room.id
                       JOIN customer ON booking_room.id_customer = customer.id;
                   """
        cursor.execute(query)
        booking_info = cursor.fetchall()
        conn.close()
        return booking_info
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


# Lưu service

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

                        # Lưu thông tin vào bảng service_detail
                        cursor.execute(
                            "INSERT INTO service_detail (id_service, booking_room_id, quantity, created_date) VALUES (%s, %s, %s, %s)",
                            (service_id, booking_room_id, quantity, created_date))

                        # Cập nhật updated_date của booking room
                        cursor.execute(
                            "UPDATE booking_room SET updated_date = NOW() WHERE id = %s AND updated_date IS NULL",
                            (booking_room_id,))
                        conn.commit()
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

        loadDataRoomUsing(booking_table)


# KẾT THÚC XỬ LÝ TRANG QUẢN LÝ PHÒNG ĐANG SỬ DỤNG

root = tk.Tk()
# root.geometry('1000x600')
root.title('Thiên Thai Karaoke')

window_width = 1200
window_height = 680
root.geometry(f"{window_width}x{window_height}")

center_window(root, window_width, window_height)


# Hàm Đặt Phòng
def booking_page():
    booking_frame = tk.Frame(main_frame)

    head_frame = tk.Frame(booking_frame, bg='green')

    heading_lb = tk.Label(booking_frame, text="Quản Lý Đặt Phòng", font=('Bold', 22), bg='green')
    heading_lb.pack(fill=tk.X, pady=1)

    # Label Tên Phòng Trống
    customer_name_lb = tk.Label(head_frame, text='Tên Phòng: ', font=('Bold', 12))
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
    customer_phone_lb = tk.Label(head_frame, text='Khách Hàng: ', font=('Bold', 12))
    customer_phone_lb.place(x=20, y=75, width=160, height=30)
    # Select box
    c.execute("SELECT name FROM `customer` order by type desc")
    options = [row[0] for row in c.fetchall()]
    selected_cus = StringVar(head_frame)
    combobox_cus = ttk.Combobox(head_frame, textvariable=selected_cus, values=options,
                                font=('verdana', 13))
    combobox_cus.place(x=200, y=75, width=350, height=30)

    # Nút lưu thông tin
    save_btn = tk.Button(head_frame, text='Lưu', font=('Bold', 12), bg='blue',
                         command=lambda: saveBookingRoom(cus_table, combobox_room, combobox_cus))
    save_btn.place(x=570, y=70, width=80, height=40)
    # Nút cập nhật thông tin
    update_btn = tk.Button(head_frame, text='Cập nhật', font=('Bold', 12), bg='blue')
    update_btn.place(x=660, y=70, width=80, height=40)
    # Nút clear thông tin
    clear_btn = tk.Button(head_frame, text='Làm sạch', font=('Bold', 12), bg='blue')
    clear_btn.place(x=750, y=70, width=80, height=40)

    head_frame.pack(pady=1)
    head_frame.pack_propagate(False)
    head_frame.configure(width=1038, height=120)

    # Frame mới cho nút tìm kiếm
    search_bar_frame = tk.Frame(booking_frame, bg='blue')
    search_lb = tk.Label(search_bar_frame, text="Danh sách Phòng Trống", font=('Bold', 12))
    search_lb.place(x=20, y=2, height=30)

    search_bar_frame.pack(pady=0)
    search_bar_frame.pack_propagate(False)
    search_bar_frame.configure(width=1038, height=40)

    # Frame mới cho bảng thông tin đặt phòng
    table_cus_frame = tk.Frame(booking_frame, bg='green')

    cus_table = ttk.Treeview(table_cus_frame)
    cus_table.place(x=0, y=10, width=1000, height=360)

    cus_table['column'] = ['Name', 'Volume', 'Description', 'Status', 'CurrentPrice']
    cus_table.column('#0', anchor=tk.W, width=0, stretch=tk.NO)

    # cus_table.column('ID', anchor=tk.W, width=50)
    cus_table.column('Name', anchor=tk.W, width=100)
    cus_table.column('Volume', anchor=tk.W, width=50)
    cus_table.column('Description', anchor=tk.W, width=350)
    cus_table.column('Status', anchor=tk.W, width=30)
    cus_table.column('CurrentPrice', anchor=tk.W, width=40)

    heading_font = ("Arial", 11, "bold")
    style = ttk.Style()
    style.configure("Treeview.Heading", font=heading_font)
    # cus_table.heading('ID', text='Mã Phòng', anchor=tk.W)
    cus_table.heading('Name', text='Tên Phòng', anchor=tk.W)
    cus_table.heading('Volume', text='Lượng người', anchor=tk.W)
    cus_table.heading('Description', text='Mô Tả Phòng', anchor=tk.W)
    cus_table.heading('Status', text='Trạng Thái', anchor=tk.W)
    cus_table.heading('CurrentPrice', text='Giá Hiện tại', anchor=tk.W)

    # đọc ra dữ liệu từ hàm loadTableRoomNull()
    loadTableRoomNull(cus_table)

    table_cus_frame.pack(pady=5)
    table_cus_frame.pack_propagate(False)
    table_cus_frame.configure(width=1038, height=420, padx=20)
    # kết thúc

    booking_frame.pack(pady=10)


# Hàm Phòng Đang Sử Dụng
def room_page():
    room_frame = tk.Frame(main_frame)

    head_frame = tk.Frame(room_frame, bg='green')

    heading_lb = tk.Label(room_frame, text="Quản Lý Phòng Đang Sử Dụng", font=('Bold', 22), bg='green')
    heading_lb.pack(fill=tk.X, pady=1)

    # Label và textfields 
    customer_name_lb = tk.Label(head_frame, text='Tên Khách Hàng: ', font=('Bold', 12))
    customer_name_lb.place(x=20, y=25, width=160, height=30)
    customer_name_text_field = tk.Entry(head_frame, font=('Bold', 12))
    customer_name_text_field.place(x=200, y=25, width=350, height=30)

    customer_phone_lb = tk.Label(head_frame, text='Số điện thoại: ', font=('Bold', 12))
    customer_phone_lb.place(x=20, y=75, width=160, height=30)
    customer_phone_text_field = tk.Entry(head_frame, font=('Bold', 12))
    customer_phone_text_field.place(x=200, y=75, width=350, height=30)

    customer_address_lb = tk.Label(head_frame, text='Địa chỉ: ', font=('Bold', 12))
    customer_address_lb.place(x=20, y=125, width=160, height=30)
    customer_address_text_field = tk.Entry(head_frame, font=('Bold', 12))
    customer_address_text_field.place(x=200, y=125, width=350, height=30)

    amount_consumed_lb = tk.Label(head_frame, text='Thanh Toán: ', font=('Bold', 12))
    amount_consumed_lb.place(x=20, y=175, width=160, height=30)
    amount_consumed_text_field = tk.Entry(head_frame, font=('Bold', 12))
    amount_consumed_text_field.place(x=200, y=175, width=350, height=30)

    # Nút lưu thông tin 
    save_btn = tk.Button(head_frame, text='Lưu', font=('Bold', 12), bg='blue',
                         command=lambda: add_customer(cus_table, customer_name_text_field, customer_phone_text_field,
                                                      customer_address_text_field, amount_consumed_text_field))
    save_btn.place(x=570, y=170, width=80, height=40)
    # Nút cập nhật thông tin 
    update_btn = tk.Button(head_frame, text='Cập nhật', font=('Bold', 12), bg='blue')
    update_btn.place(x=660, y=170, width=80, height=40)
    # Nút xóa thông tin 
    delete_btn = tk.Button(head_frame, text='Xóa', font=('Bold', 12), bg='blue')
    delete_btn.place(x=750, y=170, width=80, height=40)
    # Nút clear thông tin
    clear_btn = tk.Button(head_frame, text='Làm sạch', font=('Bold', 12), bg='blue')
    clear_btn.place(x=840, y=170, width=80, height=40)

    head_frame.pack(pady=1)
    head_frame.pack_propagate(False)
    head_frame.configure(width=1038, height=225)

    # Frame mới cho nút tìm kiếm
    search_bar_frame = tk.Frame(room_frame, bg='blue')
    search_lb = tk.Label(search_bar_frame, text="Danh Sách Phòng Đang Được Sử Dụng", font=('Bold', 12))
    search_lb.place(x=20, y=10, height=30)

    search_bar_frame.pack(pady=0)
    search_bar_frame.pack_propagate(False)
    search_bar_frame.configure(width=1038, height=50)

    # Frame mới cho bảng thông tin phòng đang sử dụng
    table_cus_frame = tk.Frame(room_frame, bg='green')

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
    cus_table.heading('Status', text='Trạng Thái', anchor=tk.W)

    # đọc ra dữ liệu từ hàm refreshTable()
    loadDataRoomUsing(cus_table)

    table_cus_frame.pack(pady=5)
    table_cus_frame.pack_propagate(False)
    table_cus_frame.configure(width=1038, height=320, padx=20)
    # kết thúc

    room_frame.pack(pady=10)


# Hàm Trang Khách Hàng
def customer_page():
    customer_frame = tk.Frame(main_frame)

    head_frame = tk.Frame(customer_frame, bg='green')

    heading_lb = tk.Label(customer_frame, text="Khách Hàng Thân Thiết", font=('Bold', 22), bg='green')
    heading_lb.pack(fill=tk.X, pady=1)

    # Label và textfields 
    customer_name_lb = tk.Label(head_frame, text='Tên Khách Hàng: ', font=('Bold', 12))
    customer_name_lb.place(x=20, y=25, width=160, height=30)
    customer_name_text_field = tk.Entry(head_frame, font=('Bold', 12))
    customer_name_text_field.place(x=200, y=25, width=350, height=30)

    customer_phone_lb = tk.Label(head_frame, text='Số điện thoại: ', font=('Bold', 12))
    customer_phone_lb.place(x=20, y=75, width=160, height=30)
    customer_phone_text_field = tk.Entry(head_frame, font=('Bold', 12))
    customer_phone_text_field.place(x=200, y=75, width=350, height=30)

    customer_address_lb = tk.Label(head_frame, text='Địa chỉ: ', font=('Bold', 12))
    customer_address_lb.place(x=20, y=125, width=160, height=30)
    customer_address_text_field = tk.Entry(head_frame, font=('Bold', 12))
    customer_address_text_field.place(x=200, y=125, width=350, height=30)

    amount_consumed_lb = tk.Label(head_frame, text='Thanh Toán: ', font=('Bold', 12))
    amount_consumed_lb.place(x=20, y=175, width=160, height=30)
    amount_consumed_text_field = tk.Entry(head_frame, font=('Bold', 12))
    amount_consumed_text_field.place(x=200, y=175, width=350, height=30)

    # Nút lưu thông tin 
    save_btn = tk.Button(head_frame, text='Lưu', font=('Bold', 12), bg='blue',
                         command=lambda: add_customer(cus_table, customer_name_text_field, customer_phone_text_field,
                                                      customer_address_text_field, amount_consumed_text_field))
    save_btn.place(x=570, y=170, width=80, height=40)
    # Nút cập nhật thông tin 
    update_btn = tk.Button(head_frame, text='Cập nhật', font=('Bold', 12), bg='blue')
    update_btn.place(x=660, y=170, width=80, height=40)
    # Nút xóa thông tin 
    delete_btn = tk.Button(head_frame, text='Xóa', font=('Bold', 12), bg='blue')
    delete_btn.place(x=750, y=170, width=80, height=40)
    # Nút clear thông tin
    clear_btn = tk.Button(head_frame, text='Làm sạch', font=('Bold', 12), bg='blue')
    clear_btn.place(x=840, y=170, width=80, height=40)
    # Nút sắp xếp thông tin theo created_date mới nhất
    clear_btn = tk.Button(head_frame, text='Sắp xếp', font=('Bold', 12), bg='blue')
    clear_btn.place(x=930, y=170, width=80, height=40)

    head_frame.pack(pady=1)
    head_frame.pack_propagate(False)
    head_frame.configure(width=1038, height=225)

    # Frame mới cho nút tìm kiếm
    search_bar_frame = tk.Frame(customer_frame, bg='blue')
    search_lb = tk.Label(search_bar_frame, text="Tìm kiếm khách hàng bằng SĐT", font=('Bold', 12))
    search_lb.place(x=20, y=10, height=30)

    search_entry = tk.Entry(search_bar_frame, font=('Bold', 12))
    search_entry.place(x=260, y=10, height=30, width=290)

    search_bar_frame.pack(pady=0)
    search_bar_frame.pack_propagate(False)
    search_bar_frame.configure(width=1038, height=50)

    # Frame mới cho bảng thông tin khách hàng

    table_cus_frame = tk.Frame(customer_frame, bg='green')

    cus_table = ttk.Treeview(table_cus_frame)
    cus_table.place(x=0, y=0, width=1000, height=320)

    cus_table['column'] = ['Name', 'Phone', 'Address', 'Type', 'Incentives']
    cus_table.column('#0', anchor=tk.W, width=0, stretch=tk.NO)

    cus_table.column('Name', anchor=tk.W, width=160)
    cus_table.column('Phone', anchor=tk.W, width=80)
    cus_table.column('Address', anchor=tk.W, width=250)
    cus_table.column('Type', anchor=tk.W, width=60)
    cus_table.column('Incentives', anchor=tk.W, width=40)

    heading_font = ("Arial", 11, "bold")
    style = ttk.Style()
    style.configure("Treeview.Heading", font=heading_font)
    cus_table.heading('Name', text='Tên Khách Hàng', anchor=tk.W)
    cus_table.heading('Phone', text='Số Điện Thoại', anchor=tk.W)
    cus_table.heading('Address', text='Địa Chỉ', anchor=tk.W)
    cus_table.heading('Type', text='Loại khách Hàng', anchor=tk.W)
    cus_table.heading('Incentives', text='Mức Ưu đãi (%)', anchor=tk.W)

    # đọc ra dữ liệu từ hàm refreshTable()
    refreshTable(cus_table)

    table_cus_frame.pack(pady=5)
    table_cus_frame.pack_propagate(False)
    table_cus_frame.configure(width=1038, height=320, padx=20)
    # kết thúc

    customer_frame.pack(pady=10)


# Hàm Trang Dịch Vụ
def service_page():
    service_frame = tk.Frame(main_frame)

    head_frame = tk.Frame(service_frame, bg='green')

    heading_lb = tk.Label(service_frame, text=" Dịch Vụ Phòng KARAOKE", font=('Bold', 22), bg='green')
    heading_lb.pack(fill=tk.X, pady=1)

    # Label tên phòng đang sử dụng
    customer_name_lb = tk.Label(head_frame, text='Tên Phòng: ', font=('Bold', 12))
    customer_name_lb.place(x=20, y=25, width=160, height=30)
    # Select box
    connection = mysql.connector.connect(host='localhost', user='root',
                                         password='170801', database='karaoke')
    c = connection.cursor()
    c.execute("SELECT name FROM `room` where status = 'active'")
    options = [row[0] for row in c.fetchall()]
    selected_room = StringVar(head_frame)
    combobox_room = ttk.Combobox(head_frame, textvariable=selected_room, values=options,
                                 font=('verdana', 13))
    combobox_room.place(x=200, y=25, width=350, height=30)

    # Label tên sản phẩm
    customer_phone_lb = tk.Label(head_frame, text='Tên Sản Phẩm: ', font=('Bold', 12))
    customer_phone_lb.place(x=20, y=75, width=160, height=30)
    # Select box
    c.execute("SELECT name FROM `service` order by unit_price desc")
    options = [row[0] for row in c.fetchall()]
    selected_cus = StringVar(head_frame)
    combobox_service = ttk.Combobox(head_frame, textvariable=selected_cus, values=options,
                                font=('verdana', 13))
    combobox_service.place(x=200, y=75, width=350, height=30)

    customer_quantity_lb = tk.Label(head_frame, text='Số Lượng: ', font=('Bold', 12))
    customer_quantity_lb.place(x=20, y=125, width=160, height=30)
    customer_quantity_text_field = tk.Entry(head_frame, font=('Bold', 12))
    customer_quantity_text_field.place(x=200, y=125, width=350, height=30)

    # Nút lưu thông tin
    save_btn = tk.Button(head_frame, text='Lưu', font=('Bold', 12), bg='blue', command=lambda: saveService(cus_table, combobox_room, combobox_service,customer_quantity_text_field ))
    save_btn.place(x=20, y=170, width=80, height=40)
    # Nút cập nhật thông tin
    update_btn = tk.Button(head_frame, text='Cập nhật', font=('Bold', 12), bg='blue')
    update_btn.place(x=110, y=170, width=80, height=40)
    # Nút xóa thông tin 
    delete_btn = tk.Button(head_frame, text='Xóa', font=('Bold', 12), bg='blue')
    delete_btn.place(x=200, y=170, width=80, height=40)
    # Nút clear thông tin
    clear_btn = tk.Button(head_frame, text='Làm sạch', font=('Bold', 12), bg='blue')
    clear_btn.place(x=290, y=170, width=80, height=40)
    # Nút sắp xếp thông tin theo created_date mới nhất
    clear_btn = tk.Button(head_frame, text='Sắp xếp', font=('Bold', 12), bg='blue')
    clear_btn.place(x=380, y=170, width=80, height=40)

    head_frame.pack(pady=1)
    head_frame.pack_propagate(False)
    head_frame.configure(width=1038, height=225)

    # Frame mới cho nút tìm kiếm
    search_bar_frame = tk.Frame(service_frame, bg='blue')
    search_lb = tk.Label(search_bar_frame, text="Danh Sách Dịch Vụ Của Phòng", font=('Bold', 12))
    search_lb.place(x=20, y=10, height=30)

    search_bar_frame.pack(pady=0)
    search_bar_frame.pack_propagate(False)
    search_bar_frame.configure(width=1038, height=50)

    # Frame mới cho bảng thông tin khách hàng

    table_cus_frame = tk.Frame(service_frame, bg='green')

    cus_table = ttk.Treeview(table_cus_frame)
    cus_table.place(x=0, y=0, width=1000, height=280)

    cus_table['column'] = ['Room', 'NameService','Unit', 'Quantity']
    cus_table.column('#0', anchor=tk.W, width=0, stretch=tk.NO)

    cus_table.column('Room', anchor=tk.W, width=120)
    cus_table.column('NameService', anchor=tk.W, width=120)
    cus_table.column('Unit', anchor=tk.W, width=60)
    cus_table.column('Quantity', anchor=tk.W, width=60)

    heading_font = ("Arial", 11, "bold")
    style = ttk.Style()
    style.configure("Treeview.Heading", font=heading_font)
    cus_table.heading('Room', text='Tên Phòng', anchor=tk.W)
    cus_table.heading('Unit', text='Đơn Vị Tính', anchor=tk.W)
    cus_table.heading('NameService', text='Tên Dịch Vụ', anchor=tk.W)
    cus_table.heading('Quantity', text='Số Lượng', anchor=tk.W)

    # đọc ra dữ liệu từ hàm refreshTable()
    loadDataRoomUsing(cus_table)

    table_cus_frame.pack(pady=5)
    table_cus_frame.pack_propagate(False)
    table_cus_frame.configure(width=1038, height=320, padx=20)
    # kết thúc

    service_frame.pack(pady=10)


# Hàm ẩn thanh hoạt động
def hide_indicators():
    booking_indicate.config(bg='#20C563')
    room_indicate.config(bg='#20C563')
    customer_indicate.config(bg='#20C563')
    manage_indicate.config(bg='#20C563')


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


options_frame = tk.Frame(root, bg='#20C563')

booking_btn = tk.Button(options_frame, text='Đặt Phòng', font=('Bold', 15), fg='#158aff', bd=0, bg='#FFFDFF',
                        command=lambda: indicate(booking_indicate, booking_page))
booking_btn.place(x=10, y=30)
booking_indicate = tk.Label(options_frame, text='', bg='#20C563')
booking_indicate.place(x=3, y=30, width=5, height=40)

room_btn = tk.Button(options_frame, text='Thanh Toán', font=('Bold', 15), fg='#158aff', bd=0, bg='#FFFDFF',
                     command=lambda: indicate(room_indicate, room_page))
room_btn.place(x=10, y=90)
room_indicate = tk.Label(options_frame, text='', bg='#20C563')
room_indicate.place(x=3, y=90, width=5, height=40)

manage_btn = tk.Button(options_frame, text='Dịch Vụ', font=('Bold', 15), fg='#158aff', bd=0, bg='#FFFDFF',
                       command=lambda: indicate(manage_indicate, service_page))
manage_btn.place(x=10, y=150)
manage_indicate = tk.Label(options_frame, text='', bg='#20C563')
manage_indicate.place(x=3, y=150, width=5, height=40)

customer_btn = tk.Button(options_frame, text='Khách Hàng', font=('Bold', 15), fg='#158aff', bd=0, bg='#FFFDFF',
                         command=lambda: indicate(customer_indicate, customer_page))
customer_btn.place(x=10, y=210)
customer_indicate = tk.Label(options_frame, text='', bg='#20C563')
customer_indicate.place(x=3, y=210, width=5, height=40)

options_frame.pack(side=tk.LEFT)
options_frame.pack_propagate(False)
options_frame.configure(width=160, height=680)

main_frame = tk.Frame(root, bg='#E5F2FF', highlightbackground='#80A7DD', highlightthickness=2)
main_frame.pack(side=tk.LEFT)
main_frame.pack_propagate(False)
main_frame.configure(width=1038, height=680)

root.mainloop()
