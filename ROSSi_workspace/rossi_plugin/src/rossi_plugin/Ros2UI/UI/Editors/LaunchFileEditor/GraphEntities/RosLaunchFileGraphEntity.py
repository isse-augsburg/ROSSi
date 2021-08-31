import os
from typing import Dict, List

from PyQt5 import QtCore
from PyQt5.QtCore import QRectF
from PyQt5.QtWidgets import QGraphicsItem

from .....utils import fullname
from .ParameterGraphEntity import ParameterGraphEntity
from ....BaseGraphEntities.AbstractGraphPortEntity import Connect
from ....UIElements.DialogWindow import OptionParameter
from ....BaseGraphEntities.AbstractGraphEntity import DataObject
from ....BaseGraphEntities.StandartGraphEntity import StandartGraphEntity
from ros2launch.api import print_arguments_of_launch_file, print_a_launch_file


class RosLaunchFileGraphEntity(StandartGraphEntity):
    display_name: str
    namespace: str = None
    parameters: List[ParameterGraphEntity]
    param_height: float = 15
    original_height = 60

    def __init__(self, path: str, packageName: str, x: float, y: float, width: float, height: float,
                 dragable: bool = False, parent: QGraphicsItem = None, id: int = -1, show_parameters=True):
        super().__init__(parent, id, x, y, width, self.original_height)
        self.path = path
        self.packageName = packageName
        self.dragable = dragable

        self.display_name = os.path.basename(path)
        print(print_arguments_of_launch_file(launch_file_path=self.path))
        print_a_launch_file(launch_file_path=self.path)
        self.exportable = True
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

    def _paramsToCode(self, intendLevel: int) -> str:
        ret = []
        for param in self.parameters:
            ret.append(param.toCode(intendLevel))
        retu = ""
        for s in ret:
            retu += s

        return retu

    def paint(self, painter, option, widget):
        super(RosLaunchFileGraphEntity, self).paint(painter, option, widget)
        painter.drawText(QRectF(0, 0, self.width, self.original_height / 3), QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter,
                         "launch file")
        painter.drawText(QRectF(0, self.original_height/3, self.width, self.original_height / 3), QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter,
                         self.packageName)
        painter.drawText(QRectF(0, self.original_height / 3 * 2, self.width, self.original_height / 3),
                         QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter, self.display_name)

    def getData(self):
        key = fullname(self)
        values = {
            "path": self.path,
            "packageName": self.packageName,
            "displayname": self.display_name
        }
        self.data = DataObject(key, values)
        return self.data

    @staticmethod
    def getObjectFromData(data: DataObject) -> 'StandartGraphEntity':
        item = RosLaunchFileGraphEntity(data.values["path"], data.values["packageName"], 0 , 0,
                                       data.values["width"], data.values["height"], dragable=False)
        return item

    def toCode(self, intendLevel: int = 0):
        intend = "\t" * intendLevel
        imports = [
            "from launch.actions import IncludeLaunchDescription",
            "from launch.launch_description_sources import PythonLaunchDescriptionSource",
            "from launch.substitutions import ThisLaunchFileDir",
        ]
        args = self._paramsToCode((intendLevel+2))
        ret = [
            intend + "IncludeLaunchDescription(",
            intend + "\t" + "PythonLaunchDescriptionSource(['" + self.path + "']),",
            intend + "\t" + "launch_arguments={\n" + args,
            intend + "\t" + "}.items(),",
            intend + "),"
        ]
        return ret, imports

    def _toDict(self) -> Dict:
        ret = {
            "path": self.path,
            "packageName": self.packageName,
            "parameters": self._paramsToDict()
        }
        return ret

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
        return [OptionParameter("display name", self.display_name, self.setDisplayName)]

    def onRemoveEvent(self):
        pass

    @staticmethod
    def fromJson(json: Dict) -> 'StandartGraphEntity':
        launch = RosLaunchFileGraphEntity(
            json["path"],
            json["packageName"],
            json["x"],
            json["y"],
            json["width"],
            json["height"],
            id=json["id"],
            show_parameters=False
        )
        for item in json["parameters"]:
            param = launch.add_new_parameter()
            param.name = item["name"]
            param.disabled = item["disabled"]
            param.port.has_to_connect_to_id = item["port"]["connected_to"]
        launch.add_new_parameter()
        return launch
