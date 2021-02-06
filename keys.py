def keyPressEvent(self, event):
    if event.key() == Qt.Key_PageUp:
        self.spn1 -= 1
        self.spn2 -= 1
    elif event.key() == Qt.Key_PageDown:
        self.spn1 += 1
        self.spn2 += 1
    elif event.key() == Qt.Key_Left:
        self.ll2 += 0.01
    elif event.key() == Qt.Key_Right:
        self.ll2 -= 0.01
    elif event.key() == Qt.Key_Up:
        self.ll1 -= 0.01
    elif event.key() == Qt.Key_Down:
        self.ll1 += 0.01


# строка http состоит из нескольких строк: code + '//' + adress + '/' + x + '/?ll=' + ll1 + ll2 + '&spn=' + 'spn1' + 'spn2' + '&l=' + type