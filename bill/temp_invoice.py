from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def my_temp(c):
    c.translate(inch, inch)
    # define a large fonT
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    registered_fonts = pdfmetrics.getRegisteredFontNames()

    c.setFont("Arial", 14)
    # choose some colors
    c.setStrokeColorRGB(0.1, 0.8, 0.1)
    c.setFillColorRGB(0, 0, 1)  # font colour
    c.drawImage('E:\\python-tkinter-karaoke\\Data\\download.png', -1 * inch, 9.2 * inch, width=90,
                height=55)
    c.drawString(0, 9.1 * inch, "Thiên Thai KARAOKE")
    c.drawString(0, 8.8 * inch, "470 Trần Đại Nghĩa, Đà Nẵng")
    c.setFillColorRGB(0, 0, 0)  # font colour
    c.line(0, 8.65 * inch, 6.8 * inch, 8.65 * inch)
    from datetime import date
    dt = date.today().strftime('%d-%b-%Y')
    c.drawString(5.7 * inch, 9.3 * inch, dt)
    c.setFont("Arial", 8)
    c.setFillColorRGB(1, 0, 0)  # font colour
    c.setFont("Arial", 40)
    c.drawString(4.3 * inch, 8.8 * inch, 'HÓA ĐƠN')
    c.rotate(45)  # rotate by 45 degree
    c.setFillColorCMYK(0, 0, 0, 0.08)  # font colour CYAN, MAGENTA, YELLOW and BLACK
    c.setFont("Arial", 120)  # font style and size
    c.drawString(2 * inch, 1 * inch, "KARAOKE")  # String written
    c.rotate(-45)  # restore the rotation
    c.setFillColorRGB(0, 0, 0)  # font colour
    c.setFont("Arial", 18)
    c.drawString(0.4 * inch, 8.3 * inch, 'Dịch Vụ')
    c.drawString(3.5 * inch, 8.3 * inch, 'Đơn Giá')
    c.drawString(4.7 * inch, 8.3 * inch, 'Số Lượng')
    c.drawString(6.1 * inch, 8.3 * inch, 'Thành Tiền')
    c.setStrokeColorCMYK(0, 0, 0, 1)  # vertical line colour
    c.line(3.4 * inch, 8.3 * inch, 3.4 * inch, 2.7 * inch)  # first vertical line
    c.line(4.7 * inch, 8.3 * inch, 4.7 * inch, 2.7 * inch)  # second vertical line
    c.line(5.85 * inch, 8.3 * inch, 5.85 * inch, 2.7 * inch)  # third vertical line
    c.line(0.01 * inch, 2.5 * inch, 7 * inch, 2.5 * inch)  # horizontal line total

    c.drawString(1 * inch, 1.8 * inch, 'Ưu Đãi')
    c.drawString(2 * inch, 0.8 * inch, 'Tổng Cộng')
    c.setFont("Arial", 22)
    c.setStrokeColorRGB(0.1, 0.8, 0.1)  # Bottom Line colour
    c.line(0, -0.7 * inch, 6.8 * inch, -0.7 * inch)
    c.setFont("Arial", 8)  # font size
    c.setFillColorRGB(1, 0, 0)  # font colour
    return c

