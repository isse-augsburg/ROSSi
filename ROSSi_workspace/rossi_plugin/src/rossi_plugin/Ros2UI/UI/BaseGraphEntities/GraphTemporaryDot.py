from PyQt5 import QtGui
from PyQt5.QtCore import QRectF, QPointF, QSizeF
from PyQt5.QtWidgets import QGraphicsItem

from ..BaseGraphEntities.AbstractGraphEntity import AbstractGraphEntity, Sticky
from ..BaseGraphEntities.AbstractGraphPortEntity import Connect


class GraphTemporaryDot(AbstractGraphEntity, Sticky):
    radius: float
    visible: bool = True

    def __init__(self, parent: 'GraphLine', x: float, y: float, radius: float = 3.0):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setX(x)
        self.setY(y)
        self.radius = radius

    def boundingRect(self):
        return QRectF(QPointF(-self.radius, -self.radius), QSizeF(self.radius*2, self.radius*2))

    def paint(self, painter, option, widget):
        if self.visible:
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 1))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
            painter.drawEllipse(QPointF(0, 0), self.radius, self.radius)

    def mouseMoveEvent(self, event):
        dx = event.pos().x() - event.lastPos().x()
        dy = event.pos().y() - event.lastPos().y()

        self.setX(self.x() + dx)
        self.setY(self.y() + dy)
        if self.parentItem() is not None:
            self.parentItem().update()
        self.scene().update()  # TODO remove and get rid of the fragments properly

    def mouseReleaseEvent(self, mouse_event):
        #check if over connectable
        for child in self.scene().items(self.scenePos()):
            if isinstance(child, Connect):
                if child.isConnectable():
                    child.connect(self.parentItem().source)
                    self.setVisible(False)
                    self.parentItem().connect(child)
                    break
        self.setSelected(False)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super(GraphTemporaryDot, self).mousePressEvent(event)

    def move(self, dx: float, dy: float):
        if self.isVisible():
            self.setX(self.x() + dx)
            self.setY(self.y() + dy)
