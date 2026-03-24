import json
import os
import socket
import customtkinter as ctk
from tkinter import filedialog, messagebox
from os import getcwd, listdir, path, remove, startfile, makedirs
from PIL import Image, ImageTk
import shutil


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

    f_name = file_path[file_path.rfind('/'):]
    file_size = path.getsize(file_path)
    print(f_name, file_path)
    # file_name;file_size(bytes);\x00\x00\x00\x00...
    sock.send(f'{f_name};{file_size};'.encode('utf-8') + bytearray(512 - len(f'{f_name};{file_size};'.encode('utf-8'))))
    with open(file_path, 'rb') as f:
        chunk = f.read(4096)
        while chunk:
            sock.send(chunk)
            chunk = f.read(4096)
    print('img_sent')


def get_profile():
    global sock, worker
    print('get_profile')
    # "login": <login>, "password": <password>, etc.
    worker = sock.recv(1024).decode('utf-8')
    worker = json.loads(worker[:worker.rfind(';')])
    print(worker)
    if worker['profile_photo']:
        get_file()
    for i in worker['certificates']:
        get_file()

    build_worker_ui()
    print('building')


def change_description(worker_login, worker_name, new_desc):
    message = f'CHANGE_DESC;{new_desc}:{worker_name};{worker_login};'
    sock.send(message.encode('utf-8') + bytearray(512 - len(message.encode('utf-8'))))


def change_profile_pic(label_widget):
    global sock, worker
    file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
    if file_path:
        ext = path.splitext(file_path)[1]
        new_name = f"pfp_{worker['login']}{ext}"
        dest = path.join(getcwd(), 'imgs', new_name)
        if not path.exists('imgs'): makedirs('imgs')
        shutil.copy(file_path, dest)
        new_img = Image.open(dest)
        ctk_img = ctk.CTkImage(light_image=new_img, dark_image=new_img, size=(300, 400))
        label_widget.configure(image=ctk_img)
        worker['profile_photo'] = new_name
        message = f'CHANGE_PROFILE_PIC;{file_path}:{worker["login"]};{worker["name"]};'
        sock.send(message.encode('utf-8') + bytearray(512 - len(message.encode('utf-8'))))
        send_file(file_path)


def add_certificate(frame):
    global sock, worker
    file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
    if file_path:
        message = f'ADD_CERTIFICATE;{file_path}:{worker["login"]};{worker["name"]};'
        sock.send(message.encode('utf-8') + bytearray(512 - len(message.encode('utf-8'))))
        data = sock.recv(512).decode('utf-8')
        worker = json.loads(data[:data.rfind(';')])
        ctk.CTkButton(frame, text=str(worker['certificates'][-1]), height=45, fg_color="transparent", border_width=1,
                      command=lambda a=worker['certificates'][-1]: startfile(path.join(getcwd(), 'imgs', a))).pack(pady=5, padx=10, fill='x')
        dest = path.join(getcwd(), 'imgs', worker['certificates'][-1])
        shutil.copy(file_path, dest)
        send_file(file_path)


