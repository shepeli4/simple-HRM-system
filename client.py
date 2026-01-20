import socket
import tkinter as tk
from tkinter import messagebox
from os import getcwd, listdir, path, remove


def close_app():
    folder_path = getcwd() + '\\imgs'
    for item in listdir(folder_path):
        item_path = path.join(folder_path, item)
        remove(item_path)


def get_img():
    global sock
    f_name = sock.recv(4096).decode('utf-8')
    with open(f'{getcwd()}\\imgs\\{f_name}', 'wb') as f:
        chunk = sock.recv(4096)
        while True:
            try:
                if chunk.decode('utf-8') == 'END':
                    break
                raise ValueError('IMG NOT FINISHED')
            except (ValueError, UnicodeDecodeError):
                f.write(chunk)
                chunk = sock.recv(4096)
    print('END')


def build_worker_ui():
    pass


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
        print(data)

        get_img()
        print('end')
    else:
        messagebox.showerror('FAIL', 'Wrong name or password')

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.1.31', 1800))  # --- CHANGE IP ON PUBLIC ---

    root = tk.Tk()
    root.title('ne')
    root.geometry('1200x600')

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
