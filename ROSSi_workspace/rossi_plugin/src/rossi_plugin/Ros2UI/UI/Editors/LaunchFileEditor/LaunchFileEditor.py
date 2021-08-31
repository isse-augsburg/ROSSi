import os
import signal
import time
from subprocess import Popen, PIPE
from typing import List

import typing

from python_qt_binding.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QDialogButtonBox, QVBoxLayout, \
    QComboBox, QWidget, QMainWindow, QMenu, QGraphicsItem

from ...BaseGraphEntities.AbstractGraphEntity import AbstractGraphEntity
from ...BaseGraphEntities.StandartGraphEntity import StandartGraphEntity
from ....CodeGenerator.CodeGeneratorLaunch import CodeGeneratorLaunch
from ....CodeGenerator.GraphToJson import exportJson, importJson
from ....UI.UIElements.InteractiveGraphicsView import InteractiveGraphicsView, BaseItem

from ...Editors.LaunchFileEditor.GraphEntities.RosExecutableGraphEntity import RosExecutableGraphEntity
from ...Editors.LaunchFileEditor.GraphEntities.RosLaunchFileGraphEntity import RosLaunchFileGraphEntity
from ...Editors.LaunchFileEditor.GraphEntities.RosNamespaceGraphEntity import RosNamespaceGraphEntity
from ...Editors.LaunchFileEditor.GraphEntities.RosArgumentGraphEntity import RosArgumentGraphEntity

from ...BaseGraphEntities.GraphEntryPort import GraphEntryPort
from ...BaseGraphEntities.GraphExitPort import GraphExitPort


