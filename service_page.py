from tkinter import messagebox

import mysql

from connectionDB import connection


def returnProduct(roomNamed, productd, quantity_request, ser_table):
    roomNamedata = roomNamed.get()
    product = productd.get()
    quantity_request = int(quantity_request.get()) if quantity_request.get() else 0

    conn = connection()
    cursor = conn.cursor()

    query = """
               select id
               from service
               where name = %s
           """
    cursor.execute(query, (product,))
    id_service = cursor.fetchone()[0]

    query = """
           select sd.id
           from service_detail sd
           join booking_room br on br.id = sd.booking_room_id
           join room r on r.id = br.id_room
           join service s on s.id = sd.id_service
           WHERE r.name = %s AND br.ended_time IS NULL and s.id = %s
       """
    cursor.execute(query, (roomNamedata, id_service))
    id_service_detail = cursor.fetchone()[0]

    query = """
               select quantity
               from service_detail
               WHERE id = %s
           """

    cursor.execute(query, (id_service_detail,))
    quantity = cursor.fetchone()[0]

    quantity_final = quantity - quantity_request
    if (quantity_final < 0):
        messagebox.showinfo("Success", "Số Lượng Sản Phẩm Không Hợp Lệ!")
        return 0
    if (quantity_final == 0):
        removeProduct(roomNamed, productd)

    query = """UPDATE service_detail SET quantity = %s  WHERE id = %s"""
    cursor.execute(query, (quantity_final, id_service_detail))
    conn.commit()
    messagebox.showinfo("Success", "Trả Sản Phẩm Thành Công!")


def removeProduct(roomName, product):
    roomName = roomName.get()
    product = product.get()

    conn = connection()
    cursor = conn.cursor()

    query = """
                   select id
                   from service
                   where name = %s
               """
    cursor.execute(query, (product,))
    id_service = cursor.fetchone()[0]

    query = """
               select sd.id
               from service_detail sd
               join booking_room br on br.id = sd.booking_room_id
               join room r on r.id = br.id_room
               join service s on s.id = sd.id_service
               WHERE r.name = %s AND br.ended_time IS NULL and s.id = %s
           """
    cursor.execute(query, (roomName, id_service))
    id_service_detail = cursor.fetchone()[0]

    query = """delete from service_detail where id = %s"""

    cursor.execute(query, (id_service_detail,))
    conn.commit()
