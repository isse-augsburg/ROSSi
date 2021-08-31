from PyQt5.QtCore import QRectF
from PyQt5.QtWidgets import QGraphicsItem, QApplication, QGraphicsScene, QGraphicsView, QGraphicsRectItem


class Example2:
    fewfwe = True
    wefew = True
    few = False
    foo = True
    few = False

import sys
from PyQt5 import QtGui

class Node(QGraphicsItem):
    def __init__(self, x: float, y:float):
        QGraphicsItem.__init__(self)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setX(x)
        self.setY(y)
    def boundingRect(self):
        return QRectF(0, 0, 10, 10)

    def paint(self, painter, option, widget):
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 1))
        painter.drawRect(0, 0, 10, 10)
        print(self.x(), self.y())

app = QApplication(sys.argv)

scene = QGraphicsScene()
scene.addText("test")

scene.addItem(Node(40,40))

view = QGraphicsView(scene)
view.show()

sys.exit(app.exec_())