from PyQt5.QtCore import QRectF, Qt, QPointF
from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView


class InteractiveGraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(InteractiveGraphicsScene, self).__init__(parent)

    def dragMoveEvent(self, event):
        pass

    def dragEnterEvent(self, event):
        pass

    def dropEvent(self, event):
        pass
