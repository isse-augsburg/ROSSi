import typing
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRectF, QPointF, QSizeF, Qt, QLineF
from PyQt5.QtWidgets import QApplication, QGraphicsItem, QWidget

from ..BaseGraphEntities.GraphTemporaryDot import GraphTemporaryDot
from ..BaseGraphEntities.AbstractGraphEntity import AbstractGraphEntity
from ..BaseGraphEntities.AbstractGraphPortEntity import AbstractGraphPortEntity, Connect


class GraphLine(AbstractGraphEntity, Connect):

    source: AbstractGraphPortEntity
    target: AbstractGraphEntity
    connected_to: Connect

    alt_target: GraphTemporaryDot = None
    stroke_width = 2

    def __init__(self, source: 'GraphExitPort', target: AbstractGraphEntity = None, removable: bool = True):
        super().__init__(source)
        self.source = source
        self.removable = removable

        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        if target is not None:
            self.target = target
        else:
            self.alt_target = GraphTemporaryDot(self, self.x(), self.y())
            self.target = self.alt_target

    def boundingRect(self):
        point = QPointF(float(min(0, int(self.target.scenePos().x() - self.scenePos().x()))) - self.stroke_width*4, float(min(0, int(self.target.scenePos().y() - self.scenePos().y()))) - self.stroke_width*4)
        size = QSizeF(abs(self.target.scenePos().x() - self.scenePos().x()) + self.stroke_width*8, abs(self.target.scenePos().y() - self.scenePos().y()) + self.stroke_width*8)
        return QRectF(point, size)

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
        if self.isSelected():
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), self.stroke_width+1))
        else:
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), self.stroke_width))

        for line in self._getLines():
            painter.drawLine(line)

        self.update()

    def _getLines(self) -> typing.List[QLineF]:
        x = 0
        y = 0
        x2 = self.target.scenePos().x() - self.scenePos().x()
        y2 = self.target.scenePos().y() - self.scenePos().y()

        dx = x2 - x
        dy = y2 - y

        ret = []
        if abs(dx) > abs(dy):
            ret.append(QLineF(x, y, x + dx/2, y))
            ret.append(QLineF(x + dx/2, y, x + dx/2, y + dy))
            ret.append(QLineF(x + dx/2, y + dy, x2, y2))
        else:
            if dx > 20:
                ret.append(QLineF(x, y, x + 10, y))
                x += 10
                dx = x2 - x
                ret.append(QLineF(x2, y2, x2 - 10, y2))
                x2 -= 10
                dx -= 10
            ret.append(QLineF(x, y, x, y + dy/2))
            ret.append(QLineF(x, y + dy/2, x + dx, y + dy/2))
            ret.append(QLineF(x + dx, y + dy/2, x2, y2))
        return ret

    def _isCloseToLine(self, pos: QPointF) -> bool:
        for line in self._getLines():
            if self._isOverLine(pos, line):
                return True
        return False

    def _isOverLine(self, pos: QPointF, line: QLineF,  scope: float = 5.0) -> bool:
        return line.x1() - scope < pos.x() < line.x2() + scope and line.y1() - scope < pos.y() < line.y2() + scope

    def mousePressEvent(self, event):
        super(GraphLine, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == QtCore.Qt.AltModifier and self.removable:
                if self._isCloseToLine(event.pos()):
                    self.remove()
                    self.scene().update()  # TODO remove and get rid of fragments properly

    def remove(self):
        if self.target is not self.alt_target:
            self.target.disconnect(self.source)
        self.source.removeLine(self)
        self.setVisible(False)

    def connect(self, port: 'Connect'):
        self.target = port
        self.scene().removeItem(self.alt_target)
        self.alt_target = None

    def disconnect(self, port: 'Connect' = None):
        pass

    def canConnectTo(self, clazz: typing.Type):
        pass

    def isConnectable(self):
        pass
