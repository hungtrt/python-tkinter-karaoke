from abc import ABC, abstractmethod
from tkinter import ttk

from IPython.terminal.pt_inputhooks import tk


class Person(ABC):
    __id = 0

    def __init__(self, id, name, phone, address):
        self.__id = id if id is not None else Person.count_id()
        self.__name = name
        self.__phone = phone
        self.__address = address

    @classmethod
    def count_id(cls):
        cls.__id += 1
        return cls.__id

    @classmethod
    def set_id(cls, value):
        cls.__id = value

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def phone(self):
        return self.__phone

    @property
    def address(self):
        return self.__address

    @name.setter
    def name(self, value):
        self.__name = value

    @phone.setter
    def phone(self, value):
        self.__phone = value

    @address.setter
    def address(self, value):
        self.__address = value

    @abstractmethod
    def get_salary(self):
        pass

    def get_position(self):
        pass

    def get_work_time(self):
        pass


class Manager(Person):
    def __init__(self, name, phone, address, position, salary, work_time, bonus, id):
        super().__init__(id, name, phone, address)
        self.__position = position
        self.__salary = salary
        self.__worktime = work_time
        self.__bonus = bonus

    def get_salary(self):
        return int(self.__salary) + int(self.__bonus)

    def get_position(self):
        return self.__position

    def get_work_time(self):
        return self.__worktime

    @property
    def position(self):
        return self.__position

    @property
    def salary(self):
        return self.__salary

    @property
    def worktime(self):
        return self.__worktime

    @property
    def bonus(self):
        return self.__bonus

    @position.setter
    def position(self, value):
        self.__position = value

    @salary.setter
    def salary(self, value):
        self.__salary = value

    @worktime.setter
    def worktime(self, value):
        self.__worktime = value

    @bonus.setter
    def bonus(self, value):
        self.__worktime = value


class Employee(Person):
    def __init__(self, name, phone, address, position, salary, work_time, id):
        super().__init__(id, name, phone, address)
        self.__position = position
        self.__salary = salary
        self.__worktime = work_time

    def get_salary(self):
        return self.__salary

    def get_position(self):
        return self.__position

    def get_work_time(self):
        return self.__worktime

    @property
    def position(self):
        return self.__position

    @property
    def salary(self):
        return self.__salary

    @property
    def worktime(self):
        return self.__worktime

    @position.setter
    def position(self, value):
        self.__position = value

    @salary.setter
    def salary(self, value):
        self.__salary = value

    @worktime.setter
    def worktime(self, value):
        self.__worktime = value
    # Hàm trang nhân sự


current_id = 0


