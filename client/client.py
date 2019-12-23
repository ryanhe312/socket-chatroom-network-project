import sys

from PyQt5.QtWidgets import QMainWindow,QApplication
from view import Ui_MainWindow
from network import Client_Network

class Client_View(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()


class Client(object):
    def __init__(self,view:Client_View,network:Client_Network):
        self.view=view
        self.network=network
        self.view.pushButton.clicked.connect(self.send)
        self.view.pushButton_2.clicked.connect(self.login)
        self.network.msg.connect(self.recv_msg)
        self.network.stat.connect(self.recv_stat)

    def send(self):
        message=self.view.textEdit.toPlainText()
        self.network.do_send(message)
        self.view.textEdit.setText("")

    def login(self):
        nickname=self.view.lineEdit.text()
        self.network.do_login(nickname)

    def recv_msg(self,msg):
        self.view.textBrowser.append(msg)

    def recv_stat(self,stat):
        self.view.statusbar.showMessage(stat)
        


if __name__=='__main__':
    app = QApplication(sys.argv)
    view = Client_View()
    network = Client_Network()
    client = Client(view,network)
    sys.exit(app.exec_())