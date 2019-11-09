import socket
import threading
import json
import time
import os
import ssl

from PyQt5.QtCore import QObject,pyqtSignal

class Client_Network(QObject):
    """
    网络应用
    """

    # 初始化QT信号量
    msg=pyqtSignal(str)
    stat=pyqtSignal(str)

    def __init__(self):
        """
        构造
        """
        super().__init__()
        self.__id = None
        self.__nickname = None   
        self.__conn_flag = False
        self.__context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.__context.load_verify_locations(os.path.join(os.getcwd(), 'ca','ca.crt'))

    def __receive_message_thread(self):
        """
        接受消息线程
        """

        while True:
            # 尝试接受消息
            try:
                buffer = self.__ssocket.recv(1024).decode()
                obj = json.loads(buffer)
                self.msg.emit('[' + str(obj['sender_nickname']) + '(' + str(obj['sender_id']) + ')' + ']' + obj['message'])

            # 如果出错结束进程
            except Exception:
                self.stat.emit('[Error] 无法从服务器获取数据')
                self.__conn_flag = False
                return
            

    def __send_message_thread(self, message):
        """
        发送消息线程
        :param message: 消息内容
        """
        self.__ssocket.send(json.dumps({
            'type': 'broadcast',
            'sender_id': self.__id,
            'message': message
        }).encode())

    def do_login(self, nickname):
        """
        登录聊天室
        :param nickname: 名字
        """

        # 连接中断
        self.__conn_flag = False

        # 创建新连接
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 尝试连接服务器
        try:
            self.__socket.connect(('127.0.0.1', 8888))
        except Exception:
            self.stat.emit('[Error] 无法连接到服务器, 请重新连接')
            self.__socket.close()
            return

        # SSL打包
        self.__ssocket = self.__context.wrap_socket(self.__socket, server_hostname='SERVER')

        # 将昵称发送给服务器，获取用户id
        self.__ssocket.send(json.dumps({
            'type': 'login',
            'nickname': nickname
        }).encode())
        
        # 尝试接受数据
        try:
            buffer = self.__ssocket.recv(1024).decode()
            obj = json.loads(buffer)
            if obj['id']:
                self.__nickname = nickname
                self.__id = obj['id']
                self.stat.emit('[Welcome] 成功登录到聊天室')

                # 开启子线程用于接受数据
                thread = threading.Thread(target=self.__receive_message_thread)
                thread.setDaemon(True)
                thread.start()
            else:
                self.stat.emit('[Error] 无法登录到聊天室, 请重新连接')
                self.__ssocket.close()
                return
        except Exception:
            self.stat.emit('[Error] 无法从服务器获取数据, 请重新连接')
            self.__ssocket.close()
            return

        # 连接建立
        self.__conn_flag = True

    def do_send(self, message):
        """
        发送消息
        : param message: 消息内容
        """

        # 确认已经连接到服务器
        if self.__conn_flag == False:
            self.stat.emit('[Notice] 尚未建立连接, 请先登录')
            return

        # 显示自己发送的消息
        self.msg.emit('[' + str(self.__nickname) + '(' + str(self.__id) + ')' + ']'+message)
        # 开启子线程用于发送数据
        thread = threading.Thread(target=self.__send_message_thread, args=(message, ))
        thread.setDaemon(True)
        thread.start()