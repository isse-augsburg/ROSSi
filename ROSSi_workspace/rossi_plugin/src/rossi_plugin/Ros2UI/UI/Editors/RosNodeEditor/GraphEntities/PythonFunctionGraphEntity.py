import os
import subprocess
import sys
from typing import Dict

from PyQt5 import QtCore
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QMouseEvent

from ....BaseGraphEntities.GraphMultipleEntryPort import GraphMultipleEntryPort
from .....utils import fullname
from ....BaseGraphEntities.AbstractGraphEntity import DataObject
from ....BaseGraphEntities.StandartGraphEntity import StandartGraphEntity


class PythonFunctionGraphEntity(StandartGraphEntity):
    def __init__(self, x: float, y: float, width: float, height: float, parent=None, id: int = -1):
        super(PythonFunctionGraphEntity, self).__init__(parent, id, x, y, width, height)
        self.name: str = ""
        self.file: str = ""
        self.workingDirectory = ""
        self.port = GraphMultipleEntryPort(self, 0, height/2)

    def setWorkingDirectory(self, workingDir: str):
        self.workingDirectory = workingDir
        print("working directory set to:", self.workingDirectory)
        if self.name != "":
            self.setFile()

    def setFile(self):
        if self.file is None or self.file == "":
            self.file = self.workingDirectory + self.name + ".py"
            if not os.path.exists(self.file):
                os.makedirs(os.path.dirname(self.file), exist_ok=True)
                print(self.file)
                with open(self.file, "w+") as f:
                    pass
                with open(self.file, "w") as f:
                    f.write("def " + self.name + "(self):")
                    f.write("\n\tpass")
                    print("created file")
            #os.makedirs(os.path.dirname(self.f), exist_ok=True)
            self.fs_watcher = QtCore.QFileSystemWatcher([self.file])
            self.fs_watcher.fileChanged.connect(self.file_changed)
        else:
            old_file = self.file
            self.file = self.workingDirectory + self.name + ".py"
            try:
                os.rename(old_file, self.file)
                with open(self.file, "w") as f:
                    lines = f.readlines()
                    lines[0] = "def " + self.name + "(self):"
                    f.writelines(lines)
            except:
                pass
            self.fs_watcher = QtCore.QFileSystemWatcher([self.file])
            self.fs_watcher.fileChanged.connect(self.file_changed)

    def setName(self, name: str):
        self.name = name
        if self.workingDirectory is not "":
            self.setFile()
        self.update(self.boundingRect())

    @QtCore.pyqtSlot(str)
    def file_changed(path):
        print('File Changed!!!')

    def getData(self) -> DataObject:
        key = fullname(self)
        values = {
            "name": self.name
        }
        self.data = DataObject(key, values)
        return self.data

    @staticmethod
    def getObjectFromData(data: DataObject) -> 'StandartGraphEntity':
        item = PythonFunctionGraphEntity(0, 0, data.values["width"], data.values["height"])
        item.name = data.values["name"]
        return item

    def _toDict(self) -> Dict:
        pass

    def toCode(self, intendLevel: int = 0):
        ret = []
        intend = "\t" * intendLevel
        with open(self.file, "r") as f:
            ret = f.readlines()
            for line in ret:
                ret[ret.index(line)] = intend + line
        return ret, []

    def paint(self, painter, option, widget):
        super(PythonFunctionGraphEntity, self).paint(painter, option, widget)
        painter.drawText(QRectF(0, 0, self.width, self.height/2), QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft, self.name)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if sys.platform == "win32":
            os.startfile(self.file)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, self.file])



