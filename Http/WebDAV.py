import socket
import ssl
import base64
from hashlib import md5, sha256

host_addr = 'webdav.yandex.ru'
port = 443
password = "pass"
username = "mail"

def get_auth():
    auth = username + ":" + password
    auth = base64.b64encode(auth.encode()).__str__()
    return auth[2:len(auth) - 1]

def get_hash():
    with open("putfile.txt") as file:
        body = file.read()
        content_len = len(body)
        sha = sha256(body.encode())
        md = md5(body.encode())
        return sha.hexdigest(), md.hexdigest(), content_len, body

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
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    client = context.wrap_socket(client)
    get_request = {"method": "GET",
               "URI": "/test.txt",
               "version": "HTTP/1.1",
               "headers": {"host": host_addr, "Accept": "*/*", "Authorization": f'Basic {get_auth()}'}}
    # print(request_from_server(client, get_request))


    sha, md, content_len, body = get_hash()
    put_request = {"method": "PUT",
                   "URI": "/putfile.txt",
                   "version": "HTTP/1.1",
                   "headers": {"host": host_addr, "Accept": "*/*", "Authorization": f'Basic {get_auth()}',
                               "Etag": md, "Sha256": sha, "Expect": "100-continue", "Content-Type": "text/plain", "Content-Length": content_len}}
    if "100 Continue" in request_from_server(client, put_request):
        client.send(body.encode())