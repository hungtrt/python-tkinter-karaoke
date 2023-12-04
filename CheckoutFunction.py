import mysql.connector

def get_incentives_percent(selected_index):
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

        cursor.execute("SELECT id_customer FROM booking_room WHERE id_room = %s and booking_room.ended_time is null",
                       (selected_room_id,))
        selected_customer_id = cursor.fetchone()[0]

        cursor.execute("SELECT customer_incentives FROM customer WHERE id = %s", (selected_customer_id,))
        selected_customer_incentives = cursor.fetchone()[0]

        return selected_customer_incentives

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Đóng kết nối
        connection.close()