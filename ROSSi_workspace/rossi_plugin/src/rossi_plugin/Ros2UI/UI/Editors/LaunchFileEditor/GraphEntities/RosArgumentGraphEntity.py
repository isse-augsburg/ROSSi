#https://stackoverflow.com/questions/57696569/ros2-how-to-pass-arguments-from-one-launch-file-to-a-child-launch-file
from typing import Dict, List

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QRectF
from PyQt5.QtWidgets import QGraphicsItem

from ....UIElements.DialogWindow import OptionParameter, ArgumentOption
from ....BaseGraphEntities.AbstractGraphEntity import DataObject
from ....BaseGraphEntities.AbstractGraphPortEntity import ValueHolder
from ....BaseGraphEntities.GraphEntryPort import GraphEntryPort
from ....BaseGraphEntities.GraphExitPort import GraphExitPort
from ....BaseGraphEntities.StandartGraphEntity import StandartGraphEntity
from .....utils import fullname


class VariableGraphEntity(StandartGraphEntity, ValueHolder):

    deg: float = 180.0
    radius: float = 5.0
    value: str = "default"
    name: str = "name"
    setToInput: bool = False
    disabled: bool = True
    hover: bool = False

    port: GraphEntryPort

    def __init__(self, x: float, y: float, width: float, height: float, parent: QGraphicsItem = None, name: str = "", disabled: bool = True):
        super(VariableGraphEntity, self).__init__(parent, -1, x, y, height, width)
        self.setX(x)
        self.setY(y)
        self.width = width
        self.height = height

        self.name = name
        self.disabled = disabled

        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setAcceptHoverEvents(True)

        self.port = GraphEntryPort(self, 0, self.height / 2)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def getText(self):
        if self.port.connected_to is not None:
            return "inherited"
        else:
            if self.setToInput:
                return "in. def. (" + self.value + ")"
            else:
                return self.value

    def getValue(self):
        if not self.disabled:
            if self.port.connected_to is not None:
                return self.port.getValue()
            else:
                return self.value
        else:
            return ""

    def paint(self, painter, option, widget):
        if not self.disabled:
            self.port.setVisible(True)
            if self.hover:
                painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 0))
                painter.setBrush(QtGui.QBrush(QtGui.QColor(250, 250, 250)))
                painter.drawRect(2, 2, self.width-4, self.height-4)
            pen = QtGui.QPen(QtGui.QColor(0, 0, 0), 2)
            painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
            painter.setPen(pen)
            #draw text
            painter.drawText(QRectF(0, 0, self.width/3, self.height), QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter, self.name+":")
            painter.drawText(QRectF(self.width/3, 0, self.width/3*2, self.height), QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter, self.getText())
        else:
            self.port.setVisible(False)

    def getInput(self):
        return self.setToInput

    def setDisabled(self, val: bool):
        self.disabled = val
    
    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.parentItem().mouseDoubleClickEvent(event)
        
    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.parentItem().mousePressEvent(event)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.parentItem().mouseMoveEvent(event)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hover = True
        super(VariableGraphEntity, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hover = False

    def onRemoveEvent(self):
        self.parentItem().onRemoveEvent()

    def toCode(self, intendLevel: int = 0) -> str:
        if not self.disabled:
            if self.port.connected_to is not None:
                #return "launch.substitutions.LaunchConfiguration('" + self.port.connected_to.getValue() + "')"
                return self.port.connected_to.getValue()
            else:
                return "'" + self.value + "'"
        else:
            return "''"

    def _toDict(self) -> Dict:
        ret = {
            "name": self.name,
            "value": self.value,
            "disabled": self.disabled,
            "set_to_input": self.setToInput,
            "port": self.port._toDict()
        }
        return ret

    def getData(self) -> DataObject:
        pass

    @staticmethod
    def getObjectFromData(data: DataObject) -> 'StandartGraphEntity':
        pass

    def getProperties(self):
        pass

    @staticmethod
    def fromJson(json: Dict) -> 'StandartGraphEntity':
        pass


class RosArgumentGraphEntity(StandartGraphEntity, ValueHolder):
    name: str = "Peter"
    value: VariableGraphEntity #default #dann kann entweder durch verbindung oder durch input (als parameter bei ros2 launch) überschrieben werden
    prefix: VariableGraphEntity
    suffix: VariableGraphEntity
    parentParameter = None
    exit_port = GraphExitPort

    def __init__(self, x: float, y: float, width: float, height: float, dragable: bool = False, parent: QGraphicsItem = None, name: str = "name", id: int = -1):
        super(RosArgumentGraphEntity, self).__init__(parent, id, x, y, width, height)
        self.dragable = dragable
        y = self.height/4
        val = self.height - y
        val = val/3
        margin = 1.5
        self.prefix = VariableGraphEntity(0, y + margin, width-5, val, self, "prefix")
        self.value = VariableGraphEntity(0, y + val + margin, width-5, val, self, "value", disabled=False)
        self.suffix = VariableGraphEntity(0, y + val * 2 + margin, width-5, val, self, "suffix")

        self.exit_port = GraphExitPort(self, self.width, self.height/2)
        self.exit_port.id = self.id
        self.exportable = True
        self.name = name

    def paint(self, painter, option, widget):
        super(RosArgumentGraphEntity, self).paint(painter, option, widget)
        painter.drawText(QRectF(0, 0, self.width, self.height/4), QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter, "arg: " + self.name)

    def boundingRect(self):
        return QRectF(-VariableGraphEntity.radius, -VariableGraphEntity.radius, self.width + self.exit_port.radius + VariableGraphEntity.radius, self.height+VariableGraphEntity.radius)

    def mouseMoveEvent(self, event):
        super(RosArgumentGraphEntity, self).mouseMoveEvent(event)

    def getData(self) -> DataObject:
        key = fullname(self)
        values = {}
        self.data = DataObject(key, values)
        return self.data

    @staticmethod
    def getObjectFromData(data: DataObject) -> 'StandartGraphEntity':
        item = RosArgumentGraphEntity(0, 0, data.values["width"], data.values["height"])
        return item

    def toCode(self, intendLevel: int = 0):
        intend = "\t" * intendLevel
        imports = [
            "from launch.actions import DeclareLaunchArgument",
            "import launch"
        ]
        ret = []
        if self.value.setToInput: # real argument
            ret.append(intend + "DeclareLaunchArgument('"+self.name+"', default_value=[" + self.prefix.toCode() + ", " + self.value.toCode() + ", " + self.suffix.toCode() + "]),")
        else: # simple variable declaration
            ret.append(intend + "DeclareLaunchArgument('"+self.name+"', default_value=[" + self.prefix.toCode() + ", " + self.value.toCode() + ", " + self.suffix.toCode() + "], description='helper variable; do not change'),")
            #ret.append(intend + self.name + " = [" + self.prefix.toCode() + ", " + self.value.toCode() + ", " + self.suffix.toCode() + "]")
        return ret, imports

    def _toDict(self) -> Dict:
        ret = {
            "name": self.name,
            "prefix": self.prefix._toDict(),
            "value": self.value._toDict(),
            "suffix": self.suffix._toDict()
        }
        return ret

    def setSuffix(self, suffix: str):
        self.suffix.value = suffix

    def setPrefix(self, prefix: str):
        self.prefix.value = prefix

    def setValue(self, value: str):
        self.value.value = value

    def setValueInput(self, var: bool):
        self.value.setToInput = not var

    def setName(self, name: str):
        self.name = name

    def getProperties(self):
        return [
            OptionParameter("name", self.name, self.setName),
            OptionParameter("prefix", self.prefix.value, self.setPrefix, abable=True, ab_setter=self.prefix.setDisabled, enabled=not self.prefix.disabled),
            ArgumentOption("value", self.value.value, overwritten=self.value.port.isConnected(), inputt=self.value.getInput(), setter=self.setValue, const_setter=self.setValueInput),
            OptionParameter("suffix", self.suffix.value, self.setSuffix, abable=True, ab_setter=self.suffix.setDisabled, enabled=not self.suffix.disabled),
        ]

    def onRemoveEvent(self):
        self.exit_port.disconnect()
        self.value.disconnect()
        self.prefix.disconnect()
        self.suffix.disconnect()

    def getValue(self):
        if self.value.setToInput:  # real argument
            return "launch.substitutions.LaunchConfiguration('" + self.name + "')"
        else:  # simple variable declaration
            return "launch.substitutions.LaunchConfiguration('" + self.name + "')"
            #return self.name

    def getParentArgumentGraphEntities(self) -> List['RosArgumentGraphEntity']:
        ret: List[RosArgumentGraphEntity] = []
        #if self.value.port.connected_to is not None:
        #    print(self.value.port.connected_to, self.value.port.connected_to.parentItem(), isinstance(self.value.port.connected_to.parentItem(), RosArgumentGraphEntity))
        if self.prefix.port.connected_to is not None and isinstance(self.prefix.port.connected_to.parentItem(), RosArgumentGraphEntity):
            ret.append(self.prefix.port.connected_to.parentItem())
        if self.value.port.connected_to is not None and isinstance(self.value.port.connected_to.parentItem(), RosArgumentGraphEntity):
            ret.append(self.value.port.connected_to.parentItem())
        if self.suffix.port.connected_to is not None and isinstance(self.suffix.port.connected_to.parentItem(), RosArgumentGraphEntity):
            ret.append(self.suffix.port.connected_to.parentItem())
        return ret

    @staticmethod
    def fromJson(json: Dict) -> 'StandartGraphEntity':
        arg = RosArgumentGraphEntity(
            json["x"],
            json["y"],
            json["width"],
            json["height"],
            id=json["id"],
            name=json["name"],
        )

        arg.prefix.name = json["prefix"]["name"]
        arg.prefix.value = json["prefix"]["value"]
        arg.prefix.setToInput = json["prefix"]["set_to_input"]
        arg.prefix.disabled = json["prefix"]["disabled"]
        arg.prefix.port.has_to_connect_to_id = json["prefix"]["port"]["connected_to"]

        arg.value.name = json["value"]["name"]
        arg.value.value = json["value"]["value"]
        arg.value.setToInput = json["value"]["set_to_input"]
        arg.value.disabled = json["value"]["disabled"]
        arg.value.port.has_to_connect_to_id = json["value"]["port"]["connected_to"]

        arg.suffix.name = json["suffix"]["name"]
        arg.suffix.value = json["suffix"]["value"]
        arg.suffix.setToInput = json["suffix"]["set_to_input"]
        arg.suffix.disabled = json["suffix"]["disabled"]
        arg.suffix.port.has_to_connect_to_id = json["suffix"]["port"]["connected_to"]
        return arg