def delete_certificate(frame3):
    global sock, worker
    def on_press():
        global worker
        nonlocal file, frame3
        print(file)
        if not file: messagebox.showerror('ERROR', 'Выберите сертификат для удаления')
        message = f'DELETE_CERTIFICATE;{file}:{worker["login"]};{worker["name"]};'.encode('utf-8')
        sock.send(message + bytearray(512 - len(message)))
        del worker['certificates'][worker['certificates'].index(file)]
        mini_root.destroy()
        for i in frame3.winfo_children():
            i.destroy()
        ctk.CTkButton(frame3, text='+ Добавить бумагу', font=('Helvetica', 12, 'bold'), fg_color="#2b719e",
                      command=lambda: add_certificate(frame3)).pack(pady=10, padx=10, fill='x')
        ctk.CTkButton(frame3, text='- Удалить бумагу', font=('Helvetica', 12, 'bold'), fg_color="#2b719e",
                      command=lambda: delete_certificate(frame3)).pack(pady=10, padx=10, fill='x')
        for i in worker['certificates']:
            ctk.CTkButton(frame3, text=str(i), height=45, fg_color="transparent", border_width=1,
                          command=lambda a=i: startfile(path.join(getcwd(), 'imgs', a))).pack(pady=5, padx=10, fill='x')

    mini_root = ctk.CTkToplevel()
    mini_root.title("Certificates")
    mini_root.geometry("800x400")
    mini_root.resizable(False, False)
    mini_root.attributes("-topmost", True)

    file = ''

    def show_preview(file_path):
        nonlocal file
        file = file_path
        try:
            full_path = path.join(getcwd(), 'imgs', file_path)
            img = Image.open(full_path)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(350, 350))
            preview_label.configure(image=ctk_img, text="")
        except Exception:
            preview_label.configure(image=None, text="Preview error")

    left_frame = ctk.CTkFrame(mini_root, width=400, fg_color="transparent")
    left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    right_frame = ctk.CTkFrame(mini_root, width=380)
    right_frame.pack(side="right", fill="both", padx=5, pady=5)
    preview_label = ctk.CTkLabel(right_frame, text="Select a file", width=350, height=350)
    preview_label.pack(expand=True)

    scrollable_frame = ctk.CTkScrollableFrame(left_frame)
    scrollable_frame.pack(fill="both", expand=True)

    for certificate_path in worker['certificates']:
        file_name = path.basename(certificate_path)
        btn = ctk.CTkButton(
            scrollable_frame,
            text=file_name,
            height=45,
            fg_color="transparent",
            border_width=1,
            command=lambda f=file_name: show_preview(f)
        )
        btn2 = ctk.CTkButton(right_frame, text='Удалить выбранную бумагу', font=('Helvetica', 12, 'bold'),
                             fg_color="#2b719e", command=lambda: on_press())
        btn2.pack(pady=6, padx=10, fill='x')
        btn.pack(pady=5, padx=10, fill='x')


def build_worker_ui():
    global sock, worker
    # for widget in root.winfo_children():
        # widget.destroy()

    root.grid_columnconfigure((0, 1, 2), weight=1)
    root.grid_rowconfigure(0, weight=1)

    frame1 = ctk.CTkFrame(root, corner_radius=15)
    frame2 = ctk.CTkFrame(root, corner_radius=15)
    frame3 = ctk.CTkScrollableFrame(root, label_text='Бумаги', corner_radius=15)

    frame1.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
    frame2.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
    frame3.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)

    img_path = f'imgs/{worker["profile_photo"]}' if worker['profile_photo'] and path.exists(
        f'imgs/{worker["profile_photo"]}') else os.getcwd() + '\\default_profile_pic.jpg'
    if img_path:
        pil_image = Image.open(img_path)
    else:
        pil_image = Image.new('RGB', (300, 400), color='gray')

    ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(300, 400))
    image_label = ctk.CTkLabel(frame1, image=ctk_image, text="")
    image_label.pack(pady=(20, 10), expand=True)

    ctk.CTkLabel(frame1, text=worker['name'], font=('Helvetica', 16, 'bold')).pack(pady=2)
    ctk.CTkLabel(frame1, text=worker['login'] or '', font=('Helvetica', 12)).pack(pady=2)
    ctk.CTkLabel(frame1, text=worker['post'], font=('Helvetica', 12)).pack(pady=(2, 20))

    desc = ctk.CTkTextbox(frame2, corner_radius=10)
    desc.pack(padx=15, pady=15, fill='both', expand=True)
    desc.insert("0.0", worker['description'])

    ctk.CTkButton(frame2, text='Изменить описание', font=('Helvetica', 14),
                  command=lambda: change_description(worker['login'], worker['name'], desc.get("0.0", "end"))).pack(
        pady=15, padx=15, fill='x')

    ctk.CTkButton(frame1, text='Изменить фото профиля', font=('Helvetica', 14),
                  command=lambda: change_profile_pic(image_label)).pack(pady=(0, 13), padx=20, fill='x')

    ctk.CTkButton(frame3, text='+ Добавить бумагу', font=('Helvetica', 12, 'bold'), fg_color="#2b719e",
                  command=lambda: add_certificate(frame3)).pack(pady=10, padx=10, fill='x')
    ctk.CTkButton(frame3, text='- Удалить бумагу', font=('Helvetica', 12, 'bold'), fg_color="#2b719e",
                  command=lambda: delete_certificate(frame3)).pack(pady=10, padx=10, fill='x')

    for i in worker['certificates']:
        ctk.CTkButton(frame3, text=str(i), height=45, fg_color="transparent", border_width=1,
                      command=lambda a=i: startfile(path.join(getcwd(), 'imgs', a))).pack(pady=5, padx=10, fill='x')


