import sys
import os
import argparse
from PIL import Image
from PIL.ImageQt import ImageQt
import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5 import QtGui


def get_cords():
    """Function returns tuple of coordinates and a delta from console args"""
    try:
        parser = argparse.ArgumentParser(description='set coordinates for program')
        parser.add_argument('lon', nargs=1, type=float, metavar='LON')
        parser.add_argument('lat', nargs=1, type=float, metavar='LAT')
        parser.add_argument('delta', nargs=1, type=float, metavar='DELTA')
        args = parser.parse_args()
        cords = tuple(map(lambda x: str(x), args.lon + args.lat))
        return cords, str(args.delta[0])
    except Exception as e:
        print(e)
        sys.exit(2)


class MainWindow(QMainWindow):
    """Main Window class"""

    def __init__(self, *args):
        super().__init__()
        uic.loadUi('main.ui', self)
        if not args:
            print('No coordinates to show')
            sys.exit(2)
        self.ll = args[0][0]
        self.delta = args[0][1]
        self.setFixedSize(800, 600)
        self.radioButton_1.setChecked(True)
        self.radioButton_1.toggled.connect(self.onClicked)
        self.radioButton_2.toggled.connect(self.onClicked)
        self.radioButton_3.toggled.connect(self.onClicked)
        self.l = 'map'
        self.getImage()
        self.initUi()

    def onClicked(self):
        if self.radioButton_1.isChecked():
            self.l = 'map'
        if self.radioButton_2.isChecked():
            self.l = 'sat'
        if self.radioButton_3.isChecked():
            self.l = 'sat,skl'
        self.getImage()
        self.initUi()

    def getImage(self):
        api_server = "http://static-maps.yandex.ru/1.x/"
        params = {
            "ll": ",".join(self.ll),
            "spn": ",".join([self.delta, self.delta]),
            "l": self.l
        }
        response = requests.get(api_server, params=params)

        if not response:
            print("Ошибка выполнения запроса.")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUi(self):
        self.pixmap = QPixmap(self.map_file)
        self.image.move(0, 0)
        self.image.resize(800, 600)
        self.image.setPixmap(self.pixmap)

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow(get_cords())
    mw.show()
    sys.exit(app.exec())
