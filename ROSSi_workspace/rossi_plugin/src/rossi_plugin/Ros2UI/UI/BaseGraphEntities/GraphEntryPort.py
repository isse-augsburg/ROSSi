import math
import typing

from PyQt5 import QtGui
from PyQt5.QtCore import QRectF
from PyQt5.QtWidgets import QGraphicsItem

from ..BaseGraphEntities.AbstractGraphPortEntity import AbstractGraphPortEntity, Connect


# A port that you can drag a line onto
class GraphEntryPort(AbstractGraphPortEntity, Connect):
    radius: int
    deg: float
    has_to_connect_to_id: int = -1
    connect_observers: typing.List[typing.Callable[[Connect], None]]

    def __init__(self, parent, x: float, y: float, deg: float = 180, radius=8):
        super().__init__(parent, x, y)
        self.deg = deg
        self.radius = radius
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.connect_observers = []

    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, self.radius*2, self.radius*2)

    # makes a '>' shaped thing
    def paint(self, painter, option, widget):
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0), 2)
        painter.setPen(pen)
        x2 = math.cos(math.radians(self.deg + 45)) * self.radius
        y2 = math.sin(math.radians(self.deg + 45)) * self.radius
        painter.drawLine(-1, 0, -1 + x2, y2)
        x2 = math.cos(math.radians(self.deg - 45)) * self.radius
        y2 = math.sin(math.radians(self.deg - 45)) * self.radius
        painter.drawLine(0, 0, -1 + x2, y2)

    def canConnectTo(self, clazz: typing.Type):
        return True

    def add_connect_observer(self, callback: typing.Callable[[Connect], None]) -> None:
        self.connect_observers.append(callback)

    def connect(self, port: typing.Union['Connect', 'AbstractGraphPortEntity', 'ValueHolder'], fire_events: bool = True) -> None:
        if self.canConnectTo(type(port)) and self.isConnectable():
            self.connected_to = port
            #print(self.connected_to.id, self.connected_to, self.connected_to.getValue())
            if fire_events:
                for callback in self.connect_observers:
                    callback(port)

    def disconnect(self, port: 'Connect' = None):
        self.connected_to = None
        for callback in self.connect_observers:
            callback(None)

    def isConnectable(self):
        return not self.isConnected()

    def getValue(self) -> str:
        if self.connected_to is not None:
            return self.connected_to.getValue()
        else:
            return None

    def _toDict(self) -> typing.Dict:
        ret = {
            "connected_to": self.connected_to.id if self.connected_to else -1
        }
        return ret
