import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from connectionDB import connection
def getCustomerByPhone(phone):
    conn = connection()
    cursor = conn.cursor()
    query = "SELECT name_id, name, phone, address, type FROM customer where phone = %s"
    cursor.execute(query, (phone,))
    results = cursor.fetchall()
    conn.close()
    return results

def generate_card(data):
    font = ImageFont.truetype("E:\\python-tkinter-karaoke\\card\\OpenSans-Semibold.ttf", size=25)
    font1 = ImageFont.truetype("E:\\python-tkinter-karaoke\\card\\OpenSans-Semibold.ttf", 33)
    template = Image.open("E:\\python-tkinter-karaoke\\card\\template.png")
    pic = Image.open(f"E:/python-tkinter-karaoke/card/QR Photos/{data['name_id']}.png")
    new_size = (290, 290)  # Kích thước mới, bạn có thể điều chỉnh theo ý muốn
    pic_resized = pic.resize(new_size, Image.LANCZOS)
    template.paste(pic_resized, (8, 145, 8 + new_size[0], 145 + new_size[1]))

    draw = ImageDraw.Draw(template)
    draw.text((455, 250), str(data['name_id']), font=font1, fill='#E64652')
    draw.text((595, 308), data['name'], font=font, fill='black')
    draw.text((595, 354), data['phone'], font=font, fill='black')
    draw.text((595, 400), data['address'], font=font, fill='black')
    draw.text((840, 20), data['type'], font=font, fill='white')
    return template


def printCardMembership(phone):
    header = ['name_id', 'name', 'phone', 'address', 'type']
    data = getCustomerByPhone(phone)
    results = [dict(zip(header, data[0]))]

    for result in results:
        card = generate_card(result)
        card.save(f"E:/python-tkinter-karaoke/card/cards/{result['name_id']}.png")
