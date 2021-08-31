import typing

from PyQt5 import QtGui
from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtWidgets import QGraphicsItem, QWidget

from ..BaseGraphEntities.GraphLine import GraphLine
from ..BaseGraphEntities.AbstractGraphPortEntity import AbstractGraphPortEntity, ValueHolder


# a port that you can drag n lines from
class GraphExitPort(AbstractGraphPortEntity, ValueHolder):
    radius: float
    name: str
    multiplicity: int = -1  # -1 = n
    lines: typing.List[GraphLine]
    new_line: GraphLine = None

    def __init__(self, parent: typing.Union[QGraphicsItem, ValueHolder], x, y, radius: float = 3.0):
        super().__init__(parent, x, y)
        self.radius = radius
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.lines  = []

    def boundingRect(self):
        return QRectF(-self.radius/2, -self.radius/2, self.radius*2, self.radius*2)

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 1))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        painter.drawEllipse(QPointF(0, 0), self.radius, self.radius)

    def mousePressEvent(self, event):
        if len(self.lines) < self.multiplicity or self.multiplicity is -1:
            self.new_line = GraphLine(self)
            self.lines.append(self.new_line)
            self.setSelected(False)

    def mouseMoveEvent(self, event):
        if self.new_line is not None and self.new_line.alt_target is not None:
            self.new_line.alt_target.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        if self.new_line is not None and self.new_line.alt_target is not None:
            self.new_line.alt_target.mouseReleaseEvent(event)
        self.new_line = None

    def dragMoveEvent(self, event):
        super().dragMoveEvent(event)

    def removeLine(self, line: GraphLine):
        self.lines.remove(line)

    def onRemoveEvent(self):
        pass

    def getValue(self):
        return self.parentItem().getValue()

    def drawConnection(self, target: AbstractGraphPortEntity, removable: bool = True):
        print("draw line to ", target)
        self.lines.append(GraphLine(self, target, removable))

    def removeConnection(self, target: AbstractGraphPortEntity):
        for line in self.lines:
            if line.target is target:
                line.remove()


