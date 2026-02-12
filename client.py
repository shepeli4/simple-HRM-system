import json
import socket
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
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


def build_worker_ui(worker):
    root.grid_columnconfigure(0, weight=0)
    root.grid_columnconfigure(1, weight=0)
    root.grid_columnconfigure(2, weight=1)
    root.grid_rowconfigure(0, weight=1)
    frame1 = tk.Frame(root, bg='white', relief='solid', borderwidth=1)
    frame2 = tk.Frame(root, bg='white', relief='solid', borderwidth=1)
    frame3 = tk.Frame(root, bg='white', relief='solid', borderwidth=1)
    frame1.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
    frame2.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
    frame3.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)

    if worker['profile_photo']:
        pil_image = Image.open(f'imgs/{worker["profile_photo"]}')
    else:
        pil_image = Image.open(f'default_profile_pic.jpg')
    resized_image = pil_image.resize((400, 500), Image.Resampling.LANCZOS)
    img = ImageTk.PhotoImage(resized_image)
    image_label = tk.Label(frame1, image=img)
    image_label.pack()
    image_label.image = img
    method_lbl = tk.Label(
        frame1,
        text=worker['name'],
        bg='white',
        font=('Helvetica', 10),
        height=1
    )
    method_lbl.pack(padx=5, pady=5, expand=False)
    method_lbl = tk.Label(
        frame1,
        text=worker['login'] if worker['login'] else '',
        bg='white',
        font=('Helvetica', 10),
        height=1
    )
    method_lbl.pack(padx=5, pady=3)
    method_lbl = tk.Label(
        frame1,
        text=worker['post'],
        bg='white',
        font=('Helvetica', 10),
        height=1
    )
    method_lbl.pack(padx=5, pady=5)
    desc = scrolledtext.ScrolledText(frame2, width=40, height=33)
    desc.grid(column=1, row=1)
    desc.insert(tk.END, worker['description'])
    btn = tk.Button(
        frame2,
        text='Изменить описание',
        font=('Helvetica', 16),
        command=lambda: change_description(worker['login'], worker['name'], desc.get(1.0, tk.END))
    )
    btn.grid(row=2, column=1)


    DEL_BUTTON = tk.Button(frame2, text='')


    frame3.grid_rowconfigure(1, weight=1)  # Делаем ряд с холстом растягиваемым
    frame3.grid_columnconfigure(0, weight=1)  # Делаем колонку с холстом растягиваемой

    label_title = tk.Label(frame3, text='Бумаги', font=('Arial', 14, 'bold'), bg='white')
    label_title.grid(row=0, column=0, columnspan=2, pady=5)

    canvas = tk.Canvas(frame3, bg='white')
    scrollbar = tk.Scrollbar(frame3, orient='vertical', command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='white')

    def on_frame_configure(e):
        canvas.configure(scrollregion=canvas.bbox('all'))

    scrollable_frame.bind('Configure', on_frame_configure)

    canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.grid(row=1, column=0, sticky='nsew')
    scrollbar.grid(row=1, column=1, sticky='ns')

    def on_mousewheel(event):
        if platform.system() == 'Windows':
            canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
        elif platform.system() == 'Darwin':
            canvas.yview_scroll(int(-1 * event.delta), 'units')
        else:
            if event.num == 4:
                canvas.yview_scroll(-1, 'units')
            elif event.num == 5:
                canvas.yview_scroll(1, 'units')

    root.bind_all('MouseWheel', on_mousewheel)
    root.bind_all('Button-4', on_mousewheel)
    root.bind_all('Button-5', on_mousewheel)

    for i in worker['certificates']:
        tk.Button(
            scrollable_frame,
            text=f'{i}',
            width=53,
            height=2,
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

    root = tk.Tk()
    root.title('ne')
    root.geometry('1200x600')
    root.resizable(False, False)

    # login frame
    login_frame = tk.Frame(root)
    login_frame.pack(expand=True)

    tk.Label(login_frame, text='Username:').pack(pady=5)
    login_name = tk.Entry(login_frame)
    login_name.pack(pady=5)

    tk.Label(login_frame, text='Password:').pack(pady=5)
    login_pass = tk.Entry(login_frame, show='•')
    login_pass.pack(pady=5)

    tk.Button(login_frame, text='Log in', command=lambda: login_action(), cursor='hand2').pack(pady=5)
    tk.Button(login_frame, text='Register', command=lambda: login_action(True), cursor='hand2').pack(pady=5)

    root.protocol("WM_DELETE_WINDOW", close_app)
    root.mainloop()