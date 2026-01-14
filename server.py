import socket
import threading
import json


def send_img(conn, path):
    with open(path, 'rb') as f:
        chunk = f.read(4096)
        while chunk:
            conn.send(chunk)
            chunk = f.read(4096)


def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 1800))
    sock.listen(5)

    try:
        while True:
            conn, addr = sock.accept()
            print(conn, addr)
            thread_registration = threading.Thread(target=handle_client, args=(conn, addr))
            thread_registration.start()
    except Exception as e:
        print(e)
        sock.close()


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
                    conn.send('FAIL'.encode('utf-8'))

        elif data[data.rfind(';') + 1:] == 'register': # idk, need to more braining
            pass


if __name__ == '__main__':
    # format: [{'login': <login>, 'password': <password>}]
    HRs = [{'login': 'shepeli18', 'password': '9', 'post': 'dibil'},
           {'login': 'V3nalita', 'password': '9', 'post': 'nigger'},
           {'login': 'Sak4ra', 'password': '9', 'post': 'zadrot'}]
    try:
        with open('HRs.json', encoding='utf-8') as f:
            HRs = json.load(f)
    except FileNotFoundError:
        with open('HRs.json', encoding='utf-8') as f:
            json.dump([{'login': 'shepeli18', 'password': '9', 'post': 'dibil'},
                            {'login': 'V3nalita', 'password': '9', 'post': 'nigger'},
                            {'login': 'Sak4ra', 'password': '9', 'post': 'zadrot'}], f)

    # format: [{'login': <login>, 'password': <password>, etc.}]
    workers = [{'login': 'shepeli18', 'password': '9'}, {'login': 'V3nalita', 'password': '9'}]
    try:
        with open('workers.json', encoding='utf-8') as f:
            workers = json.load(f)
    except FileNotFoundError:
        with open('HRs.json', encoding='utf-8') as f:
            json.dump([{'login': 'shepeli18', 'password': '9'}, {'login': 'V3nalita', 'password': '9'}], f)
    print(HRs, workers)
    start_server()