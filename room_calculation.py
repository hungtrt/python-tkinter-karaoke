from datetime import datetime, timedelta
import mysql.connector

def connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="170801",
        database="karaoke"
    )
    return conn
def total_for_frame_time_from_database(room_name):
    conn = connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM room WHERE name = %s", (room_name,))
    id_room = cursor.fetchone()
    id_room_result = id_room[0]

    cursor.execute("SELECT created_date FROM booking_room WHERE id_room = %s and ended_time is null", (id_room_result,))
    result_create_date = cursor.fetchone()

    cursor.execute("SELECT id FROM booking_room WHERE id_room = %s and ended_time is null", (id_room_result,))
    id_booking_room = cursor.fetchone()[0]

    cursor = conn.cursor()
    cursor.execute("SELECT ended_time FROM booking_room WHERE id_room = %s and id = %s", (id_room_result,id_booking_room))
    result_ended_time = cursor.fetchone()

    if result_ended_time[0] is not None:
        formatted_created_date = result_create_date[0].strftime("%Y-%m-%d %H:%M:%S")
        ended_time_format = result_ended_time[0].strftime("%Y-%m-%d %H:%M:%S")
    else:
        formatted_created_date = result_create_date[0].strftime("%Y-%m-%d %H:%M:%S")
        ended_time_format = datetime.now()
        ended_time_format = ended_time_format.strftime("%Y-%m-%d %H:%M:%S")

    result = total_for_frame_time(formatted_created_date, ended_time_format, room_name)
    return result
def total_for_frame_time(timestamp1, timestamp2, room_name):
    time_format = "%Y-%m-%d %H:%M:%S"
    start_time = datetime.strptime(timestamp1, time_format)
    end_time = datetime.strptime(timestamp2, time_format)

    total_time_khung1 = timedelta()
    total_time_khung2 = timedelta()
    total_time_khung3 = timedelta()

    start_khung1 = datetime.strptime("06:00:00", "%H:%M:%S").time()
    end_khung1 = datetime.strptime("16:59:59", "%H:%M:%S").time()
    start_khung2 = datetime.strptime("17:00:00", "%H:%M:%S").time()
    end_khung2 = datetime.strptime("21:59:59", "%H:%M:%S").time()
    start_khung3_1 = datetime.strptime("22:00:00", "%H:%M:%S").time()
    end_khung3_1 = datetime.strptime("23:59:59", "%H:%M:%S").time()
    start_khung3_2 = datetime.strptime("00:00:00", "%H:%M:%S").time()
    end_khung3_2 = datetime.strptime("05:59:59", "%H:%M:%S").time()

    while start_time < end_time:
        current_time = start_time.time()
        if start_khung1 <= current_time <= end_khung1:
            total_time_khung1 += timedelta(minutes=1)
        elif start_khung2 <= current_time <= end_khung2:
            total_time_khung2 += timedelta(minutes=1)
        elif (start_khung3_1 <= current_time <= end_khung3_1) or (start_khung3_2 <= current_time <= end_khung3_2):
            total_time_khung3 += timedelta(minutes=1)

        start_time += timedelta(minutes=1)

    time_frame_1 = total_time_khung1.seconds // 60
    time_frame_2 = total_time_khung2.seconds // 60
    time_frame_3 = total_time_khung3.seconds // 60

    price_frame_1 = 0
    price_frame_2 = 0
    price_frame_3 = 0

    conn = connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM room WHERE name = %s", (room_name,))
    selected_room_id = cursor.fetchone()[0]

    if (time_frame_1 != 0):
        cursor.execute("SELECT unit_price FROM room_rates WHERE id_room = %s and time_slot=1",
                       (selected_room_id,))
        unit_price = cursor.fetchone()[0]
        unit_price = unit_price / 60

        price_frame_1 = time_frame_1 * unit_price
        price_frame_1 = round(price_frame_1)

    if (time_frame_2 != 0):
        cursor.execute("SELECT unit_price FROM room_rates WHERE id_room = %s and time_slot=2",
                       (selected_room_id,))
        unit_price = cursor.fetchone()[0]
        unit_price = unit_price / 60

        price_frame_2 = time_frame_2 * unit_price
        price_frame_2 = round(price_frame_2)

    if (time_frame_3 != 0):
        cursor.execute("SELECT unit_price FROM room_rates WHERE id_room = %s and time_slot=3",
                       (selected_room_id,))
        unit_price = cursor.fetchone()[0]
        unit_price = unit_price / 60

        price_frame_3 = time_frame_3 * unit_price
        price_frame_3 = round(price_frame_3)

    total_price = price_frame_1 + price_frame_2 + price_frame_3
    return total_price