# def personnel_page():
#     manager_frame = tk.Frame(main_frame)
#
#     head_frame = tk.Frame(manager_frame, bg='green')
#
#     heading_lb = tk.Label(manager_frame, text="Nhân Sự", font=('Bold', 22), bg='green')
#     heading_lb.pack(fill=tk.X, pady=1)
#
#     # Label và textfields
#     personnel_name_lb = tk.Label(head_frame, text='Tên: ', font=('Bold', 12))
#     personnel_name_lb.place(x=20, y=25, width=160, height=30)
#     personnel_name_text_field = tk.Entry(head_frame, font=('Bold', 12))
#     personnel_name_text_field.place(x=200, y=25, width=350, height=30)
#
#     personnel_phone_lb = tk.Label(head_frame, text='Số điện thoại: ', font=('Bold', 12))
#     personnel_phone_lb.place(x=20, y=75, width=160, height=30)
#     personnel_phone_text_field = tk.Entry(head_frame, font=('Bold', 12))
#     personnel_phone_text_field.place(x=200, y=75, width=350, height=30)
#
#     personnel_address_lb = tk.Label(head_frame, text='Địa chỉ: ', font=('Bold', 12))
#     personnel_address_lb.place(x=20, y=125, width=160, height=30)
#     personnel_address_text_field = tk.Entry(head_frame, font=('Bold', 12))
#     personnel_address_text_field.place(x=200, y=125, width=350, height=30)
#
#     position_lb = tk.Label(head_frame, text='Chức vụ: ', font=('Bold', 12))
#     position_lb.place(x=20, y=175, width=160, height=30)
#     selected_position = tk.StringVar()
#     combo_position = ttk.Combobox(head_frame, font=('Bold', 12), state="readonly", values=["Quản lý", "Nhân viên"],
#                                   textvariable=selected_position)
#     combo_position.place(x=200, y=175, width=350, height=30)
#
#     salary_lb = tk.Label(head_frame, text='Lương: ', font=('Bold', 12))
#     salary_lb.place(x=570, y=25, width=160, height=30)
#     salary_text_field = tk.Entry(head_frame, font=('Bold', 12))
#     salary_text_field.place(x=750, y=25, width=350, height=30)
#
#     work_time_lb = tk.Label(head_frame, text='Giờ làm: ', font=('Bold', 12))
#     work_time_lb.place(x=570, y=75, width=160, height=30)
#     work_time_text_field = tk.Entry(head_frame, font=('Bold', 12))
#     work_time_text_field.place(x=750, y=75, width=350, height=30)
#
#     bonus_lb = tk.Label(head_frame, text='Thưởng: ', font=('Bold', 12))
#     bonus_lb.place(x=570, y=125, width=160, height=30)
#     bonus_text_field = tk.Entry(head_frame, font=('Bold', 12))
#     bonus_text_field.place(x=750, y=125, width=350, height=30)
#
#     # Nút lưu thông tin
#     save_btn = tk.Button(head_frame, text='Lưu', font=('Bold', 12), bg='blue',
#                          command=lambda: addPersonnel(cus_table, personnel_name_text_field.get(),
#                                                       personnel_phone_text_field.get(),
#                                                       personnel_address_text_field.get(), selected_position.get(),
#                                                       salary_text_field.get(), work_time_text_field.get(),
#                                                       bonus_text_field.get()))
#     save_btn.place(x=570, y=170, width=80, height=40)
#     # Nút cập nhật thông tin
#     update_btn = tk.Button(head_frame, text='Cập nhật', font=('Bold', 12), bg='blue',
#                            command=lambda: updateDataInFile(cus_table, current_id, personnel_name_text_field.get(),
#                                                             personnel_phone_text_field.get(),
#                                                             personnel_address_text_field.get(), selected_position.get(),
#                                                             salary_text_field.get(), work_time_text_field.get(),
#                                                             bonus_text_field.get()))
#     update_btn.place(x=660, y=170, width=80, height=40)
#     # Nút xóa thông tin
#     delete_btn = tk.Button(head_frame, text='Xóa', font=('Bold', 12), bg='blue',
#                            command=lambda: deleteDataInFile(cus_table, current_id))
#     delete_btn.place(x=750, y=170, width=80, height=40)
#     # Nút clear thông tin
#     clear_btn = tk.Button(head_frame, text='Làm sạch', font=('Bold', 12), bg='blue', command=lambda: refreshInput())
#     clear_btn.place(x=840, y=170, width=80, height=40)
#     # Nút sắp xếp thông tin theo tên
#     clear_btn = tk.Button(head_frame, text='Sắp xếp', font=('Bold', 12), bg='blue',
#                           command=lambda: readFileAndDisplay(cus_table, True))
#     clear_btn.place(x=930, y=170, width=80, height=40)
#
#     head_frame.pack(pady=1)
#     head_frame.pack_propagate(False)
#     head_frame.configure(width=1038, height=225)
#
#     # Frame mới cho bảng nhân sự
#
#     table_cus_frame = tk.Frame(manager_frame, bg='green')
#
#     cus_table = ttk.Treeview(table_cus_frame)
#     cus_table.place(x=0, y=0, width=1000, height=320)
#
#     cus_table['column'] = ['ID', 'Name', 'Phone', 'Address', 'Position', 'Salary', 'Work Time']
#     cus_table.column('#0', anchor=tk.W, width=0, stretch=tk.NO)
#     cus_table.column('ID', anchor=tk.W, width=0)
#     cus_table.column('Name', anchor=tk.W, width=160)
#     cus_table.column('Phone', anchor=tk.W, width=80)
#     cus_table.column('Address', anchor=tk.W, width=200)
#     cus_table.column('Position', anchor=tk.W, width=60)
#     cus_table.column('Salary', anchor=tk.W, width=60)
#     cus_table.column('Work Time', anchor=tk.W, width=60)
#
#     heading_font = ("Arial", 11, "bold")
#     style = ttk.Style()
#     style.configure("Treeview.Heading", font=heading_font)
#     cus_table.heading('ID', text='ID', anchor=tk.W)
#     cus_table.heading('Name', text='Tên', anchor=tk.W)
#     cus_table.heading('Phone', text='Số Điện Thoại', anchor=tk.W)
#     cus_table.heading('Address', text='Địa Chỉ', anchor=tk.W)
#     cus_table.heading('Position', text='Chức vụ', anchor=tk.W)
#     cus_table.heading('Salary', text='Lương', anchor=tk.W)
#     cus_table.heading('Work Time', text='Ca làm việc', anchor=tk.W)
#     # đọc ra dữ liệu từ hàm readFileAndDisplay()
#     readFileAndDisplay(cus_table, False)
#     cus_table.bind('<ButtonRelease-1>', lambda event: handle_click())
#     table_cus_frame.pack(pady=5)
#     table_cus_frame.pack_propagate(False)
#     table_cus_frame.configure(width=1038, height=320, padx=20)
#
#     # kết thúc
#
#     def handle_click():
#         global current_id
#         item = cus_table.selection()[0]
#         data = cus_table.item(item, 'values')
#         current_id = data[0]
#         if data[4] == 'Quản lý':
#             combo_position.current(0)
#         else:
#             combo_position.current(1)
#         personnel_name_text_field.delete(0, tk.END)
#         personnel_name_text_field.insert(0, data[1])
#         personnel_address_text_field.delete(0, tk.END)
#         personnel_address_text_field.insert(0, data[3])
#         personnel_phone_text_field.delete(0, tk.END)
#         personnel_phone_text_field.insert(0, data[2])
#         salary_text_field.delete(0, tk.END)
#         salary_text_field.insert(0, int(data[5]) - int(data[7]))
#         work_time_text_field.delete(0, tk.END)
#         work_time_text_field.insert(0, data[6])
#         bonus_text_field.delete(0, tk.END)
#         bonus_text_field.insert(0, data[7])
#
#     def refreshInput():
#         personnel_name_text_field.delete(0, tk.END)
#         personnel_address_text_field.delete(0, tk.END)
#         personnel_phone_text_field.delete(0, tk.END)
#         salary_text_field.delete(0, tk.END)
#         work_time_text_field.delete(0, tk.END)
#         bonus_text_field.delete(0, tk.END)
#
#     manager_frame.pack(pady=10)


