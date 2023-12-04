from datetime import timedelta, datetime
import mysql.connector
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from CheckoutFunction import get_incentives_percent
from pdf.temp_invoice import my_temp
from room_calculation import total_for_frame_time_from_database


def connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="170801",
        database="karaoke"
    )
    return conn


# Check room_id từ tên phòng
def id_room(room_name):
    conn = connection()
    cursor = conn.cursor()
    query = """
            SELECT id
            FROM room
            WHERE name = %s
        """
    cursor.execute(query, (room_name,))
    results = cursor.fetchone()
    return results[0]


# Check id_booking_room từ room_id
def id_booking_room(id_room):
    conn = connection()
    cursor = conn.cursor()
    query = """
                SELECT id 
                FROM booking_room
                WHERE id_room = %s and ended_time is null
            """
    cursor.execute(query, (id_room,))
    results = cursor.fetchone()
    return results[0]


# Data setting for invoice
# Lấy tên sản phẩm và đơn giá
def nameServiceAndUnitPrice(id_booking_room):
    # Kết nối đến cơ sở dữ liệu
    conn = connection()
    cursor = conn.cursor()
    query = """
            SELECT service.name, service.unit_price
            FROM service
            JOIN service_detail ON service.id = service_detail.id_service
            JOIN karaoke.booking_room br ON br.id = service_detail.booking_room_id
            WHERE service_detail.booking_room_id = %s
        """

    booking_room_id = id_booking_room
    cursor.execute(query, (booking_room_id,))
    results = cursor.fetchall()
    return results


# Chuyển kết quả thành kiểu dữ liệu giống my_prod
def convertData(results):
    my_prod_query_result = {result[0]: result[1] for result in results}
    my_prod = {}
    counter = 1
    for key, value in my_prod_query_result.items():
        my_prod[counter] = [key, value]
        counter += 1

    return my_prod


# sales table keeps the product id and quantity sold
def quantityService(booking_room_id):
    conn = connection()
    cursor = conn.cursor()
    query = """
        SELECT
        ROW_NUMBER() OVER (ORDER BY karaoke.service_detail.id) AS keyIndex,
        service_detail.quantity
    FROM
        service
    JOIN
        service_detail ON service.id = service_detail.id_service
    JOIN
        karaoke.booking_room br ON br.id = service_detail.booking_room_id
    WHERE
        service_detail.booking_room_id = %s
    """

    cursor.execute(query, (booking_room_id,))
    results = cursor.fetchall()
    my_sale = dict(results)
    return my_sale


# discount_rate
def discount_rate(room_name):
    discount_rate = get_incentives_percent(room_name)
    return discount_rate


# Lấy tổng thời gian hát
def get_booking_duration(room_id):
    conn = connection()
    cursor = conn.cursor()
    query = """
                SELECT TIMEDIFF(b.created_date, br.created_date) AS duration
                FROM booking_room br
                join bill b on br.id = b.id_booking_room
                join room r on r.id = br.id_room
                where r.id = %s and ended_time is null
               """

    cursor.execute(query, (room_id,))
    result = cursor.fetchone()[0]  # Use fetchone instead of fetchall()[0]
    conn.close()

    return result


# Chuyển sang phút
def convert_minutes(delta_str):
    if isinstance(delta_str, timedelta):
        total_seconds = delta_str.total_seconds()
        minutes = total_seconds / 60
        return round(minutes)
    else:
        raise ValueError("Input must be a timedelta object")


# Tính tổng tiền
def totalPrice(selected_index):
    selected_room_id = total_for_frame_time_from_database(selected_index)
    return selected_room_id


# Tính tiền đơn giá phòng mỗi giờ
def priceForRoom(selected_index, room_id):
    total = totalPrice(selected_index)
    delta_str = get_booking_duration(room_id)
    result = convert_minutes(delta_str)
    if(result==0):
        result = 1
    unit_price = total / result
    unit_price = unit_price * 60
    return unit_price


# gộp dữ liệu



def printFuncInvoice(room_name):

    id_room_data = id_room(room_name)
    id_booking_room_data = id_booking_room(id_room_data)
    results = nameServiceAndUnitPrice(id_booking_room_data)

    my_prod = convertData(results)
    my_sale = quantityService(id_booking_room_data)
    discount_rate_data = discount_rate(room_name)

    time = get_booking_duration(id_room_data)
    priceForRoomdata = priceForRoom(room_name, id_room_data)
    priceForRoomdata = round(priceForRoomdata)
    price_room = {1: [room_name, priceForRoomdata]}
    sub = totalPrice(room_name)

    my_path = r'E:\python-tkinter-karaoke\bill\bill.pdf'
    c = canvas.Canvas(my_path, pagesize=letter)
    c = my_temp(c)  # run the template

    c.setFillColorRGB(0, 0, 1)  # font colour
    c.setFont("Arial", 20)
    row_gap = 0.6  # gap between each row
    line_y_0 = 7.9
    line_y = 7.3  # location of fist Y position
    total = sub
    for items in price_room:
        c.drawString(0.1 * inch, line_y_0 * inch, str(room_name))  # p Name
        c.drawRightString(4.5 * inch, line_y_0 * inch, str(priceForRoomdata))  # p Price
        c.drawRightString(5.7 * inch, line_y_0 * inch, str(time))  # p Qunt
        c.drawRightString(7 * inch, line_y_0 * inch, str(sub))  # Sub Total

    for items in my_sale:
        c.drawString(0.1 * inch, line_y * inch, str(my_prod[items][0]))  # p Name
        c.drawRightString(4.5 * inch, line_y * inch, str(my_prod[items][1]))  # p Price
        c.drawRightString(5.5 * inch, line_y * inch, str(my_sale[items]))  # p Qunt
        sub_total = my_prod[items][1] * my_sale[items]
        c.drawRightString(7 * inch, line_y * inch, str(sub_total))  # Sub Total
        total = round(total + sub_total, 1)
        line_y = line_y - row_gap
    c.drawRightString(7 * inch, 2.1 * inch, str(float(total)))  # Total
    discount = round((discount_rate_data / 100) * total, 1)
    c.drawRightString(4 * inch, 1.8 * inch, str(discount_rate_data) + '%')  # discount
    c.drawRightString(7 * inch, 1.8 * inch, '-' + str(discount))  # discount
    total_final = total - discount
    c.setFont("Times-Bold", 22)
    c.setFillColorRGB(1, 0, 0)  # font colour
    c.drawRightString(7 * inch, 0.8 * inch, str(total_final))
    c.showPage()
    c.save()

