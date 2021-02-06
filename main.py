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
        self.btn_plan.clicked.connect(self.onClicked)
        self.btn_satellite.clicked.connect(self.onClicked)
        self.btn_hybride.clicked.connect(self.onClicked)
        self.search_btn.clicked.connect(self.search)
        self.l = 'map'
        self.search = False
        self.getImage()
        self.initUi()
        self.mark = {}

    def onClicked(self):
        if self.sender().text() == 'Карта':
            self.l = 'map'
        if self.sender().text() == 'Спутник':
            self.l = 'sat'
        if self.sender().text() == 'Гибрид':
            self.l = 'sat,skl'
        self.getImage()
        self.initUi()

    def search(self):
        object = ('+').join(self.adress_edit.text().split())
        apikey = "40d1649f-0493-4b70-98ba-98533de7710b"
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={apikey}&geocode={object}&format=json"
        response = requests.get(geocoder_request)
        if response:
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_coodrinates = toponym["Point"]["pos"]
            self.ll = toponym_coodrinates.split()
            self.search = True
            self.getImage()
            self.initUi()

        else:
            print("Ошибка выполнения запроса:")
            print(geocoder_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")

    def getImage(self):
        api_server = "http://static-maps.yandex.ru/1.x/"
        if self.search:
            params = {
                "ll": ",".join(self.ll),
                "spn": ",".join([self.delta, self.delta]),
                "l": self.l,
                "pt": "{0},pm2dgl".format("{0},{1}".format(self.ll[0], self.ll[1]))
            }
        else:
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