class LaunchFileEditor(InteractiveGraphicsView):
    def __init__(self, parent, node):
        super(LaunchFileEditor, self).__init__(parent, node)
        self.process = None

    def addedItem(self, item):
        pass

    def dropEvent(self, event):
        print("launch file super call")
        super(LaunchFileEditor, self).dropEvent(event)

    # updates relationships of all elemtents after a drag
    def update(self):
        namespaces: List[RosNamespaceGraphEntity] = []
        # get all namespaces
        for item in self.scene().items():
            if type(item) is RosNamespaceGraphEntity:
                namespaces.append(item)

        # checks if a namespace moved out or into another one and updates their relations
        for namespace in namespaces:
            smalles: StandartGraphEntity.StandartGraphEntity = None
            for namespace2 in namespaces:
                if namespace is not namespace2:
                    if self.isInside(namespace, namespace2):
                        if smalles is None:
                            smalles = namespace2
                        else:
                            if smalles.area() > namespace2.area():
                                smalles = namespace2
            if smalles is not None:
                if namespace.parentItem() is not smalles:
                    namespace.setPos(namespace.scenePos() - smalles.scenePos())
                    namespace.setParentItem(smalles)
            else:
                pos = namespace.scenePos()
                namespace.setParentItem(self.baseItem)
                namespace.setPos(pos)

        # update everything else -> get the smalles namespace thats fully over the item
        for item in self.scene().items():
            if type(item) is RosExecutableGraphEntity or type(item) is RosLaunchFileGraphEntity:
                # remeber old parent of item
                parent = item.parentItem()
                foundParent = False
                for namespace in namespaces:
                    # iterate only over the top level namespaces
                    if namespace.parentItem() is self.baseItem:
                        r = self.getInnermostNamespace(namespace, item)
                        # at least the top level namespace or some child namespace contains the item
                        if r is not None:
                            foundParent = True
                            print("innermost namespace is ", r.namespaceName)
                            # TODO what if 2 or more namespaces contain the item
                            if item.parentItem() is not r:
                                pos = item.scenePos()
                                item.setX(pos.x() - r.scenePos().x())
                                item.setY(pos.y() - r.scenePos().y())
                                item.setParentItem(r)
                # no parent found and the old parent is not the canvas itself
                # there has been an old parent that the item has been moved out of
                if not foundParent and parent is not self.baseItem:
                    print("innermost namespace has changed")
                    if item.parentItem() is not None:
                        pos = item.scenePos()
                        item.setParentItem(self.baseItem)
                        item.setPos(pos)
        self.printTree()

    def printTree(self):
        namespaces: List[RosNamespaceGraphEntity] = []
        # get all outer namespaces
        for item in self.scene().items():
            if type(item) is RosNamespaceGraphEntity and item.parentItem() is self.baseItem:
                namespaces.append(item)
            elif type(item) is RosExecutableGraphEntity and item.parentItem() is self.baseItem:
                print(item.display_name)
        for namespace in namespaces:
            self.recPrintNamespace(namespace, 0)


    def recPrintNamespace(self, namespace, tabs=0):
        pr = ""
        for i in range(tabs):
            pr += "\t"
        print(pr + "namespace: " + namespace.namespaceName)
        for item in namespace.childItems():
            if type(item) is RosNamespaceGraphEntity and item.parentItem() is namespace:
                self.recPrintNamespace(item, tabs+1)
            elif type(item) is RosExecutableGraphEntity and item.parentItem() is namespace:
                print(pr +"\t" + "executable: " + item.display_name)

    def getInnermostNamespace(self, namespace: RosNamespaceGraphEntity, item: QGraphicsItem):
        if self.isInside(item, namespace):
            ret = namespace
            for child in namespace.childItems():
                if type(child) is RosNamespaceGraphEntity:
                    if child.parentItem() is namespace:
                        r = self.getInnermostNamespace(child, item)
                        if r is not None:
                            ret = r
                            break
            return ret
        else:
            return None

    def addAll(self, items: List[StandartGraphEntity]):
        super(LaunchFileEditor, self).addAll(items)
        #makes connections after import
        for item in self.scene().items():
            if isinstance(item, GraphEntryPort):
                if item.has_to_connect_to_id is not -1:
                    for item2 in self.scene().items():
                        if isinstance(item2, AbstractGraphEntity):
                            #print(item2.id, item2.id == item.has_to_connect_to_id, isinstance(item2, AbstractGraphEntity), item.has_to_connect_to_id)
                            if item2.id == item.has_to_connect_to_id:
                                #print(item2, "conencted to")
                                if isinstance(item2, RosArgumentGraphEntity):
                                    item.connect(item2.exit_port, fire_events=False)
                                    item2.exit_port.drawConnection(item)
                                    item.has_to_connect_to_id = -1
                                else:
                                    item.connect(item2, fire_events=False)
                                    item.has_to_connect_to_id = -1
                                    if isinstance(item2, GraphExitPort):
                                        item2.drawConnection(item)
                                break
        self.update()

    def run(self):
        filename = "/tmp/ROSSi/launch/"
        os.makedirs(filename, exist_ok=True)
        filename += str(int(time.time()) * 1000)+".launch.py"
        CodeGeneratorLaunch(self.getAllStandardGraphEntities(), self.baseItem).make_launch_file(filename)
        command = "exec ros2 launch {0}".format(filename)
        self.process = Popen(command, shell=True, stdout=PIPE)

    def stop(self):
        if self.process is not None:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)

    def getFileMenuBarEntries(self) -> typing.Dict[str, typing.Callable]:
        ret = {}
        ret["export json"] = self.export_json
        ret["import json"] = self.import_json
        return ret

    def getOwnMenuBarEntries(self) -> typing.Dict[str, typing.Callable]:
        ret = {"export launch file": self.export_launch_file}
        return ret

    @staticmethod
    def getOwnMenuBarName() -> str:
        return "Launch File Editor"

    @staticmethod
    def getEditor(parent=None, node=None):
        return LaunchFileEditor(parent, node)

    def export_launch_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            CodeGeneratorLaunch(self.getAllStandardGraphEntities(), self.baseItem).make_launch_file(fileName)
            print("launch file created: " + fileName)

    def export_json(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "Text Files (*.json);;All Files (*)", options=options)
        if fileName:
            exportJson(fileName, self.getAllStandardGraphEntities(), "launch")

    def import_json(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "Text Files (*.json);;All Files (*)", options=options)
        if fileName:
            # import into self if nothing done yet
            if len(self.scene().items()) <= 1:
                self.addAll(importJson(fileName, "launch"))
            else:
                self.requestTabEvent.emit((self.__class__, fileName, importJson(fileName, "launch")))