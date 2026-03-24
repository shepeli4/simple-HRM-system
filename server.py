import socket
import threading
import json
import os


def get_file(conn):
    f_name, f_size, buff = conn.recv(512).decode('utf-8').split(';')
    f_size = int(f_size)
    path = f'{os.getcwd()}\\server_imgs'
    with open(f'{path}\\{len(os.listdir(path))}{f_name[f_name.rfind("."):]}', 'wb') as f:
        for i in range(f_size // 4096):
            chunk = conn.recv(4096)
            f.write(chunk)
        chunk = conn.recv(f_size - f_size // 4096 * 4096)
        f.write(chunk)


def send_file(conn, path):
    f_name = path[path.rfind('\\'):]
    file_size = os.path.getsize(path)
    print(f_name)
    # file_name;file_size(bytes);\x00\x00\x00\x00...
    conn.send(f'{f_name};{file_size};'.encode('utf-8') + bytearray(512 - len(f'{f_name};{file_size};'.encode('utf-8'))))
    with open(path, 'rb') as f:
        chunk = f.read(4096)
        while chunk:
            conn.send(chunk)
            chunk = f.read(4096)
    print('img_sent')



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
    print('send_profile')
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
    print(worker)
    # worker;\x00\x00\x00\x00...
    conn.send(f'{json.dumps(worker)};'.encode('utf-8')+ bytearray(1024 - len(f'{json.dumps(worker)};'.encode('utf-8'))))
    if worker['profile_photo']:
        send_file(conn, f'server_imgs\\{worker["profile_photo"]}')
    for i in worker['certificates']:
        send_file(conn, f'server_imgs\\{i}')


def user_communication(conn):
    while True:
        data = conn.recv(512).decode('utf-8')
        data = data[:data.rfind(';')]
        command, args = data[:data.find(';')], data[data.find(';') + 1:]
        if command == 'CHANGE_DESC':
            # args = '<description>:<worker_name>;<worker_login>'
            desc, worker_name, worker_login = args[:args.rfind(':')], args[args.rfind(':') + 1:args.rfind(';')], args[args.rfind(';') + 1:]
            if worker_login:
                for i in range(len(workers)):
                    if workers[i]['login'] == worker_login:
                        workers[i]['description'] = desc
                        with open('workers.json', 'w') as f:
                            json.dump(workers, f)

        elif command == 'EXIT':
            print('user left')
            return

        elif command == 'CHANGE_PROFILE_PIC':
            file_name, worker_login, worker_name = [args[:args.rfind(':')],
                                                    args[args.rfind(':') + 1:args.rfind(';')],
                                                    args[args.rfind(';') + 1:]]
            if worker_login:
                for i in range(len(workers)):
                    if workers[i]['login'] == worker_login:
                        path = f'{os.getcwd()}\\server_imgs\\'
                        workers[i]['profile_photo'] = f'{len(os.listdir(path))}{file_name[file_name.rfind("."):]}'
                        get_file(conn)
                        with open('workers.json', 'w') as f:
                            json.dump(workers, f)
            else:
                for i in range(len(workers)):
                    if workers[i]['name'] == worker_name and workers[i]['login'] == '':
                        path = f'{os.getcwd()}\\server_imgs\\'
                        workers[i]['profile_photo'] = f'{len(os.listdir(path))}{file_name[file_name.rfind("."):]}'
                        get_file(conn)
                        with open('workers.json', 'w') as f:
                            json.dump(workers, f)

        elif command == 'ADD_CERTIFICATE':
            file_name, worker_login, worker_name = [args[:args.rfind(':')],
                                                    args[args.rfind(':') + 1:args.rfind(';')],
                                                    args[args.rfind(';') + 1:]]
            if worker_login:
                for i in range(len(workers)):
                    if workers[i]['login'] == worker_login:
                        path = f'{os.getcwd()}\\server_imgs\\'
                        workers[i]['certificates'].append(f'{len(os.listdir(path))}{file_name[file_name.rfind("."):]}')
                        message = f'{json.dumps(workers[i])};'.encode('utf-8')
                        conn.send(message + bytearray(512 - len(message)))
            else:
                for i in range(len(workers)):
                    if workers[i]['name'] == worker_name and workers[i]['login'] == '':
                        path = f'{os.getcwd()}\\server_imgs\\'
                        workers[i]['certificates'].append(f'{len(os.listdir(path))}{file_name[file_name.rfind("."):]}')
            get_file(conn)
            with open('workers.json', 'w') as f:
                json.dump(workers, f)

        elif command == 'DELETE_CERTIFICATE':
            file_name, worker_login, worker_name = [args[:args.rfind(':')],
                                                    args[args.rfind(':') + 1:args.rfind(';')],
                                                    args[args.rfind(';') + 1:]]
            if worker_login:
                for i in range(len(workers)):
                    if workers[i]['login'] == worker_login:
                        with open(f'{os.getcwd()}\\server_imgs\\{file_name}', 'wb') as f:
                            f.write(bytearray(1))
                        del workers[i]['certificates'][workers[i]['certificates'].index(file_name)]
                        print(workers[i]['certificates'])
            else:
                for i in range(len(workers)):
                    if workers[i]['name'] == worker_name and workers[i]['login'] == '':
                        with open(f'{os.getcwd()}\\server_imgs\\{file_name}', 'wb') as f:
                            f.write(bytearray(1))
                        del workers[i]['certificates'][workers[i]['certificates'].index(file_name)]
                        print(workers[i]['certificates'])
            with open('workers.json', 'w') as f:
                json.dump(workers, f)

        elif command == 'GET_PROFILE':
            worker_login, worker_name = args[:args.rfind(';')], args[args.rfind(';') + 1:]
            send_profile(conn, worker_name, worker_login)

        elif command == 'DELETE_PROFILE':
            worker_login, worker_name = args[:args.rfind(';')], args[args.rfind(';') + 1:]
            for i in range(len(workers)):
                if worker_login == workers[i]['login'] and worker_name == workers[i]['name']:
                    del workers[i]
                    with open('workers.json', 'w', encoding='utf-8') as f:
                        json.dump(workers, f)
                    break

        elif command == 'ADD_ACCOUNT':
            worker_login, worker_name, worker_post = [args[:args.find(':')],
                                                      args[args.find(':') + 1: args.rfind(':')],
                                                      args[args.rfind(':') + 1:]]
            workers.append({'login': worker_login, 'password': logins_without_account[worker_login], 'post': worker_post,
                            'profile_photo': '', 'certificates': [], 'name': worker_name, 'description': ''})
            del logins_without_account[worker_login]
            with open('workers.json', 'w', encoding='utf-8') as f:
                json.dump(workers, f)
            with open('logins_without_account.json', 'w', encoding='utf-8') as f:
                json.dump(logins_without_account, f)
            print(workers, logins_without_account, sep='\n')

        elif command == 'ADD_HR':
            worker_login, worker_name = args[:args.rfind(';')], args[args.rfind(';') + 1:]
            for i in HRs:
                if worker_login == i['login']:
                    message = f'ERROR;Этот пользователь уже находится на должности HR;'.encode('utf-8')
                    conn.send(message + bytearray(256 - len(message)))
                    break
            else:
                for i in range(len(workers)):
                    print(worker_login, workers[i]['login'])
                    if worker_login == workers[i]['login'] and worker_name == workers[i]['name']:
                        HRs.append({'login': worker_login, 'password': workers[i]['password']})
                        message = f'SUCCESS;'.encode('utf-8')
                        conn.send(message + bytearray(256 - len(message)))
                        with open('HRs.json', 'w') as f:
                            json.dump(HRs, f)
                        break

        elif command == 'DELETE_HR':
            worker_login, worker_name = args[:args.rfind(';')], args[args.rfind(';') + 1:]
            for i in range(len(HRs)):
                if worker_login == HRs[i]['login']:
                    del HRs[i]
                    message = f'SUCCESS;'.encode('utf-8')
                    conn.send(message + bytearray(256 - len(message)))
                    with open('HRs.json', 'w') as f:
                        json.dump(HRs, f)
                    break
            else:
                message = f'ERROR;Этот пользователь не находится на должности HR;'.encode('utf-8')
                conn.send(message + bytearray(256 - len(message)))

def handle_client(conn):
    not_login_in = True
    while not_login_in:
        data = conn.recv(1024).decode('utf-8')
        if data[data.rfind(';') + 1:] == 'login':
            login = data[:data.find(':')]
            password = data[data.find(':') + 1:data.find(';')]
            for i in HRs:
                if i['login'] == login and i['password'] == password:
                    conn.send('SUCCESS;HR'.encode('utf-8'))
                    not_login_in = False
                    send_profile(conn, i['login'], login)
                    message = (json.dumps(workers) + ';').encode('utf-8')
                    conn.send(message + bytearray(2048 - len(message)))
                    message = (json.dumps(logins_without_account) + ';').encode('utf-8')
                    conn.send(message + bytearray(1024 - len(message)))
                    break
            else:
                for i in workers:
                    if i['login'] == login and i['password'] == password:
                        conn.send('SUCCESS;worker'.encode('utf-8'))
                        not_login_in = False
                        send_profile(conn, i['name'], login)
                        break
                else:
                    conn.send('FAIL;Wrong login or password'.encode('utf-8'))

        elif data[data.rfind(';') + 1:] == 'registration': # idk, need to more braining
            login = data[:data.find(':')]
            password = data[data.find(':') + 1:data.find(';')]
            if login in list(map(lambda x: x['login'], HRs)) or login in list(logins_without_account.keys()):
                conn.send('FAIL;User with this login already exist'.encode('utf-8'))
                continue
            else:
                conn.send('SUCCESS;dummy'.encode('utf-8'))
                logins_without_account[login] =  password
                with open('logins_without_account.json', 'w', encoding='utf-8') as f:
                    json.dump(logins_without_account, f)

    thread_registration = threading.Thread(target=user_communication, args=(conn,))
    thread_registration.start()


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
        with open('workers.json', 'w', encoding='utf-8') as f:
            json.dump([{'login': 'shepeli18', 'password': '9'}, {'login': 'V3nalita', 'password': '9'}], f)
    print(HRs, workers)

    # format: {<login>: <password>}
    logins_without_account = {}
    try:
        with open('logins_without_account.json', encoding='utf-8') as f:
            logins_without_account = json.load(f)
    except FileNotFoundError:
        with open('logins_without_account.json', 'w', encoding='utf-8') as f:
            json.dump({}, f)
    start_server()