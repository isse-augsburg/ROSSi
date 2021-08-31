from typing import Dict

from PyQt5 import QtCore
from PyQt5.QtCore import QRectF
from PyQt5.QtWidgets import QGraphicsItem

from ....BaseGraphEntities.GraphMultipleEntryPort import GraphMultipleEntryPort
from .....UI.Editors.LiveDiagram.GraphEntities.RosRunningNode import RosRunningNode
from ....BaseGraphEntities.AbstractGraphEntity import DataObject
from ....BaseGraphEntities.GraphEntryPort import GraphEntryPort
from ....BaseGraphEntities.GraphExitPort import GraphExitPort
from ....BaseGraphEntities.StandartGraphEntity import StandartGraphEntity


class RosRunningNodeGraphEntity(StandartGraphEntity):
    original_height: float = 40

    entry: GraphMultipleEntryPort
    exit: GraphExitPort

    def __init__(self, node: RosRunningNode, x: float, y: float, width: float = 222, height: float = 40, parent: QGraphicsItem = None):
        super().__init__(parent, -1, x, y, width, self.original_height)
        self.node = node
        self.exit = GraphExitPort(self, self.width, self.height/2)
        self.entry = GraphMultipleEntryPort(self, 0,  self.height/2)

    def paint(self, painter, option, widget):
        super(RosRunningNodeGraphEntity, self).paint(painter, option, widget)
        painter.drawText(QRectF(0, 0, self.width, self.original_height), QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter, self.node.name)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        try:
            self.parentItem().updateSize()
        except:
            pass

    def getData(self) -> DataObject:
        pass

    def _toDict(self) -> Dict:
        pass

    def toCode(self, intendLevel: int = 0):
        pass

    def getProperties(self):
        pass

    def equals(self, node: 'RosRunningNodeGraphEntity') -> bool:
        return self.node.equals(node.node)
