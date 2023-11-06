import socket
import select
import errno
import sys
import threading

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234
my_username = input("Username: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)

def send_message():
    while True:
        message = input(f'{my_username} > ')
        if message:
            if message.startswith('/delete '):
                # Handle message deletion
                message_parts = message.split(' ')
                if len(message_parts) == 2:
                    message_to_delete = message_parts[1]
                    message = f"/delete {message_to_delete}"
                else:
                    print("Invalid delete command. Usage: /delete <message_id>")
                    continue

            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(message_header + message)

send_thread = threading.Thread(target=send_message)
send_thread.daemon = True
send_thread.start()

# def create_user():
#     message = input(f'{my_username}')
#     if message:
#         if message.startswith('/add_user')

while True:
    try:
        while True:
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()
            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            if message.startswith('/delete '):
                # Handle message deletion
                if my_username == username:
                    # Delete the message if it was sent by the current user
                    message_parts = message.split(' ')
                    if len(message_parts) == 2:
                        message_id_to_delete = message_parts[1]
                        print(f'Message deleted: {message_id_to_delete}')
                    else:
                        print("Invalid delete command. Usage: /delete <message_id>")
                    continue

            print(f'{username} > {message}')
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()
        continue
    except Exception as e:
        print('Reading error: {}'.format(str(e)))
        sys.exit()
