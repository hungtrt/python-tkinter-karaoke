from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Đường dẫn đến file font trên hệ thống của bạn
font_path = 'E:/project-python/arial-unicode-ms .ttf'

# Đăng ký font
pdfmetrics.registerFont(TTFont('YourFontName', font_path))

def create_invoice(file_path, customer_name, items, total_amount):
    pdf = canvas.Canvas(file_path, pagesize=letter)

    # Sử dụng font đã đăng ký
    pdf.setFont("YourFontName", 12)

    # Tạo hóa đơn
    pdf.drawString(100, 750, f"Hóa đơn cho: {customer_name}")
    pdf.drawString(100, 730, "Sản phẩm/dịch vụ")

    y_position = 710
    for item in items:
        pdf.drawString(100, y_position, f"{item['name']}: {item['price']} VND")
        y_position -= 15

    pdf.drawString(100, y_position, "Tổng cộng: " + str(total_amount) + " VND")

    pdf.save()

# Sử dụng hàm để tạo hóa đơn
invoice_data = [
    {"name": "Dịch vụ 1", "price": 100},
    {"name": "Dịch vụ 2", "price": 150},
    # Thêm các sản phẩm/dịch vụ khác nếu cần
]
create_invoice("invoice.pdf", "Khách hàng ABC", invoice_data, 250)
