import os
from typing import Dict, Callable, Tuple, List

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QRectF

from .CodeHolder import CodeHolder
from .RosPublisherGraphEntity import RosPublisherGraphEntity
from ....UIElements.DialogWindow import OptionParameter, DoneParameter
from ....BaseGraphEntities.AbstractGraphEntity import DataObject
from ....BaseGraphEntities.StandartGraphEntity import StandartGraphEntity

from pathlib import Path


class RosBaseNodeGraphEntityNew(StandartGraphEntity, CodeHolder):
    def __init__(self, x: float, y: float, width: float, height: float, parent=None, id: int = -1):
        super(RosBaseNodeGraphEntityNew, self).__init__(parent, id, x, y, width, height)
        self.exportable = True
        self.name = "node_name"

    def getData(self) -> DataObject:
        return None

    def _toDict(self) -> Dict:
        ret = {
            "name": self.name
        }
        return ret

    def toCode(self, intendLevel: int = 0):
        intend = "\t" * intendLevel
        imports = [
            "import rclpy",
            "from rclpy.node import Node"
        ]
        ret = [intend + "class " + self.name+"(Node):",
               intend + "",
               intend + "\tdef __init__(self):",
               intend + "\t\tsuper().__init__('" + self.name + "')",
               ]
        return ret, imports

    def paint(self, painter, option, widget):
        super(RosBaseNodeGraphEntityNew, self).paint(painter, option, widget)
        painter.drawText(QRectF(0, 0, self.width, self.height), QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft, self.name)

    def setName(self, name: str):
        self.name = name

    def getCode(self, intendLevel=0) -> Tuple[List[str], List[str], List[str]]:
        pass

    def getProperties(self):
        ret = [OptionParameter("name", self.name, self.setName)]
        return ret

    @staticmethod
    def getObjectFromData(data: DataObject) -> 'StandartGraphEntity':
        pass

    @staticmethod
    def fromJson(json: Dict) -> 'StandartGraphEntity':
        ret = RosBaseNodeGraphEntityNew(json["x"],
                                      json["y"],
                                      json["width"],
                                      json["height"],
                                      id=json["id"], )
        ret.name = json["name"]
        return ret
