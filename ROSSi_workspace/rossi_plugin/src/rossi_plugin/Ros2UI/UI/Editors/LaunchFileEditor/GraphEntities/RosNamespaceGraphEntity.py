from typing import List, Dict

from PyQt5 import QtCore
from PyQt5.QtCore import QRectF, QPointF

from ....UIElements.DialogWindow import OptionParameter
from ....BaseGraphEntities.AbstractGraphEntity import DataObject
from ....BaseGraphEntities.AbstractGraphPortEntity import Connect
from ....BaseGraphEntities.GraphEntryPort import GraphEntryPort
from ....BaseGraphEntities.ResizableGraphEntity import ResizableGraphEntity
from .....utils import fullname


class RosNamespaceGraphEntity(ResizableGraphEntity):
    namespaceName: str
    port: GraphEntryPort

    def __init__(self, x: float, y: float, width: float, height: float, parent=None, dragable=False, namespaceName: str="default", id: int = -1):
        super(RosNamespaceGraphEntity, self).__init__(x, y, width, height, parent=parent, id=id)
        self.namespaceName = namespaceName
        self.dragable = dragable
        self.setZValue(-10)

        self.exportable = True
        self.port = GraphEntryPort(self, 0, 10)
        self.port.add_connect_observer(self.on_port_connect_event)

        self.displayName: str = namespaceName

    def on_port_connect_event(self, connected_to: Connect):
        if self.port.connected_to is None:
            self.displayName = self.namespaceName
        else:
            self.displayName = "inherited"

    def paint(self, painter, option, widget):
        super(RosNamespaceGraphEntity, self).paint(painter, option, widget)
        painter.drawText(QRectF(0, 0, self.width, self.height), QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft, self.displayName)

    oldpos: QPointF = None

    def mouseMoveEvent(self, mouseEvent):
        if self.handleSelected is not None and not self.dragable:
            self.interactiveResize(mouseEvent.pos())
            if self.oldpos is not None:
                dx = self.x() - self.oldpos.x()
                dy = self.y() - self.oldpos.y()
                for child in self.childItems():
                    child.setY(child.y() - dy)
                    child.setX(child.x() - dx)
        else:
            for child in self.childItems():
                if child is not self.port:
                    child.mouseMoveEvent(mouseEvent)
            super(RosNamespaceGraphEntity, self).mouseMoveEvent(mouseEvent)
        self.oldpos = self.pos()

    def getData(self):
        key = fullname(self)
        values = {
            "namespaceName": self.namespaceName
        }
        self.data = DataObject(key, values)
        return self.data

    @staticmethod
    def getObjectFromData(data: DataObject) -> 'StandartGraphEntity':
        item = RosNamespaceGraphEntity(0, 0, data.values["width"], data.values["height"],
                                       namespaceName=data.values["namespaceName"])
        return item

    def toCode(self, intendLevel: int = 0, innercode: List[str] = []):
        intend = "\t" * intendLevel
        imports = [
            "from launch.actions import GroupAction",
            "from launch_ros.actions import PushRosNamespace"
        ]
        ret = [
            intend + "GroupAction([",
            intend + "\t" + "PushRosNamespace("+self._code_from_port()+"),",
        ]
        ret.extend(innercode)
        ret.append(intend + "]),")
        return ret, imports
    #https://github.com/ros2/launch_ros/issues/43

    def _code_from_port(self) -> str:
        if self.port.connected_to is not None:
            return self.port.connected_to.getValue()
        else:
            return "'"+self.namespaceName+"'"

    def _toDict(self) -> Dict:
        ret = {
            "name": self.namespaceName,
            "port": self.port._toDict()
        }
        return ret

    def setNamespaceName(self, name: str):
        self.namespaceName = name.replace(" ", "_")

    def getProperties(self):
        if self.port.connected_to is None:
            return [OptionParameter("name", self.namespaceName, self.setNamespaceName)]
        else:
            return []

    def onRemoveEvent(self):
        pass

    def onResize(self):
        super(RosNamespaceGraphEntity, self).onResize()
        self.port.setX(0)
        self.port.setY(10)
        self.update(self.boundingRect())

    @staticmethod
    def fromJson(json: Dict) -> 'StandartGraphEntity':
        name = RosNamespaceGraphEntity(
            json["x"],
            json["y"],
            json["width"],
            json["height"],
            id=json["id"],
            namespaceName=json["name"],
        )
        name.port.has_to_connect_to_id = json["port"]["connected_to"]
        return name