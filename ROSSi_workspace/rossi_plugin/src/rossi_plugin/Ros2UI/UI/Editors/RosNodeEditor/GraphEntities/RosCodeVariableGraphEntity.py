from typing import Dict


from PyQt5 import QtCore
from PyQt5.QtCore import QRectF

from .....utils import fullname
from ....BaseGraphEntities.AbstractGraphEntity import DataObject
from ....BaseGraphEntities.StandartGraphEntity import StandartGraphEntity


class RosCodeVariableGraphEntity(StandartGraphEntity):
    def __init__(self,  x: float, y: float, width: float, height: float, name: str = "var",  parent=None, id: int = -1):
        super(RosCodeVariableGraphEntity, self).__init__(parent, id, x, y, width, height)
        self.name = name

    def paint(self, painter, option, widget):
        super(RosCodeVariableGraphEntity, self).paint(painter, option, widget)
        painter.drawText(QRectF(0, 0, self.width, self.height/2), QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft, self.name)

    def getData(self) -> DataObject:
        key = fullname(self)
        values = {
            "name": self.name
        }
        self.data = DataObject(key, values)
        return self.data

    @staticmethod
    def getObjectFromData(data: DataObject) -> 'StandartGraphEntity':
        item = RosCodeVariableGraphEntity(0, 0, data.values["width"], data.values["height"])
        item.name = data.values["name"]
        return item

    def _toDict(self) -> Dict:
        pass

    def toCode(self, intendLevel: int = 0):
        pass

    def getProperties(self):
        pass

