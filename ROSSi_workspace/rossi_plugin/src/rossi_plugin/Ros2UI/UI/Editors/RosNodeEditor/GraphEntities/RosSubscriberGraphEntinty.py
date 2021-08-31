from typing import Dict, Tuple, List

from PyQt5 import QtCore
from PyQt5.QtCore import QRectF

from .CodeHolder import CodeHolder
from .....utils import fullname
from .....Representations.Ros2Representations.RosTopic import RosSubscriber
from ....BaseGraphEntities.AbstractGraphEntity import DataObject
from ....BaseGraphEntities.StandartGraphEntity import StandartGraphEntity
from ....UIElements.DialogWindow import OptionParameter, SelectionParameter
from ..utils import getAllTopics


class RosSubscriberGraphEntity(StandartGraphEntity, CodeHolder):
    def __init__(self, x: float, y: float, width: float, height: float, parent=None, id: int = -1):
        super(RosSubscriberGraphEntity, self).__init__(parent, id, x, y, width, height)
        self.name: str = ""
        self.subscriber = RosSubscriber("", "")
        self.exportable = True
        # self.callback = PythonFunctionGraphEntity(x + width + 30, y, 200, 50, self)

    def getData(self) -> DataObject:
        key = fullname(self)
        values = {
            "name": self.name
        }
        self.data = DataObject(key, values)
        return self.data

    @staticmethod
    def getObjectFromData(data: DataObject) -> 'StandartGraphEntity':
        item = RosSubscriberGraphEntity(0, 0, data.values["width"], data.values["height"])
        item.name = data.values["name"]
        return item

    def _toDict(self) -> Dict:
        ret = {
            "name": self.name,
            "topic_name": self.subscriber.topic.name,
            "topic_type": self.subscriber.topic.msg_type
        }
        return ret

    def toCode(self, intendLevel: int = 0):
        intend = "\t" * intendLevel
        ret = [
            intend + "self." + self.name + " = self.create_subscription(" + self.subscriber.topic.msg_type.split("/")[
                2] + ",'" + self.subscriber.topic.name + "',self." + self.name + "_callback)",
        ]
        cl = self.subscriber.topic.msg_type.split("/")
        imports = ["from " + cl[0] + "." + cl[1] + " import " + cl[2]]
        return ret, imports

    # return constructor code, own code, imports
    def getCode(self, intendLevel=0) -> Tuple[List[str], List[str], List[str]]:
        constructor, imports = self.toCode(2)
        method = []
        method.extend([
            "\tdef " + self.name + "_callback(self, msg: " + self.subscriber.topic.msg_type.split("/")[2] + ", 10):",
            "\t\tprint(msg)"
        ])

        return constructor, method, imports

    def paint(self, painter, option, widget):
        super(RosSubscriberGraphEntity, self).paint(painter, option, widget)
        painter.drawText(QRectF(0, 0, self.width, self.height / 2), QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft, self.name)
        painter.drawText(QRectF(0, self.height / 2, self.width, self.height / 2),
                         QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft, self.subscriber.topic.name)

    def getProperties(self):
        return [OptionParameter("name", self.name, lambda val: setattr(self, "name", val)),
                OptionParameter("topic name", self.subscriber.topic.name, self.setTopicName),
                SelectionParameter(getAllTopics(), self.subscriber.topic.msg_type, self.setMsgType)]

    def setMsgType(self, value: str):
        self.subscriber.topic.msg_type = value

    def setTopicName(self, value: str):
        self.subscriber.topic.name = value

    @staticmethod
    def fromJson(json: Dict) -> 'StandartGraphEntity':
        ret = RosSubscriberGraphEntity(json["x"],
                                       json["y"],
                                       json["width"],
                                       json["height"],
                                       id=json["id"], )
        ret.name = json["name"]
        ret.subscriber.topic.name = json["topic_name"]
        ret.subscriber.topic.msg_type = json["topic_type"]
        return ret
