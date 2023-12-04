import tkinter as tk

def clear_textfields(customer_name_text_field, customer_phone_text_field, customer_address_text_field, amount_consumed_text_field,id_lb):
    customer_name_text_field.delete(0, tk.END)
    customer_phone_text_field.delete(0, tk.END)
    customer_address_text_field.delete(0, tk.END)
    amount_consumed_text_field.delete(0, tk.END)
    id_lb.config(text="")

def clear_textfields_update(customer_name_text_field, customer_phone_text_field, customer_address_text_field, id_lb):
    customer_name_text_field.delete(0, tk.END)
    customer_phone_text_field.delete(0, tk.END)
    customer_address_text_field.delete(0, tk.END)
    id_lb.config(text="")
def clear_cobobox(combobox_cus, combobox_room):
    combobox_cus.set("")
    combobox_room.set("")

def clear_cobobox_and_textfield(combobox_1, combobox_2, quantity_text_field,ser_table):
    combobox_1.set("")
    combobox_2.set("")
    # Xóa dữ liệu cũ trên Treeview
    ser_table.delete(*ser_table.get_children())
    quantity_text_field.delete(0, tk.END)

def clear_checkout_room(room_combobox,
                        room_checkout_result_label, money_service_label, incentives_percent_label,
                        total_label, incentives_label, final_label):
    room_combobox.set("")
    room_checkout_result_label.config(text="")
    money_service_label.config(text="")
    incentives_percent_label.config(text="")
    total_label.config(text="")
    incentives_label.config(text="")
    final_label.config(text="")

def clearNameServiceAndQuantity(combobox_nameService,quantity_text_field):
    combobox_nameService.set("")
    quantity_text_field.delete(0, tk.END)
