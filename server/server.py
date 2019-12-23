import socket
import threading
import json
import ssl
import os
import time

class Server:
    def __init__(self):
        self.__connections = list()
        self.__nicknames = list()
        self.__context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.__context.load_cert_chain(os.path.join('server.crt'), os.path.join('server.key'))

    def __user_thread(self, user_id):
        connection = self.__connections[user_id]
        nickname = self.__nicknames[user_id]
        print('[Server] User', user_id, nickname, 'joined this chatroom')
        self.__broadcast(message='User ' + str(nickname) + '(' + str(user_id) + ')' + 'joined this chatroom')

        while True:
            try:
                buffer = connection.recv(1024).decode()
                obj = json.loads(buffer)
                if obj['type'] == 'broadcast':
                    self.__broadcast(obj['sender_id'], obj['message'])
                else:
                    print('[Server] Failed to parse json:', connection.getsockname(), connection.fileno())
            except Exception:
                print('[Server] Connection failed:', connection.getsockname(), connection.fileno())
                self.__broadcast(message='User ' + str(nickname) + '(' + str(user_id) + ')' + 'exited the chatroom')
                self.__connections[user_id].close()
                self.__connections[user_id] = None
                self.__nicknames[user_id] = None
                return

            time.sleep(0.1)

    def __broadcast(self, user_id=0, message=''):
        for i in range(1, len(self.__connections)):
            if user_id != i and self.__connections[i]:
                self.__connections[i].send(json.dumps({
                    'sender_id': user_id,
                    'sender_nickname': self.__nicknames[user_id],
                    'message': message
                }).encode())

    def start(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind(('127.0.0.1', 8888))
        self.__socket.listen(10)
        self.__ssocket = self.__context.wrap_socket(self.__socket, server_side=True)
        #self.__ssocket = self.__socket
        print('[Server] Server is running......')
        self.__connections.clear()
        self.__nicknames.clear()
        self.__connections.append(None)
        self.__nicknames.append('System')

        while True:
            connection, _ = self.__ssocket.accept()
            print('[Server] Received one connection', connection.getsockname(), connection.fileno())

            try:
                buffer = connection.recv(1024).decode()
                obj = json.loads(buffer)
                if obj['type'] == 'login':
                    self.__connections.append(connection)
                    self.__nicknames.append(obj['nickname'])
                    connection.send(json.dumps({
                        'id': len(self.__connections) - 1
                    }).encode())

                    thread = threading.Thread(target=self.__user_thread, args=(len(self.__connections) - 1, ))
                    thread.setDaemon(True)
                    thread.start()
                else:
                    print('[Server] Failed to parse json:', connection.getsockname(), connection.fileno())
            except Exception:
                print('[Server] Failed to receive:', connection.getsockname(), connection.fileno())


if __name__ == "__main__":
    server = Server()
    server.start()
