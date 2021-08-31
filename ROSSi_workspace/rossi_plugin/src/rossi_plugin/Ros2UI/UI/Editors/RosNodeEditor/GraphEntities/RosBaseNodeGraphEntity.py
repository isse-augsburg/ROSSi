import os
from typing import Dict, Callable

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QRectF

from .RosPublisherGraphEntity import RosPublisherGraphEntity
from ....UIElements.DialogWindow import OptionParameter, DoneParameter
from ....BaseGraphEntities.AbstractGraphEntity import DataObject
from ....BaseGraphEntities.StandartGraphEntity import StandartGraphEntity

from pathlib import Path


class RosBaseNodeGraphEntity(StandartGraphEntity):
    def __init__(self, x: float, y: float, width: float, height: float, parent=None, onNameChange: Callable = None,  id: int = -1):
        super(RosBaseNodeGraphEntity, self).__init__(parent, id, x, y, width, height)
        home = str(Path.home())
        self.base_working_directory = home + "/Desktop/ROSSi/"
        self.filename = None
        self.exportable = True
        self.name = ""
        self.onNameChange = onNameChange

    def getData(self) -> DataObject:
        pass

    def _toDict(self) -> Dict:
        pass

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

    """sets the nodes/executables name and renames the file associated with it"""
    def setName(self, name: str) -> bool:
        try:
            if self.filename is None:
                self.working_directory = self.base_working_directory + name + "/"
                self.filename = self.working_directory + "base.py"
                if not os.path.exists(self.filename):
                    os.makedirs(os.path.dirname(self.filename), exist_ok=True)
                    with open(self.filename, "a+") as f:
                        print("created file")
                self.name = name
                self.onNameChange()
                return True
            else:
                new = self.base_working_directory + name + "/"
                #new = self.working_directory + "base.py"
                print("file exists?", os.path.exists(new), new)
                if not os.path.exists(new):
                    os.rename(self.working_directory, new)
                    self.working_directory = new
                    self.name = name
                    self.onNameChange()
                    return True
                else:
                    return False
        except IOError as e:
            print(e)
            return False

    def setWorkingDirectory(self, path: str):
        self.working_directory = path

    def paint(self, painter, option, widget):
        super(RosBaseNodeGraphEntity, self).paint(painter, option, widget)
        painter.drawText(QRectF(0, 0, self.width, self.height), QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft, self.name)

    def onOptionsDialogClose(self):
        #TODO add rename logic of all connected pythonfunctiongraphentities
        pass

    def getProperties(self):
        ret = [OptionParameter("name", self.name, self.setName), DoneParameter(self.onOptionsDialogClose)]
        #ret = [OptionParameter("name", self.name, self.setName), FolderPathParameter(self.working_directory, self.setWorkingDirectory)]
        return ret

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
        super(RosBaseNodeGraphEntity, self).mouseDoubleClickEvent(event)
        #webbrowser.open("test.py")

    def addPublisher(self, publisher: 'RosPublisherGraphEntity'):
        pass

    def addSubscriber(self, publisher: 'RosSubscriberGraphEntity'):
        pass

