import socket
import threading
import json


def send_img(conn, path):
    f_name = path[path.rfind('\\'):]
    print(f_name)
    conn.send(f_name.encode('utf-8'))
    with open(path, 'rb') as f:
        chunk = f.read(4096)
        while chunk:
            conn.send(chunk)
            chunk = f.read(4096)
    print('end')
    conn.send('END'.encode('utf-8'))


def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 1800))
    sock.listen(5)

    try:
        while True:
            conn, addr = sock.accept()
            print(conn, addr)
            thread_registration = threading.Thread(target=handle_client, args=(conn,))
            thread_registration.start()
    except Exception as e:
        print(e)
        sock.close()


def send_profile(conn, name, login=None):
    if login:
        for i in workers:
            if i['login'] == login:
                worker = i
                break
    else:
        for i in workers:
            if i['name'] == name and not i['login']:
                worker = i
                break
    conn.send(json.dumps(worker).encode('utf-8'))
    if worker['profile_photo']:
        send_img(conn, f'server_imgs\\{worker["profile_photo"]}')
    for i in worker['certificates']:
        send_img(conn, f'server_imgs\\{i}')


def handle_client(conn):
    not_login_in = True
    while not_login_in:
        data = conn.recv(1024).decode('utf-8')
        if data[data.rfind(';') + 1:] == 'login':
            name = data[:data.find(':')]
            password = data[data.find(':') + 1:data.find(';')]
            for i in HRs:
                if i['login'] == name and i['password'] == password:
                    conn.send('SUCCESS;HR'.encode('utf-8'))
                    not_login_in = False
                    break
            else:
                for i in workers:
                    if i['login'] == name and i['password'] == password:
                        conn.send('SUCCESS;worker'.encode('utf-8'))
                        not_login_in = False
                        break
                else:
                    conn.send('FAIL;Wrong name or password'.encode('utf-8'))

        elif data[data.rfind(';') + 1:] == 'registration': # idk, need to more braining
            name = data[:data.find(':')]
            password = data[data.find(':') + 1:data.find(';')]
            if name in list(map(lambda x: x['login'], HRs)) or name in list(map(lambda x: x['login'], logins_without_account)):
                conn.send('FAIL;User with this login already exist'.encode('utf-8'))
                continue
            else:
                conn.send('SUCCESS;dummy'.encode('utf-8'))
                logins_without_account.append({'login': name, 'password': password})
                with open('logins_without_account.json', 'w', encoding='utf-8') as f:
                    json.dump(logins_without_account, f)


if __name__ == '__main__':
    # format: [{'login': <login>, 'password': <password>}]
    HRs = [{'login': 'shepeli18', 'password': '9'},
           {'login': 'V3nalita', 'password': '9'}]
    try:
        with open('HRs.json', encoding='utf-8') as f:
            HRs = json.load(f)
    except FileNotFoundError:
        with open('HRs.json', encoding='utf-8') as f:
            json.dump([{'login': 'shepeli18', 'password': '9'},
                            {'login': 'V3nalita', 'password': '9'}], f)

    # format: [{'login': <login>, 'password': <password>...}]
    workers = [{'login': 'shepeli18', 'password': '9'}, {'login': 'V3nalita', 'password': '9'}]
    try:
        with open('workers.json', encoding='utf-8') as f:
            workers = json.load(f)
    except FileNotFoundError:
        with open('workers.json', encoding='utf-8') as f:
            json.dump([{'login': 'shepeli18', 'password': '9'}, {'login': 'V3nalita', 'password': '9'}], f)
    print(HRs, workers)

    # format: [{'login': <login>, 'password': <password>}]
    logins_without_account = []
    try:
        with open('logins_without_account.json', encoding='utf-8') as f:
            logins_without_account = json.load(f)
    except FileNotFoundError:
        with open('logins_without_account.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
    start_server()
