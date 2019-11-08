import sys

from PyQt5.QtWidgets import QMainWindow,QApplication
from view import Ui_MainWindow
from network import Client_Network

class Client_View(QMainWindow,Ui_MainWindow):
    """
    图形窗口
    """

    def __init__(self):
        """
        初始化UI
        """

        super().__init__()
        self.setupUi(self)
        self.show()


class Client(object):
    """
    控制台
    """

    def __init__(self,view:Client_View,network:Client_Network):
        """
        初始化信号
        """
        
        self.view=view
        self.network=network

        # 信号与槽连接
        self.view.pushButton.clicked.connect(self.send)
        self.view.pushButton_2.clicked.connect(self.login)
        self.network.msg.connect(self.recv_msg)
        self.network.stat.connect(self.recv_stat)

    def send(self):
        """
        发送消息
        """

        message=self.view.textEdit.toPlainText()
        self.network.do_send(message)
        self.view.textEdit.setText("")

    def login(self):
        """
        登录
        """

        nickname=self.view.lineEdit.text()
        self.network.do_login(nickname)

    def recv_msg(self,msg):
        """
        收到消息
        """
        self.view.textBrowser.append(msg)

    def recv_stat(self,stat):
        """
        更新状态栏
        """
        self.view.statusbar.showMessage(stat)
        


if __name__=='__main__':
    app = QApplication(sys.argv)
    view = Client_View()
    network = Client_Network()
    client = Client(view,network)
    sys.exit(app.exec_())