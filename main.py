import sys
import os
import argparse
from PIL import Image
from PIL.ImageQt import ImageQt
import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog
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
        self.initUi(args)

    def initUi(self, args):
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
        self.mark = {}

    def onClicked(self):
        if self.sender().text() == 'Карта':
            self.l = 'map'
        if self.sender().text() == 'Спутник':
            self.l = 'sat'
        if self.sender().text() == 'Гибрид':
            self.l = 'sat,skl'
        self.getImage()

    def search(self):
        text_toponym, ok_pressed = QInputDialog.getText(self, 'Введите объект поиска', 'Что найти на карте?')

        if ok_pressed:
            object = ('+').join(text_toponym.split())
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
                self.search = False
                self.toponym_l.setText(text_toponym)
            else:
                print("Ошибка выполнения запроса:")
                print(geocoder_request)
                print("Http статус:", response.status_code, "(", response.reason, ")")

    def keyPressEvent(self, event):
        try:
            delta = float(self.delta)
            if event.key() == Qt.Key_PageUp:
                if delta * 2 > 90:
                    delta = 90
                else:
                    delta *= 2
            if event.key() == Qt.Key_PageDown:
                if delta / 2 < 0.002:
                    delta = 0.002
                else:
                    delta /= 2
            self.delta = str(delta)

            ll = list(map(float, self.ll))
            k = round(float(self.delta) * 1.4, 5)
            h_k = round(k * 1.7, 5)
            if event.key() == Qt.Key_Up:
                if ll[1] + k > 80:
                    ll[1] = 80
                else:
                    ll[1] += k
            if event.key() == Qt.Key_Right:
                if ll[0] + h_k > 179:
                    ll[0] = -179
                else:
                    ll[0] += h_k
            if event.key() == Qt.Key_Left:
                if ll[0] - h_k < -179:
                    ll[0] = 179
                else:
                    ll[0] -= h_k
            if event.key() == Qt.Key_Down:
                if ll[1] - k < -80:
                    ll[1] = -80
                else:
                    ll[1] -= k
            self.ll = list(map(str, ll))

            self.getImage()
        except Exception as e:
            print('Error: ', e)

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
        self.setImage()

    def setImage(self):
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow(get_cords())
    mw.show()
    sys.exit(app.exec())
