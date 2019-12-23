import socket
import threading
import json
import time
import os
import ssl

from PyQt5.QtCore import QObject,pyqtSignal

class Client_Network(QObject):
    msg=pyqtSignal(str)
    stat=pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.__id = None
        self.__nickname = None   
        self.__conn_flag = False
        self.__context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.__context.load_verify_locations(os.path.join('server.crt'))

    def __receive_message_thread(self):
        while True:
            try:
                buffer = self.__ssocket.recv(1024).decode()
                obj = json.loads(buffer)
                self.msg.emit('[' + str(obj['sender_nickname']) + '(' + str(obj['sender_id']) + ')' + ']' + obj['message'])

            except Exception:
                self.stat.emit('[Error] Failed to fetch data from server.')
                self.__conn_flag = False
                return

            time.sleep(1)
            

    def __send_message_thread(self, message):
        self.__ssocket.send(json.dumps({
            'type': 'broadcast',
            'sender_id': self.__id,
            'message': message
        }).encode())

    def do_login(self, nickname):
        self.__conn_flag = False
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.__socket.connect(('127.0.0.1', 8888))
        except Exception:
            self.stat.emit('[Error] Failed to connect to the sever, please reconnect.')
            self.__socket.close()
            return

        self.__ssocket = self.__context.wrap_socket(self.__socket, server_hostname='SERVER')
        #self.__ssocket = self.__socket
        self.__ssocket.send(json.dumps({
            'type': 'login',
            'nickname': nickname
        }).encode())
        
        try:
            buffer = self.__ssocket.recv(1024).decode()
            obj = json.loads(buffer)
            if obj['id']:
                self.__nickname = nickname
                self.__id = obj['id']
                self.stat.emit('[Welcome] Login Succeeded')
                thread = threading.Thread(target=self.__receive_message_thread)
                thread.setDaemon(True)
                thread.start()
            else:
                self.stat.emit('[Error] Failed to login, please try again.')
                self.__ssocket.close()
                return
        except Exception:
            self.stat.emit('[Error] [Error] Failed to connect to the sever, please reconnect.')
            self.__ssocket.close()
            return

        self.__conn_flag = True

    def do_send(self, message):
        if self.__conn_flag == False:
            self.stat.emit('[Notice] Please login first.')
            return

        self.msg.emit('[' + str(self.__nickname) + '(' + str(self.__id) + ')' + ']'+message)
        thread = threading.Thread(target=self.__send_message_thread, args=(message, ))
        thread.setDaemon(True)
        thread.start()