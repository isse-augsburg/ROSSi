import typing
from abc import abstractmethod, ABC

from PyQt5 import QtGui
from PyQt5.QtWidgets import QGraphicsItem, QWidget

from ..BaseGraphEntities.AbstractGraphEntity import AbstractGraphEntity


class Connect:
    connected_to: typing.Union['Connect', 'AbstractGraphPortEntity', 'ValueHolder'] = None

    def isConnected(self):
        return self.connected_to is not None

    @abstractmethod
    def connect(self, port: typing.Union['Connect', 'AbstractGraphPortEntity', 'ValueHolder']):
        raise NotImplementedError

    @abstractmethod
    def disconnect(self, port: 'Connect' = None):
        raise NotImplementedError

    @abstractmethod
    def canConnectTo(self, clazz: typing.Type):
        raise NotImplementedError

    @abstractmethod
    def isConnectable(self):
        raise NotImplementedError


class ValueHolder:
    def getValue(self):
        raise NotImplementedError


class AbstractGraphPortEntity(AbstractGraphEntity):
    def __init__(self, parent: QGraphicsItem, x: float, y: float):
        super().__init__(parent)
        self.setX(x)
        self.setY(y)
        self.setAcceptHoverEvents(True)

    @abstractmethod
    def boundingRect(self):
        raise NotImplementedError

    @abstractmethod
    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
        raise NotImplementedError


