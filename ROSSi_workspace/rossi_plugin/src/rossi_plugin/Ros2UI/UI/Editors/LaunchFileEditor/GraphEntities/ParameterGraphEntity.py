import typing
from typing import Dict

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QRectF
from PyQt5.QtWidgets import QGraphicsItem

from ....UIElements.DialogWindow import OptionParameter, OptionsWindow
from ....BaseGraphEntities.AbstractGraphEntity import DataObject
from ....BaseGraphEntities.AbstractGraphPortEntity import Connect
from ....BaseGraphEntities.GraphEntryPort import GraphEntryPort
from ....BaseGraphEntities.StandartGraphEntity import StandartGraphEntity


class ParameterGraphEntity(StandartGraphEntity):
    deg: float = 180.0
    radius: float = 5.0
    name: str = None
    hover: bool = False
    disabled: bool = True

    port: GraphEntryPort

    def __init__(self, x: float, y: float, width: float, height: float, parent: QGraphicsItem = None):
        super(ParameterGraphEntity, self).__init__(parent, -1, x, y, width, height)
        self.setX(x)
        self.setY(y)
        self.width = width
        self.height = height

        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setAcceptHoverEvents(True)

        self.port = GraphEntryPort(self, 0, self.height / 2)
        self.port.add_connect_observer(self.on_port_connect_event)

    def on_port_connect_event(self, connected: Connect):
        if connected is None:
            self.disabled = True
        else:
            self.disabled = False
            OptionsWindow([OptionParameter("parameter name", self.name, self.setName)])

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def getText(self):
        if self.port.connected_to is not None:
            return "inherited"
        else:
            return "not set"

    def paint(self, painter, option, widget):
        self.port.setVisible(True)
        if self.hover:
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 0))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(250, 250, 250)))
            painter.drawRect(2, 2, self.width - 4, self.height - 4)
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0), 2)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        painter.setPen(pen)

        if self.disabled is False:
            # draw text
            painter.drawText(QRectF(0, 0, self.width / 2, self.height), QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter,
                             self.name if self.name is not None else ":")
            painter.drawText(QRectF(self.width / 2, 0, self.width/2, self.height),
                             QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter, "inherited")
        else:
            painter.drawText(QRectF(0, 0, self.width, self.height), QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter,
                             self.name + " : " + self.getText() if self.name else "drag sth here to create param")

    def setName(self, name: str):
        self.name = name

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.parentItem().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.parentItem().mousePressEvent(event)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.parentItem().mouseMoveEvent(event)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hover = True
        super(ParameterGraphEntity, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hover = False

    def onRemoveEvent(self):
        self.parentItem().onRemoveEvent()

    def toCode(self, intendLevel: int = 0) -> str:
        intend = "\t" * intendLevel
        if not self.disabled:
            if self.port.connected_to is not None and self.port.connected_to.getValue() is not None:
                return intend + "\"" + self.name + "\": " + self.port.connected_to.getValue() + ",\n"
            else:
                return ""
        else:
            return ""

    def _toDict(self) -> typing.Dict:
        ret = {
            "name": self.name,
            "disabled": self.disabled,
            "port": self.port._toDict()
        }
        return ret

    def getData(self) -> DataObject:
        pass

    @staticmethod
    def getObjectFromData(data: DataObject) -> 'StandartGraphEntity':
        pass

    def getProperties(self):
        pass

    @staticmethod
    def fromJson(json: Dict) -> 'StandartGraphEntity':
        pass