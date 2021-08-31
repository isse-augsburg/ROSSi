from typing import Dict, List

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QRectF
from PyQt5.QtWidgets import QGraphicsItem

from .RosRunningNodeGraphEntity import RosRunningNodeGraphEntity
from ...RosNodeEditor.utils import getAllFieldsOfTopic
from ....BaseGraphEntities.GraphMultipleEntryPort import GraphMultipleEntryPort
from ....UIElements.DialogWindow import DisplayParameter
from .....utils import dynamic_import_ros2_msg
from .....Representations.Ros2Representations.RosTopic import RosTopic
from ....BaseGraphEntities.AbstractGraphEntity import DataObject
from ....BaseGraphEntities.GraphExitPort import GraphExitPort
from ....BaseGraphEntities.StandartGraphEntity import StandartGraphEntity


class RosRunningTopicGraphEntity(StandartGraphEntity):
    original_height: float = 70

    entry: GraphMultipleEntryPort
    exit: GraphExitPort

    def __init__(self, topic: RosTopic, x: float, y: float, width: float = 70, height: float = 70, parent: QGraphicsItem = None, node=None):
        super().__init__(parent, -1, x, y, width, self.original_height)
        self.exit = GraphExitPort(self, self.width, self.height/2)
        self.entry = GraphMultipleEntryPort(self, 0,  self.height/2)
        self.topic = topic
        self.node = node
        self.param = DisplayParameter("")
        self.msg_dic = {}
        self.createSubscriber()

    def createSubscriber(self):
        try:
            #print(self.topic.msg_type[0])
            klass = dynamic_import_ros2_msg(self.topic.msg_type[0])
            #print(klass)
            self.msg_dic = getAllFieldsOfTopic(self.topic.msg_type[0])
            self.node.create_subscription(klass, self.topic.name, self.callback, 10)
            o = klass()
            # print("--------------____>", klass)
        except:
            self.param.setText("couldn't find class of msg type...")

    def callback(self, msg):
        if self.param is not None:
            self.last_msg = msg
            t = self.pretty(self.msg_dic, self.last_msg)
            self.param.setText("couldn't find class of msg type " if t == "" else t)

    def pretty(self, d, msg, indent=0) -> str:
        ret = ""
        for key, value in d.items():
            if isinstance(value, dict):
                ret += '\t' * indent + str(key) + "\n"
                ret += self.pretty(value, msg, indent + 1) + "\n"
            else:
                if hasattr(msg, key):
                    t = '\t' * (indent + 1) + str(key) + " ("+str(value)+")" + ": " + str(getattr(msg, key)) + "\n"
                    ret += t#('\n'+'\t' * (indent + 2)).join(l for line in t.splitlines() for l in textwrap.wrap(t, width=100))
        return ret

    def paint(self, painter, option, widget):
        super(RosRunningTopicGraphEntity, self).paint(painter, option, widget)
        painter.drawText(QRectF(0, 0, self.width, self.original_height), QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter, self.topic.name)

    def getData(self) -> DataObject:
        pass

    def _toDict(self) -> Dict:
        pass

    def toCode(self, intendLevel: int = 0):
        pass

    def getProperties(self):
        return [self.param]

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
        super(RosRunningTopicGraphEntity, self).mouseDoubleClickEvent(event)
        self.param = DisplayParameter("")

    def equals(self, topic: 'RosRunningTopicGraphEntity') -> bool:
        return self.topic.equals(topic.topic)

    def addPublisher(self, node: RosRunningNodeGraphEntity):
        self.entry.connect(node.exit)
        node.exit.drawConnection(self.entry)

    def addSubscriber(self, node: RosRunningNodeGraphEntity):
        node.entry.connect(self.exit)
        self.exit.drawConnection(node.entry)

    def removePublisher(self, node: RosRunningNodeGraphEntity):
        node.exit.removeConnection(self.entry)
        self.entry.disconnect(node.exit)

    def removeSubscriber(self, node: RosRunningNodeGraphEntity):
        node.entry.disconnect(self.exit)
        self.exit.removeConnection(node.entry)

    def getPublishers(self) -> List[RosRunningNodeGraphEntity]:
        ret = []
        for port in self.entry.connected_to_n:
            ret.append(port.parentItem())
        return ret

    def getSubscribers(self) -> List[RosRunningNodeGraphEntity]:
        ret = []
        for line in self.exit.lines:
            ret.append(line.target.parentItem())
        return ret