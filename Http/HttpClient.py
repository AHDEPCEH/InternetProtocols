import socket

host_addr = 'url'
port = 80


def request_from_server(socket, request: dict):
    message = ""
    message += f'{request.get("method")} {request.get("URI")} {request.get("version")}\n'
    headers = request.get("headers")
    headers = dict(headers)
    for key, val in headers.items():
        message += f'{key}: {val}\n'
    print(message)
    message += '\n'
    socket.send(bytes(message, "utf-8"))
    recv_data = socket.recv(4096)
    while not recv_data:
        recv_data += socket.recv(4096)
    return recv_data.decode("cp1251")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((host_addr, port))
    request = {"method": "GET",
               "URI": "/",
               "version": "HTTP/1.0",
               "headers": {}}
    print(request_from_server(client, request))