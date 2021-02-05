import sys
import os
import argparse

import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel


def get_cords():
    try:
        parser = argparse.ArgumentParser(description='set coordinates for program')
        parser.add_argument('lon', nargs=1, type=float, metavar='LON')
        parser.add_argument('lat', nargs=1, type=float, metavar='LAT')
        args = parser.parse_args()
        cords = tuple(map(lambda x: str(x), args.lon + args.lat))
        return cords
    except Exception as e:
        print(e)
        sys.exit(2)


class MainWindow(QMainWindow):
    def __init__(self, ll):
        super().__init__()
        uic.loadUi('main.ui', self)
        if not ll:
            print('No coordinates to show')
            sys.exit(2)
        self.ll = ll
        self.setFixedSize(800, 600)
        self.getImage()
        self.initUi()

    def getImage(self):
        api_server = "http://static-maps.yandex.ru/1.x/"

        delta = "0.02"

        params = {
            "ll": ",".join(self.ll),
            "spn": ",".join([delta, delta]),
            "l": "map"
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