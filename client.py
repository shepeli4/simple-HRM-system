import json
import socket
import tkinter as tk
import customtkinter as ctk
from tkinter import scrolledtext, filedialog, messagebox
from os import getcwd, listdir, path, remove, startfile
from PIL import Image, ImageTk
import platform


def close_app():
    global sock
    sock.send('EXIT;;'.encode('utf-8') + bytearray(512 - len('EXIT;;'.encode('utf-8'))))
    folder_path = getcwd() + '\\imgs'
    for item in listdir(folder_path):
        item_path = path.join(folder_path, item)
        remove(item_path)
    root.destroy()


def get_file():
    global sock
    f_name, f_size, buff = sock.recv(512).decode('utf-8').split(';')
    f_size = int(f_size)
    with open(f'{getcwd()}\\imgs\\{f_name}', 'wb') as f:
        for i in range(f_size // 4096):
            chunk = sock.recv(4096)
            f.write(chunk)
        chunk = sock.recv(f_size - f_size // 4096 * 4096)
        f.write(chunk)


def send_file(file_path):
    global sock

    f_name = file_path[file_path.rfind('\\'):]
    file_size = path.getsize(file_path)
    print(f_name)
    # file_name;file_size(bytes);\x00\x00\x00\x00...
    sock.send(f'{f_name};{file_size};'.encode('utf-8') + bytearray(512 - len(f'{f_name};{file_size};'.encode('utf-8'))))
    with open(file_path, 'rb') as f:
        chunk = f.read(4096)
        while chunk:
            sock.send(chunk)
            chunk = f.read(4096)
    print('img_sent')


def get_profile():
    global sock
    print('get_profile')
    # "login": <login>, "password": <password>, etc.
    worker = sock.recv(1024).decode('utf-8')
    worker = json.loads(worker[:worker.rfind(';')])
    print(worker)
    if worker['profile_photo']:
        get_file()
    for i in worker['certificates']:
        get_file()

    build_worker_ui(worker)


def change_description(worker_login, worker_name, new_desc):
    message = f'CHANGE_DESC;{new_desc}:{worker_name};{worker_login};'
    sock.send(message.encode('utf-8') + bytearray(512 - len(message.encode('utf-8'))))


def change_profile_pic(worker_login, worker_name):
    global sock
    file_path = filedialog.askopenfilename(filetypes=(("Jpg Files", "*.jpg"),
                                                      ("Png Files", "*.png"),
                                                      ('Jpeg Files', '*.jpeg'),
                                                      ("All Files", "*.*")))
    f_name = file_path[file_path.rfind('\\'):]
    message = f'CHANGE_PROFILE_PIC;{f_name}:{worker_login};{worker_name};'
    sock.send(message.encode('utf-8') + bytearray(512 - len(message.encode('utf-8'))))
    send_file(file_path)
    # ПРОВЕРИТЬ РАБОТОСПОСОБНОСТЬ ПУТЁМ ДОБАВЛЕНИЯ КНОПКИ


def build_worker_ui(worker):
    for widget in root.winfo_children():
        widget.destroy()

    root.grid_columnconfigure((0, 1, 2), weight=1)
    root.grid_rowconfigure(0, weight=1)

    frame1 = ctk.CTkFrame(root, corner_radius=15)
    frame2 = ctk.CTkFrame(root, corner_radius=15)
    frame3 = ctk.CTkScrollableFrame(root, label_text='Бумаги', corner_radius=15)

    frame1.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
    frame2.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
    frame3.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)

    img_path = f'imgs/{worker["profile_photo"]}' if worker['profile_photo'] else 'default_profile_pic.jpg'
    pil_image = Image.open(img_path)
    ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(300, 400))

    image_label = ctk.CTkLabel(frame1, image=ctk_image, text="")
    image_label.pack(pady=20, expand=True)

    ctk.CTkLabel(frame1, text=worker['name'], font=('Helvetica', 16, 'bold')).pack(pady=2)
    ctk.CTkLabel(frame1, text=worker['login'] if worker['login'] else '', font=('Helvetica', 12)).pack(pady=2)
    ctk.CTkLabel(frame1, text=worker['post'], font=('Helvetica', 12)).pack(pady=(2, 20))

    desc = ctk.CTkTextbox(frame2, corner_radius=10)
    desc.pack(padx=15, pady=15, fill='both', expand=True)
    desc.insert("0.0", worker['description'])

    btn = ctk.CTkButton(
        frame2,
        text='Изменить описание',
        font=('Helvetica', 14),
        command=lambda: change_description(worker['login'], worker['name'], desc.get("0.0", "end"))
    )
    btn.pack(pady=15, padx=15, fill='x')

    for i in worker['certificates']:
        ctk.CTkButton(
            frame3,
            text=f'{i}',
            height=45,
            fg_color="transparent",
            border_width=1,
            command=lambda a=i: startfile(f'{getcwd()}\\imgs\\{a}')
        ).pack(pady=5, padx=10, fill='x')


def login_action(register=False):
    global sock
    name = login_name.get()
    password = login_pass.get()

    if not name or not password and ';' not in name and ';' not in password and ':' not in name and ':' not in password:
        messagebox.showerror('FAIL', 'Enter correct name and password')
        return

    mode = 'registration' if register else 'login'
    data = f'{name}:{password};{mode}'
    sock.send(data.encode('utf-8'))
    data = sock.recv(1024).decode('utf-8')

    if 'SUCCESS' == data[:data.find(';')]:
        login_frame.pack_forget()
        print(data[data.find(';') + 1:])

        if data[data.find(';') + 1:] == 'HR':
            pass
        elif data[data.find(';') + 1:] == 'worker':
            get_profile()
        else:
            messagebox.showinfo('SUCCESS', 'Please, go to your HR and ask him for registrate you\n:)')
            root.destroy()
    else:
        messagebox.showerror('FAIL', data[data.find(';') + 1:])

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.1.188', 1800))  # --- CHANGE IP ON PUBLIC ---

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title('ne')
    root.geometry('1200x600')
    root.minsize(900, 500)

    login_frame = ctk.CTkFrame(root, corner_radius=20)
    login_frame.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(login_frame, text='Username:', font=('Helvetica', 12)).pack(pady=(20, 5))
    login_name = ctk.CTkEntry(login_frame, width=250)
    login_name.pack(pady=5, padx=40)

    ctk.CTkLabel(login_frame, text='Password:', font=('Helvetica', 12)).pack(pady=5)
    login_pass = ctk.CTkEntry(login_frame, show='•', width=250)
    login_pass.pack(pady=5)

    ctk.CTkButton(login_frame, text='Log in', width=200, command=lambda: login_action()).pack(pady=20)
    ctk.CTkButton(login_frame, text='Register', width=200, fg_color="transparent", border_width=1,
                  command=lambda: login_action(True)).pack(pady=(0, 20))

    root.protocol("WM_DELETE_WINDOW", close_app)
    root.resizable(False, False)
    root.mainloop()