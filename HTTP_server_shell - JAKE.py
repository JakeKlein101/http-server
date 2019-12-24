# HTTP Server Shell
# Author: Barak Gonen
# Purpose: Provide a basis for Ex. 4.4
# Note: The code is written in a simple way, without classes, log files or other utilities, for educational purpose
# Usage: Fill the missing functions and constants

import os
import socket

IP = "127.0.0.1"
PORT = 80
DEFAULT_URL = "index.html"
REDIRECTION_DICTIONARY = []
SOCKET_TIMEOUT = 1
SITE_FUNCTIONS = {'calculate-next': 'calculate_next', "calculate-area": "calculate_area",
                  'upload': 'upload_file', 'image': 'get_image'}

TEXT_HTTP_HEADER = b'HTTP/1.1 ' + b'200 OK' + b"\n" +\
                          b"Content-Type: text/html; charset=utf-8" + b'\n'\
                          + b'Connection: Keep-Alive\nServer: YOGEV\n' + b'\n'

JPG_HTTP_HEADER = b'HTTP/1.1 ' + b'200 OK' + b'\n' + b"Content-Type: image/jpg"\
                          + b'\n' + b'Connection: Keep-Alive\nServer: YOGEV\n' + b'\n'

JS_HTTP_HEADER = b'HTTP/1.1 ' + b'200 OK' + b'\n' + \
                          b"Content-Type: text/javascript; charset=UTF-8; charset=utf-8"\
                          + b'\n' \
                          + b'Connection: Keep-Alive\nServer: YOGEV\n' + b'\n'

CSS_HTTP_HEADER = b'HTTP/1.1 ' + b'200 OK' + b'\n' + b"Content-Type: text/css; charset=utf-8" + b'\n'\
                          + b'Connection: Keep-Alive\nServer: YOGEV\n' + b'\n'

ICO_HTTP_HEADER = b'HTTP/1.1 ' + b'200 OK' + b'\n' + \
                          b"Content-Type: image/x-icon; charset=UTF-8; charset=utf-8" \
                          + b'\n' \
                          + b'Connection: Keep-Alive\nServer: YOGEV\n' + b'\n'


class Functions:
    @staticmethod
    def get_image(image_name):
        with open("webroot/" + image_name + ".jpg", "rb") as file:
            return file.read()

    @ staticmethod
    def calculate_next(num):
        return int(num) + 1

    @staticmethod
    def calculate_area(height, width):
        return (int(height) * int(width)) / 2

    @staticmethod
    def upload_file(filename):  # working on supporting the post protocol
        pass
        with open("pic", "wb") as file:
            file.write()


def get_params(params):
    return tuple([p.split('=')[-1] for p in params.split('&')])


def is_function(func):
    if '?' in func:
        return func.split('?')[0] in SITE_FUNCTIONS
    return func in SITE_FUNCTIONS


def get_file_name(url):
    if url == "/":
        return "index"
    return url.split(".")[0]


def get_file_type(url):
    if url == "/":
        return "html"
    print(url.split(".")[-1])
    return url.split(".")[-1]


def get_file_data(filename):
    """ Get data from file """
    with open("webroot/" + filename, 'rb') as data:  # opens requested file in byte format
        return data.read()


def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client"""
    # TO DO : add code that given a resource (URL and parameters) generates the proper response
    if resource == '/':
        url = DEFAULT_URL
    else:
        url = resource
    # TO DO: check if URL had been redirected, not available or other error code. For example:
    if os.path.isfile('webroot/' + url):
        if url in REDIRECTION_DICTIONARY:
            pass
            # TO DO: send 302 redirection response

        # TO DO: extract requested file tupe from URL (html, jpg etc)
        filetype = get_file_type(url)
        if filetype == 'html':
            http_header = TEXT_HTTP_HEADER
        elif filetype == 'jpg':
            http_header = JPG_HTTP_HEADER
        elif filetype == 'css':
            http_header = CSS_HTTP_HEADER
        elif filetype == "js":
            http_header = JS_HTTP_HEADER
        elif filetype == "ico":
            http_header = ICO_HTTP_HEADER
        else:
            http_header = b"pycharm is annoying"
        data = get_file_data(url)  # TO DO: read the data from the file
        http_response = http_header + data
        client_socket.send(http_response)

    elif is_function(url.split('/')[-1]):
        func_name = url.split('/')[-1]
        params = None
        if "?" in func_name:
            func_name, params = func_name.split("?")
            print(func_name, params)
        func = getattr(Functions, SITE_FUNCTIONS[func_name])
        params = get_params(params)
        print(*params)
        file_data = str(func(*params)).encode()
        if func_name == "image":
            http_header = JPG_HTTP_HEADER
        else:
            http_header = TEXT_HTTP_HEADER
        http_response = http_header + file_data
        client_socket.send(http_response)

    else:
        http_response = b'HTTP/1.1 ' + b'404 NOT FOUND' + b"\n" + \
                        b"Content-Type: text/html; charset=utf-8" + b'\n' \
                        + b'Connection: Keep-Alive\nServer: YOGEV\n' + b'\n'
        client_socket.send(http_response)


def validate_http_request(request):
    """ Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL """
    data_list = request.split()
    print(data_list)
    if data_list:
        if ("GET" in data_list or "POST" in data_list) and r"HTTP/1.1" in data_list:
            return True, data_list[1]
        else:
            return False, "INVALID"
    return False, "INVALID"


def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print('Client connected')
    while True:
        client_request = (client_socket.recv(1024).decode())
        valid_http, resource = validate_http_request(client_request)
        if valid_http:
            print('Got a valid HTTP request')
            handle_client_request(resource, client_socket)
        else:
            print('Error: Not a valid HTTP request')
            break
    print('Closing connection')
    client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(10)
    print("Listening for connections on port %d" % PORT)
    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        try:
            handle_client(client_socket)
        except socket.timeout:
            client_socket.close()
            print("timed out")


if __name__ == "__main__":
    # Call the main handler function
    main()
