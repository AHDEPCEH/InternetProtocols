import socket
import ssl
import base64

host_addr = 'smtp.yandex.ru'
port = 465
user_name = 'mail'
password ='your pswd'

def request(socket, request : bytearray) -> str:
    socket.send((request.decode() + '\n').encode())
    recv_data = socket.recv(65535).decode()
    return recv_data

with open("pass", "r") as file:
    password = file.readline()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((host_addr, port))
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    client = context.wrap_socket(client)
    print(client.recv(1024))
    print(request(client, bytes(f"EHLO {user_name}", "utf-8")))

    base64login = base64.b64encode(user_name.encode())
    base64password = base64.b64encode(password.encode())

    print(request(client, b'AUTH LOGIN'))
    print(request(client, base64login))
    print(request(client, base64password))

    print(request(client, bytes(f'MAIL FROM:{user_name}@yandex.ru', "utf-8")))
    print(request(client, bytes(f"RCPT TO:{user_name}@yandex.ru", "utf-8")))
    print(request(client, b'DATA'))

    with open('msg.txt') as file:
        msg = file.read() + '\n.\n'
        print(msg)
        print(request(client, msg.encode()))