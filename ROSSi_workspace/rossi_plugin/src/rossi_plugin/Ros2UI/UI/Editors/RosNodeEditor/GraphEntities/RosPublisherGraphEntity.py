from typing import Dict, Tuple, List

from PyQt5 import QtCore
from PyQt5.QtCore import QRectF

from .CodeHolder import CodeHolder
from .PythonFunctionGraphEntity import PythonFunctionGraphEntity
from .....utils import fullname
from .....Representations.Ros2Representations.RosTopic import RosPublisher
from ....BaseGraphEntities.AbstractGraphEntity import DataObject
from ....BaseGraphEntities.StandartGraphEntity import StandartGraphEntity
from ....UIElements.DialogWindow import OptionParameter, SelectionParameter
from ..utils import getAllTopics, getAllFieldsOfTopic


class RosPublisherGraphEntity(StandartGraphEntity, CodeHolder):


    def __init__(self, x: float, y: float, width: float, height: float, parent=None, id: int = -1, isPreview=False):
        super(RosPublisherGraphEntity, self).__init__(parent, id, x, y, width, height)
        self.exportable = True
        self.publisher = RosPublisher("topic", "type")
        self.isPreview = isPreview
        self.buffersize = 10
        self.hertz = 20
        # self.publish = PythonFunctionGraphEntity(x + width + 30, y, 200, 50, self)

        #if not isPreview:
        #    self.exit_port = GraphExitPort(self, self.width, self.height / 2)
        #    self.exit_port.id = self.id
        #    self.pub_function = PythonFunctionGraphEntity(x + width + 30, y, 200, 50, self)
        #    self.pub_function.port.connect(self.exit_port, False)
        #    self.exit_port.drawConnection(self.pub_function.port, removable=False)
        #    self.setName("publisher")
        #else:
        self.name: str = "publisher"


    def getData(self) -> DataObject:
        key = fullname(self)
        values = {
            "name": self.name,
            "hertz": self.hertz,
            "topic_name": self.publisher.topic.name,
            "topic_type": self.publisher.topic.msg_type
        }
        self.data = DataObject(key, values)
        return self.data

    @staticmethod
    def getObjectFromData(data: DataObject) -> 'StandartGraphEntity':
        item = RosPublisherGraphEntity(0, 0, data.values["width"], data.values["height"])
        item.name = data.values["name"]
        return item

    def _toDict(self) -> Dict:
        ret = {
            "name": self.name,
            "hertz": self.hertz,
            "topic_name": self.publisher.topic.name,
            "topic_type": self.publisher.topic.msg_type
        }
        return ret

    def toCode(self, intendLevel: int = 0):
        intend = "\t" * intendLevel
        ret = [
            intend + "self." + self.name + " = self.create_publisher("+self.publisher.topic.msg_type.split("/")[2]+", '"+self.publisher.topic.name+"', 10)",
            intend + "self.create_timer("+str(self.hertz)+", self."+self.name+"_publish)"
        ]
        cl = self.publisher.topic.msg_type.split("/")
        imports = ["from " + cl[0]+"."+cl[1] + " import " + cl[2]]
        return ret, imports

    # return constructor code, own code, imports
    def getCode(self, intendLevel=0) -> Tuple[List[str], List[str], List[str]]:
        constructor, imports = self.toCode(2)
        method = []

        #if self.pub_function is not None:
        #    method.extend(self.pub_function.toCode(1)[0])
        method.extend(["\tdef " + self.name + "_publish(self):",
                "\t\tpass"])
        return constructor, method, imports

    def paint(self, painter, option, widget):
        super(RosPublisherGraphEntity, self).paint(painter, option, widget)
        painter.drawText(QRectF(0, 0, self.width, self.height/2), QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft, self.name)
        painter.drawText(QRectF(0, self.height/2, self.width, self.height/2), QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft, self.publisher.topic.name)

    def setTopicName(self, name: str):
        self.publisher.topic.name = name

    def setName(self, name: str):
        self.name = name
        #self.pub_function.setName(name+"_publish")
        #self.pub_function.update(self.pub_function.boundingRect())

    def setHertz(self, hertz: int):
        self.hertz = hertz

    def getProperties(self):
        return [OptionParameter("name", self.name, self.setName),
                OptionParameter("hertz", str(self.hertz), self.setHertz),
                OptionParameter("topic name", self.publisher.topic.name, self.setTopicName),
                SelectionParameter(getAllTopics(), self.publisher.topic.msg_type, self.setMsgType)]

    def setMsgType(self, value: str):
        self.publisher.topic.msg_type = value
        print(getAllFieldsOfTopic(value))

    @staticmethod
    def fromJson(json: Dict) -> 'StandartGraphEntity':
        ret = RosPublisherGraphEntity(json["x"],
                                json["y"],
                                json["width"],
                                json["height"],
                                id=json["id"],)
        ret.name = json["name"]
        ret.hertz = json["hertz"]
        ret.publisher.topic.name = json["topic_name"]
        ret.publisher.topic.msg_type = json["topic_type"]
        return ret
