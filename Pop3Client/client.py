import socket
import ssl
import base64
import random

host_addr = 'pop.yandex.ru'
port = 995
user_name = 'mail'
password = str


# def generate_random_str():
#     return "boundary_askljhvaxmsvhdkl"


def request(socket, request):
    socket.send(request + b'\n')
    # написать получение данных правильно
    recv_data = socket.recv(65535).decode()
    return recv_data


# def create_letter():
#     with open('headers.txt', 'r') as file:
#         letter = file.read() + '\n'
#
#     boundary = generate_random_str()
#
#     letter += f"""Content-Type: multipart/mixed;
#     boundary=\"{boundary}\""""
#     letter += '\n\n'
#
#     letter += f'--{boundary}'
#     # TODO заголовки для текста (Content-Type, \n)
#
#     with open('body.txt', 'r') as file:
#         letter += file.read() + '\n'
#     letter += f'--{boundary}' + '\n'
#     # TODO заголовки для картинки (Content-Type, \n)
#
#     with open('cat.jpg', 'rb') as file:
#         letter += base64.b64encode(file.read()).decode()
#     letter += '\n'
#     letter += f'--{boundary}--' + '\n.\n'
#     return letter


# print(create_letter())
# quit()

with open("pass", "r") as file:
    password = file.readline()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((host_addr, port))
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    # context = ssl.create_default_context()
    client = context.wrap_socket(client)
    print(client.recv(1024).decode("utf-8"))
    print(request(client, bytes(f"USER {user_name}", "utf-8")))
    print(request(client, bytes(f"PASS {password}", "utf-8")))
    count_messages = request(client, b'STAT')
    for i in range(1, int(count_messages.split(' ')[1]) + 1):
        print(request(client, bytes(f"RETR {str(i)}", "utf-8")))
        ans = client.recv(1024).decode("utf-8")
        while ans != '':
            print(ans)
            ans = client.recv(1024).decode("utf-8")
        print()
    print(request(client, b'QUIT'))