def hr_window():
    global sock

    def get_profile_in_func():
        nonlocal workers, left_combobox
        global worker

        for i in range(len(workers)):
            print(workers[i]['login'], left_combobox.get())
            if workers[i]['login'] == left_combobox.get():
                worker = workers[i]
                login_frame.pack_forget()
                data = f'GET_PROFILE;{worker["login"]};{worker["name"]};'.encode('utf-8')
                sock.send(data + bytearray(512 - len(data)))
                get_profile()
                break
        else:
            messagebox.showerror('ERROR', 'Такого пользователя не существет.')

    def delete_profile():
        nonlocal workers, left_combobox
        global worker
        if worker['login'] == left_combobox.get():
            messagebox.showerror('ERROR', 'Вы не можете удалить уже открытый профиль.')
            return
        if messagebox.askokcancel('Are u sure?', f'Вы уверены что хотите удалить пользователя {left_combobox.get()}'):
            for i in range(len(workers)):
                if workers[i]['login'] == left_combobox.get():
                    data = f'DELETE_PROFILE;{workers[i]["login"]};{workers[i]["name"]};'.encode('utf-8')
                    sock.send(data + bytearray(512 - len(data)))
                    del workers[i]
                    left_combobox.configure(values=[i['login'] for i in workers])
                    left_combobox.set(workers[0]['login'])
                    break

    def add_account():
        nonlocal workers, right_combobox, workers_without_login, name_entry, post_entry
        global worker
        if not name_entry.get() or not post_entry.get():
            messagebox.showerror('FAIL', 'поля с именем и должностью не должны бать пусты')
            return
        for i in workers_without_login:
            if i == right_combobox.get():
                data = f'ADD_ACCOUNT;{right_combobox.get()}:{name_entry.get()}:{post_entry.get()};'.encode('utf-8')
                sock.send(data + bytearray(512 - len(data)))
                workers.append(
                    {'login': i, 'password': workers_without_login[i], 'post': post_entry.get(),
                     'profile_photo': '', 'certificates': [], 'name': name_entry.get(), 'description': ''})
                del workers_without_login[i]
                print(workers, workers_without_login, sep='\n')
                right_combobox.configure(values=workers_without_login.keys())
                right_combobox.set('')
                left_combobox.configure(values=[j['login'] for j in workers])
                left_combobox.set(workers[0]['login'])
                break
        else:
            messagebox.showerror('ERROR', 'Такого аккаунта не существует.')

    def add_hr():
        nonlocal workers, left_combobox
        if messagebox.askokcancel('Are u sure?', f'Вы уверены что хотите повысить пользователя {left_combobox.get()} до HR?'):
            for i in workers:
                if i['login'] == left_combobox.get():
                    data = f'ADD_HR;{i["login"]};{i["name"]};'.encode('utf-8')
                    sock.send(data + bytearray(512 - len(data)))
                    data = sock.recv(256).decode('utf-8')
                    data = data[:data.rfind(';')]
                    if data != 'SUCCESS':
                        messagebox.showerror('FAIL', data[data.find(';') + 1:])
                    break
            else:
                messagebox.showerror('FAIL', 'Такого аккаунта не существует')

    def delete_hr():
        nonlocal workers, left_combobox
        if messagebox.askokcancel('Are u sure?', f'Вы уверены что хотите снять пользователя {left_combobox.get()} с должности HR?'):
            for i in workers:
                if i['login'] == left_combobox.get():
                    data = f'DELETE_HR;{i["login"]};{i["name"]};'.encode('utf-8')
                    sock.send(data + bytearray(512 - len(data)))
                    data = sock.recv(256).decode('utf-8')
                    data = data[:data.rfind(';')]
                    if data != 'SUCCESS':
                        messagebox.showerror('FAIL', data[data.find(';') + 1:])
                    break
            else:
                messagebox.showerror('FAIL', 'Такого аккаунта не существует')


    workers = sock.recv(2048).decode('utf-8')
    workers = json.loads(workers[:workers.rfind(';')])

    workers_without_login = sock.recv(1024).decode('utf-8')
    workers_without_login = json.loads(workers_without_login[:workers_without_login.rfind(';')])
    print(workers_without_login)

    hr_root = ctk.CTkToplevel()
    hr_root.title("hr_window")
    hr_root.geometry("600x400")
    hr_root.resizable(False, False)
    hr_root.attributes("-topmost", True)
    hr_root.grid_columnconfigure((0, 1), weight=1)
    hr_root.grid_rowconfigure(0, weight=1)

    left_frame = ctk.CTkFrame(hr_root)
    left_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

    right_frame = ctk.CTkFrame(hr_root)
    right_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

    left_combobox = ctk.CTkComboBox(left_frame, values=[i['login'] for i in workers])
    left_combobox.pack(anchor='nw', padx=5, pady=5, fill='x')

    ctk.CTkButton(left_frame, text='Открыть профиль', font=('Helvetica', 14), command=get_profile_in_func).pack(pady=5, padx=5, fill='x')

    ctk.CTkButton(left_frame, text='Удалить профиль', fg_color='#a6252e', hover_color='#890023',
                  font=('Helvetica', 14), command=delete_profile).pack(anchor='sw', pady=5, padx=5, fill='x', side='bottom')

    ctk.CTkButton(left_frame, text='Повысить до HR', font=('Helvetica', 14), command=add_hr).pack(pady=5, padx=5, fill='x')

    ctk.CTkButton(left_frame, text='Снять с должности HR', fg_color='#a6252e', hover_color='#890023',
                  font=('Helvetica', 14), command=delete_hr).pack(pady=5, padx=5, fill='x')

    right_combobox = ctk.CTkComboBox(right_frame, values=list(workers_without_login))
    right_combobox.pack(anchor='nw', padx=5, pady=5, fill='x')

    name_entry = ctk.CTkEntry(right_frame, placeholder_text='Имя и Фамилия')
    name_entry.pack(pady=5, padx=5, fill='x')

    post_entry = ctk.CTkEntry(right_frame, placeholder_text='Должность')
    post_entry.pack(pady=5, padx=5, fill='x')

    ctk.CTkButton(right_frame, text='Добавить аккаунт', command=add_account).pack(pady=5, padx=5, fill='x', side='bottom')


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
            get_profile()
            hr_window()
        elif data[data.find(';') + 1:] == 'worker':
            get_profile()
        else:
            messagebox.showinfo('SUCCESS', 'Please, go to your HR and ask him for registrate you\n:)')
            root.destroy()
    else:
        messagebox.showerror('FAIL', data[data.find(';') + 1:])

if __name__ == '__main__':
    # "login": <login>, "password": <password>, etc.
    worker = {}

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