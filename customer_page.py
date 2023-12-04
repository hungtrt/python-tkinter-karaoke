from datetime import datetime
from tkinter import messagebox

import mysql
from unidecode import unidecode

from connectionDB import connection


def removeCustomerByPhone(phone):
    phone = phone.get()
    conn = connection()
    cursor = conn.cursor()
    query = """delete from customer where phone = %s"""
    cursor.execute(query, (phone,))
    conn.commit()


def add_customer(nameEntry, phoneEntry, addressEntry, amountConsumedEntry):
    name = str(nameEntry.get())
    phone = str(phoneEntry.get())
    address = str(addressEntry.get())
    amount_consumed = int(amountConsumedEntry.get()) if amountConsumedEntry.get() else 0

    # Các trường tự động cập nhật
    # Cập nhật ưu đãi và loại khách hàng dựa trên số tiền đã tiêu
    if (amount_consumed < 0):
        messagebox.showinfo("Error", "Vui lòng nhập tiền thanh toán không âm!")
        return
    if amount_consumed < 1500000:
        customer_incentives = 3
        type = str('Membership')
    elif 1500000 <= amount_consumed < 3000000:
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
            query = """
                SELECT phone
                FROM customer
                WHERE phone = %s
                """
            cursor.execute(query, (phone,))
            check = cursor.fetchone()
            if check is not None:
                messagebox.showinfo("Error", "Số điện thoại đã được dùng. Vui lòng thử lại!")
                return

            name_convert = name.split()
            first_name = name_convert[-1]
            last_name = name_convert[0]
            first_name_without_diacritics = ''.join(char for char in first_name if char.isalnum())
            last_name_without_diacritics = ''.join(char for char in last_name if char.isalnum())
            name_result = first_name_without_diacritics + last_name_without_diacritics
            name_result = unidecode(name_result)
            name_id = name_result + phone[-4:]


            cursor.execute(
                "INSERT INTO customer (name,name_id, phone, address, type, customer_incentives, amount_consumed, created_date) VALUES (%s,%s, %s, %s, %s, %s, %s, %s)",
                (name, name_id, phone, address, type, customer_incentives, amount_consumed, created_date))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Lưu Khách Hàng Thành Công!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            messagebox.showinfo("Error", "Vui lòng thử lại")
            return


def update_customer(nameEntry, phoneEntry, addressEntry, lb_id):
    id_lb = lb_id.cget("text")
    name = str(nameEntry.get())
    phone = str(phoneEntry.get())
    address = str(addressEntry.get())
    updated_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not (name and phone and address):
        messagebox.showinfo("Error", "Bạn chưa nhập đủ thông tin!")
        return
    else:
        try:
            conn = connection()
            cursor = conn.cursor()
            query = """
                            SELECT phone
                            FROM customer
                            WHERE phone = %s and name_id <> %s
                            """
            cursor.execute(query, (phone,id_lb))
            check = cursor.fetchone()
            if check is not None:
                messagebox.showinfo("Error", "Số điện thoại đã được dùng. Vui lòng thử lại!")
                return

            name_convert = name.split()
            first_name = name_convert[-1]
            last_name = name_convert[0]
            first_name_without_diacritics = ''.join(char for char in first_name if char.isalnum())
            last_name_without_diacritics = ''.join(char for char in last_name if char.isalnum())
            name_result = first_name_without_diacritics + last_name_without_diacritics
            name_result = unidecode(name_result)
            name_id = name_result + phone[-4:]

            cursor.execute(
                "UPDATE customer "
                "SET name = %s, phone= %s, address = %s, name_id = %s, updated_date = %s "
                "where name_id = %s",
                (name, phone, address, name_id, updated_date, id_lb))

            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Cập Khách Hàng Thành Công!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            messagebox.showinfo("Error", "Vui lòng thử lại")
            return

