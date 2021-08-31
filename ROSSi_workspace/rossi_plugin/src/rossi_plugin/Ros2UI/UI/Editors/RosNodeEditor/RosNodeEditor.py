import typing

from PyQt5.QtWidgets import QFileDialog

from .GraphEntities.CodeHolder import CodeHolder
from .GraphEntities.PythonFunctionGraphEntity import PythonFunctionGraphEntity
from .GraphEntities.RosBaseNodeGraphEntityNew import RosBaseNodeGraphEntityNew
from ....CodeGenerator.GraphToJson import exportJson, importJson
from ....UI.UIElements.InteractiveGraphicsView import InteractiveGraphicsView


class RosNodeEditor(InteractiveGraphicsView):
    def __init__(self, parent, node):
        super(RosNodeEditor, self).__init__(parent, node)
        self.type = 1
        self.baseNode = RosBaseNodeGraphEntityNew(0, 0, 70, 70, self.baseItem)
        #OptionsWindow(self.baseNode.getProperties())
        
    def addedItem(self, item):
        pass
        #if isinstance(item, StandartGraphEntity):
        #    arr = item.childItems()
        #    arr.append(item)
        #    for i in arr:
        #        if isinstance(i, PythonFunctionGraphEntity):
        #            i.setWorkingDirectory(self.baseNode.working_directory)

    def removedItem(self, item):
        if isinstance(item, PythonFunctionGraphEntity):
            if item.parentItem() != self.baseItem:
                self.removeItem(item.parentItem())

    def changeWorkingDirectory(self):
        for item in self.scene().items():
            if isinstance(item, PythonFunctionGraphEntity):
                item.setWorkingDirectory(self.baseNode.working_directory)

    def toCode(self):
        # node imports
        imports = self.baseNode.toCode(0)[1]

        # node class constructor
        clas = self.baseNode.toCode(0)[0]

        # class methods
        methods = []
        for item in self.scene().items():
            if isinstance(item, CodeHolder) and not isinstance(item, RosBaseNodeGraphEntityNew):
                clas.extend(item.getCode(1)[0])
                methods.extend(item.getCode(1)[1])
                imports.extend(item.getCode(0)[2])

        # def main....
        arr = ["def main(args=None):",
               "\tnode = " + self.baseNode.name+"()",
               "\trclpy.spin(node)",
               "\tnode.destroy_node()",
               "\trclpy.shutdown()",
               "",
               "if __name__ == '__main__':",
               "\t main()"
               ]

        imports.extend(["", ""])
        ret = []
        ret.extend(clas)
        ret.append("")
        ret.extend(methods)
        ret.append("")
        ret.extend(arr)
        return ret, imports

    def export_python_node(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            end = ".py"
        if end not in fileName:
            fileName += end
        with open(fileName, "w+") as out:
            text = []
            code, imports = self.toCode()
            text.extend(imports)
            text.extend(code)
            for s in text:
                out.write(s + "\n")

    @staticmethod
    def getOwnMenuBarName() -> str:
        return "Node Editor"

    @staticmethod
    def getEditor(parent=None, node=None):
        return RosNodeEditor(parent, node)

    def getOwnMenuBarEntries(self) -> typing.Dict[str, typing.Callable]:
        ret = {"export python node": self.export_python_node}
        return ret

    def getFileMenuBarEntries(self) -> typing.Dict[str, typing.Callable]:
        ret = {}
        ret["export json"] = self.export_json
        ret["import json"] = self.import_json
        return ret

    def export_json(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            end = ".json"
        if end not in fileName:
            fileName += end
        exportJson(fileName, self.getAllStandardGraphEntities(), "node")

    def import_json(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "Text Files (*.json);;All Files (*)", options=options)
        if fileName:
            # import into self if nothing done yet
            if len(self.scene().items()) <= 1:
                self.addAll(importJson(fileName, "node"))
            else:
                self.requestTabEvent.emit((self.__class__, fileName, importJson(fileName, "node")))

