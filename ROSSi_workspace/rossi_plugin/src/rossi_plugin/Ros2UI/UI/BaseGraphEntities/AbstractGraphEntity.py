import time

import typing

from PyQt5 import QtGui
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget, QGraphicsObject
from argparse import Namespace

class Sticky:
    def move(self, dx: float, dy: float):
        raise NotImplementedError


class AbstractGraphEntity(QGraphicsObject):
    id: int = -1  # used to keep track of connections between two AbstractGraphEntities exported to a JSON

    def __init__(self, parent: QGraphicsItem, id: int = -1):
        super(AbstractGraphEntity, self).__init__(parent=parent)
        self.id = id
        if self.id is -1:
            self.id = int(time.time() * 1000)  # set the id to current millis since epoch thingy
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

    def boundingRect(self):
        raise NotImplementedError

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
        raise NotImplementedError

    def onRemoveEvent(self):
        pass  # To be overridden


# helper class to store key value pairs
# TODO use from argparse import Namespace
class DataObject:
    def __init__(self, key: str, values: dict):
        self.key = key
        self.values = values


