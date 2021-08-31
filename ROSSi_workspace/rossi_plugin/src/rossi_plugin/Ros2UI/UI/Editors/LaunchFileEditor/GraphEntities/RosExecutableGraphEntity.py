from typing import Dict, List

from PyQt5 import QtCore
from PyQt5.QtCore import QRectF
from PyQt5.QtWidgets import QGraphicsItem

from .ParameterGraphEntity import ParameterGraphEntity
from .....utils import fullname
from .....Representations.Ros2Representations.RosPackage import RosExecutable, RosPackage
from ....UIElements.DialogWindow import OptionParameter
from ....BaseGraphEntities.AbstractGraphEntity import DataObject
from ....BaseGraphEntities.AbstractGraphPortEntity import Connect
from ....BaseGraphEntities.StandartGraphEntity import StandartGraphEntity


class RosExecutableGraphEntity(StandartGraphEntity):
    display_name: str
    namespace: str
    parameters: List[ParameterGraphEntity]
    param_height: float = 15
    original_height: float = 40

    def __init__(self, exe: RosExecutable, x: float, y: float, width: float = 222, height: float = 40, dragable: bool = False, display_name: str = "", parent: QGraphicsItem = None, id: int = -1, show_parameters=True):
        super().__init__(parent, id, x, y, width, self.original_height)
        self.exe = exe
        self.dragable = dragable
        self.display_name = exe.displayName if display_name is "" else display_name

        #NodeInfo(self.exe.package.name, self.exe.executableName).get_topics(self.call)

        self.exportable = True
        self.namespace = None
        self.parameters = []

        if show_parameters:
            self.add_new_parameter()

    def add_new_parameter(self) -> ParameterGraphEntity:
        param = ParameterGraphEntity(0, self.height, self.width, self.param_height, self)
        param.disabled = True
        param.port.add_connect_observer(self.on_port_connect_event)
        self.parameters.append(param)
        self.height += self.param_height
        return param

    def on_port_connect_event(self, connected: Connect):
        if connected is None:
            pass
        else:
            for param in self.parameters:
                print(param.port.connected_to)
                if param.disabled and param.port.connected_to is None and param.name is None:
                    return
            self.add_new_parameter()

    def call(self, info: str):
        print(info)

    def paint(self, painter, option, widget):
        super(RosExecutableGraphEntity, self).paint(painter, option, widget)
        painter.drawText(QRectF(0, 0, self.width, self.original_height/2), QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter, self.display_name)
        painter.drawText(QRectF(0, self.original_height/2, self.width, self.original_height/2), QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter, self.exe.package.name)

    def getData(self):
        key = fullname(self)
        values = {
            "executable": self.exe,
            "displayname": self.display_name
        }
        self.data = DataObject(key, values)
        return self.data

    @staticmethod
    def getObjectFromData(data: DataObject) -> 'StandartGraphEntity':
        item = RosExecutableGraphEntity(data.values["executable"], 0, 0, data.values["width"],
                                        data.values["height"], dragable=False)
        return item

    def __namespacehelper(self) -> str:
        if self.namespace is not None and self.namespace is not "":
            return "namespace='" + self.namespace + "',"
        return ""

    def toCode(self, intendLevel: int = 0):
        intend = "\t" * intendLevel
        imports = [
            "from launch_ros.actions import Node"
        ]
        ret = [
            intend + "Node(",
            intend + "\t" + "package='"+self.exe.package.name+"',",
            intend + "\t" + self.__namespacehelper(),
            intend + "\tnode_executable='" + self.exe.executableName + "',",
            intend + "\tnode_name='" + self.display_name + "',",
            intend + "\toutput='screen',",
            intend + "\tparameters=[{\n" + self._paramsToCode(intendLevel+2),
            intend + "\t}],",
            intend + "),"
        ]
        return ret, imports

    def _toDict(self) -> Dict:
        ret = {
            "name": self.display_name,
            "executable": self.exe.executableName,
            "packageName": self.exe.package.name,
            "parameters": self._paramsToDict()
        }
        return ret

    def _paramsToCode(self, intendLevel) -> str:
        ret = []
        for param in self.parameters:
            ret.append(param.toCode(intendLevel))
        retu = ""
        for s in ret:
            retu += s

        return retu

    def _paramsToDict(self):
        ret = []
        for param in self.parameters:
            if param.disabled is False:
                ret.append(param._toDict())
        return ret

    def setDisplayName(self, name: str):
        self.display_name = name

    def setNameSpace(self, namespace):
        self.namespace = namespace

    def getProperties(self):
        ret = [OptionParameter("display name", self.display_name, self.setDisplayName)]
        for param in self.parameters:
            ret.append(OptionParameter("parameter name", param.name, param.setName))

        return ret

    def onRemoveEvent(self):
        pass

    @staticmethod
    def fromJson(json: Dict) -> 'StandartGraphEntity':
        exe = RosExecutableGraphEntity(
            RosExecutable(json["executable"], json["executable"], RosPackage(json["packageName"])),
            json["x"],
            json["y"],
            json["width"],
            json["height"],
            id=json["id"],
            display_name=json["name"],
            show_parameters=False
        )
        for item in json["parameters"]:
            param = exe.add_new_parameter()
            param.name = item["name"]
            param.disabled = item["disabled"]
            param.port.has_to_connect_to_id = item["port"]["connected_to"]
        exe.add_new_parameter()
        return exe