# Thêm dữ liệu vào file
def addPersonnel(cus_table, name, phone, address, position, salary, work_time, bonus):
    f = open('E:\python-tkinter-karaoke\Data\personnel.txt', 'a', encoding='utf-8')
    if position == 'Quản lý':
        manager = Manager(id=None, name=name, phone=phone, address=address, position=position, salary=salary,
                          work_time=work_time, bonus=bonus)
        f.write(f'{manager.id},{name},{phone},{address},{position},{manager.get_salary()},{work_time}, {bonus}\n')
        cus_table.insert(parent='', index='end', iid=manager.id, text="",
                         values=(manager.id, name, phone, address, position, manager.get_salary(), work_time),
                         tag="orow")
    else:
        employee = Employee(id=None, name=name, phone=phone, address=address, position=position, salary=salary,
                            work_time=work_time)
        f.write(f'{employee.id},{name},{phone},{address},{position},{employee.get_salary()},{work_time},0\n')
        cus_table.insert(parent='', index='end', iid=employee.id, text="",
                         values=(employee.id, name, phone, address, position, employee.get_salary(), work_time),
                         tag="orow")

    f.close()


# Đọc dữ liệu file
def readFileAndDisplay(my_tree, sort):
    for data in my_tree.get_children():
        my_tree.delete(data)

    with open('E:\python-tkinter-karaoke\Data\personnel.txt', 'r', encoding='utf-8') as f:
        new_data = f.readlines()
    data_array = []
    for array in new_data:
        values = array.strip().split(',')
        data_array.append(values)
    if sort == True:
        data_array.sort(key=lambda x: x[1], reverse=True)

    current_id = 0
    for values in data_array:
        item_id = values[0]
        if int(values[0]) > (int(current_id)):
            current_id = values[0]
        my_tree.insert(parent='', index='end', iid=item_id, text="",
                       values=(values[0], values[1], values[2], values[3], values[4],values[5], values[6],values[7]),
                       tag="orow")

    my_tree.tag_configure('orow', background='#EEEEEE', font=('Arial', 12))
    Person.set_id(int(current_id))


def updateDataInFile(my_tree, id, name, phone, address, position, salary, work_time, bonus):
    f = open('E:\python-tkinter-karaoke\Data\personnel.txt', 'r+', encoding='utf-8')
    current_data = f.readlines()
    for i in range(len(current_data)):
        values = current_data[i].strip().split(',')
        if values[0] == id:
            if position == 'Quản lý':
                manager = Manager(name, phone, address, position, salary, work_time, bonus, id)
                current_data[
                    i] = f'{id},{name},{phone},{address},{position},{manager.get_salary()},{work_time}, {bonus}\n'
            else:
                employee = Employee(name, phone, address, position, salary, work_time, id)
                current_data[i] = f'{id},{name},{phone},{address},{position},{employee.get_salary()},{work_time},0\n'
            break
    f.seek(0)
    f.write('')
    f.writelines(current_data)
    f.close()
    readFileAndDisplay(my_tree, False)


def deleteDataInFile(my_tree, id):
    f = open('E:\python-tkinter-karaoke\Data\personnel.txt', 'r+', encoding='utf-8')
    current_data = f.readlines()
    f.seek(0)
    f.truncate()
    for i in range(len(current_data)):
        values = current_data[i].strip().split(',')
        if values[0] == id:
            current_data.pop(i)
            continue
        f.write(current_data[i])
    f.close()
    readFileAndDisplay(my_tree, False)


# nút page nhân sự
# customer_btn = tk.Button(options_frame, text='Nhân Sự', font=('Bold', 15), fg='#158aff', bd=0, bg='#FFFDFF',
#                          command=lambda: indicate(customer_indicate, personnel_page))
# customer_btn.place(x=10, y=270)
# customer_indicate = tk.Label(options_frame, text='', bg='#20C563')
# customer_indicate.place(x=3, y=270, width=5, height=40)