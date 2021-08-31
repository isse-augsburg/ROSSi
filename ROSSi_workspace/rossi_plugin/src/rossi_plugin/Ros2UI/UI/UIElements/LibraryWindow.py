import os
from typing import List

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QItemSelection, QVariant
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt5.QtWidgets import QGraphicsScene, QVBoxLayout, QTreeView, QListWidget, QListWidgetItem
from ament_index_python import get_resource
from ros2launch.api.api import get_launch_file_paths
from ros2pkg.api import get_prefix_path

from ..Editors.RosNodeEditor.GraphEntities.RosCodeVariableGraphEntity import RosCodeVariableGraphEntity
from ..Editors.RosNodeEditor.GraphEntities.RosPublisherGraphEntity import RosPublisherGraphEntity
from ..Editors.RosNodeEditor.GraphEntities.RosSubscriberGraphEntinty import RosSubscriberGraphEntity
from ...Representations.Ros2Representations.RosPackage import RosPackage
from ...Representations.Ros2Representations.RosPackage import RosExecutable
from ..UIElements.Accordion import Expander
from ..Editors.LaunchFileEditor.GraphEntities.RosLaunchFileGraphEntity import RosLaunchFileGraphEntity
from ..Editors.LaunchFileEditor.GraphEntities.RosNamespaceGraphEntity import RosNamespaceGraphEntity
from ..Editors.LaunchFileEditor.GraphEntities.RosArgumentGraphEntity import RosArgumentGraphEntity
from ..UIElements.InteractiveGraphicsView import InteractiveGraphicsView
from ..Editors.LaunchFileEditor.GraphEntities.RosExecutableGraphEntity import RosExecutableGraphEntity
from ....Sniffer.BuiltInSniffer import BuiltInSniffer
from ....Sniffer.OperatorSniffer import OperatorSniffer
from ....Sniffer.PkgutilSniffer import PkgutilSniffer
from ....Sniffer.ROS2Sniffer import ROS2Sniffer


class LibraryWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(LibraryWindow, self).__init__()
        _, package_path = get_resource('packages', 'rossi_plugin')
        uic.loadUi(os.path.join(package_path, 'share', 'rossi_plugin', 'resource', 'library.ui'), self)
        self.treeView = QTreeView()#self.findChild(QtWidgets.QTreeView, 'treeView')
        self.treeView.setHeaderHidden(True)
        packages = []
        for packageName, executables in ROS2Sniffer().getStuff().items():
            executableList = []
            launchFileList = []
            for exe, no in executables.items():
                executable = RosExecutable(exe, exe, package=RosPackage(packageName))
                executableList.append(executable)
            launchFileList = get_launch_file_paths(path=get_prefix_path(package_name=packageName) + "/share/" + packageName + "/launch/")
            print(get_prefix_path(package_name=packageName) + "/share/" + packageName + "/launch/")
            print("\t", launchFileList)
            package = RosPackageTreeNode(RosPackage(packageName, executableList, launchFileList))
            packages.append(package)

        self.treeView.setModel(RosPackageTreeModel(packages))
        self.treeView.header().resizeSection(0, self.treeView.size().width())
        self.preview = self.findChild(QVBoxLayout, 'preview')
        self.storage = self.findChild(QVBoxLayout, 'storage')
        self.storage.setAlignment(QtCore.Qt.AlignTop)
        collapsible = Expander(self, 'ROS 2 - Executables')
        collapsible.setWidget(self.treeView)
        self.storage.addWidget(self.makeRos2Stuff())
        self.storage.addWidget(self.makeRos2NodeStuff())
        self.storage.addWidget(collapsible)
        pythonStuff = Expander(self, 'Python 3')
        #pythonStuff.setWidget(self.makePythonStuffTree())
        self.storage.addWidget(pythonStuff)
        self.scene = QGraphicsScene()
        self.view = InteractiveGraphicsView(self.scene)
        self.preview.addWidget(self.view)
        self.show()
        self.treeView.selectionModel().selectionChanged.connect(self.treeSelectionChanged)

    def treeSelectionChanged(self, newSelection: QItemSelection, oldSelection: QItemSelection):
        self.view.hoverpresslist = []
        li = []
        if self.treeView.selectionModel().selectedIndexes()[0].internalPointer().package.executables is not None:
            package = self.treeView.selectionModel().selectedIndexes()[0].internalPointer().package
            y = 0
            he = 60
            for launchFile in self.treeView.selectionModel().selectedIndexes()[0].internalPointer().package.launchFiles:
                li.append(RosLaunchFileGraphEntity(launchFile, package.name, 10, y, 300, he, dragable=True, show_parameters=False))
                y += he +10
            he = 40
            for exe in self.treeView.selectionModel().selectedIndexes()[0].internalPointer().package.executables:
                li.append(RosExecutableGraphEntity(exe, 10, y, 222, he, dragable=True, show_parameters=False))
                y+= he + 10
        self.view.addAll(li)

    def makeRos2Stuff(self):
        self.rosLaunchList = QListWidget()
        self.rosLaunchList.addItem(QListWidgetItem("namespace"))
        self.rosLaunchList.addItem(QListWidgetItem("argument"))
        expander = Expander(self, "ROS 2 - Launch Specific")
        expander.setWidget(self.rosLaunchList)
        self.rosLaunchList.selectionModel().selectionChanged.connect(self.ros2stuffSelectionChanged)
        return expander

    def makeRos2NodeStuff(self):
        self.rosNodeList = QListWidget()
        self.rosNodeList.addItem(QListWidgetItem("publisher"))
        self.rosNodeList.addItem(QListWidgetItem("subscriber"))
        self.rosNodeList.addItem(QListWidgetItem("class variable"))
        expander = Expander(self, "ROS 2 - Node Programming")
        expander.setWidget(self.rosNodeList)
        self.rosNodeList.selectionModel().selectionChanged.connect(self.ros2NodeStuffSelectionChanged)
        return expander

    def ros2NodeStuffSelectionChanged(self, newSelection: QItemSelection):
        self.view.hoverpresslist = []
        li = []
        if self.rosNodeList.item(newSelection.indexes()[0].row()).text() == "publisher":
            i = RosPublisherGraphEntity(0, 0, 200, 50, isPreview=True)
            i.name = "publisher"
            i.dragable = True
            li.append(i)
        elif self.rosNodeList.item(newSelection.indexes()[0].row()).text() == "subscriber":
            i = RosSubscriberGraphEntity(0, 0, 200, 50)
            i.name = "subscriber"
            i.dragable = True
            li.append(i)
        elif self.rosNodeList.item(newSelection.indexes()[0].row()).text() == "class variable":
            i = RosCodeVariableGraphEntity(0, 0, 100, 50)
            i.dragable = True
            li.append(i)
        self.view.addAll(li)

    def ros2stuffSelectionChanged(self, newSelection: QItemSelection):
        self.view.hoverpresslist = []
        li = []
        if self.rosLaunchList.item(newSelection.indexes()[0].row()).text() == "namespace":
            li.append(RosNamespaceGraphEntity(0, 0, 200, 50, namespaceName="name", dragable=True))
        elif self.rosLaunchList.item(newSelection.indexes()[0].row()).text() == "argument":
            li.append(RosArgumentGraphEntity(0, 0, 200, 70, dragable=True))
        self.view.addAll(li)

    def makePythonStuffTree(self):
        treeView = QTreeView()
        root_model = QStandardItemModel()

        treeView.setModel(root_model)
        tree = self.pop(OperatorSniffer().getModuleInfo())
        tree.update(self.pop(BuiltInSniffer().getModuleInfo()))
        tree.update(self.pop(PkgutilSniffer().getModuleInfo()))
        #tree.update({"ROS 2": ROS2Sniffer().getStuff()})
        self._populateTree(tree, root_model.invisibleRootItem())
        #treeView.selectionModel().selectionChanged.connect(self.test)
        treeView.setHeaderHidden(True)
        return treeView

    def pop(self, list):
        tree = {}
        for moduleName, functions, classes, constants in list:
            functionDict = {}
            classDict = {}
            constantDict = {}
            for graphFunctionEntity in functions:
                functionDict[graphFunctionEntity.name] = {}  # graphFunctionEntity
            for graphClassEntity in classes:
                classDict[graphClassEntity.displayName] = {}  # graphClassEntity
            for constant in constants:
                pass
            sub = {}
            sub.update({"functions": functionDict})
            sub.update({"classes": classDict})
            sub.update({"constants": constantDict})
            tree.update({moduleName: sub})
        return tree

    def _populateTree(self, children, parent):
        for child in sorted(children):
            child_item = QStandardItem(child)
            parent.appendRow(child_item)
            if isinstance(children, dict):
                self._populateTree(children[child], child_item)


class RosPackageTreeNode:
    def __init__(self, package: RosPackage):
        self.package = package
        self.parent = None
        self.children = []
        self.row = 0
        self.column = 0

    def executable(self, row):
        if 0 <= row < len(self.package.executables):
            return self.package.executables[row]

    def data(self, column):
        if column == self.column:
                return QVariant(self.package.name)

    def color(self, column, row):
        if column == self.column and row == self.row:
            color = QColor()
            color.setRgb(0, 0, 0)
            if self.package.executables is not None and len(self.package.executables) == 0:
                color.setRgb(210, 210, 210)
                return QVariant(color)
            return QVariant(color)
        return QVariant()

    def getDepth(self, add):
        add += 1
        if len(self.children) == 0:
            return add
        else:
            return max([child.getDepth(add) for child in self.children])
        return add

    def addSubPackage(self, pkg):
        pkg.parent = self
        pkg.row = len(self.children)
        pkg.column = self.column
        self.children.append(pkg)


class AbstractRosUITreeModel(QtCore.QAbstractItemModel):
    def __init__(self):
        QtCore.QAbstractItemModel.__init__(self)
        pass


class PythonModuleTreeModel(AbstractRosUITreeModel):
    def __init__(self):
        super(PythonModuleTreeModel, self).__init__()
        pass


class RosPackageTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, packages: List[RosPackageTreeNode]):
        super(RosPackageTreeModel, self).__init__()
        self.node = RosPackageTreeNode("")
        tmp = RosPackageTreeNode(RosPackage("packages"))
        for pkg in packages:
            tmp.addSubPackage(pkg)
            #self.node.addSubPackage(pkg)
        self.node.addSubPackage(tmp)


    def rowCount(self, index):
        if index.isValid():
            return len(index.internalPointer().children)
        return len(self.node.children)

    def columnCount(self, index):
        if index.isValid():
            return index.internalPointer().getDepth(0)
        return self.node.getDepth(0)

    def index(self, row, column, _parent=None):
        if not _parent or not _parent.isValid():
            parent = self.node
        else:
            parent = _parent.internalPointer()

        if not QtCore.QAbstractItemModel.hasIndex(self, row, column, _parent):
            return QtCore.QModelIndex()

        child = parent.children[row]
        if child:
            return QtCore.QAbstractItemModel.createIndex(self, row, column, child)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if index.isValid():
            p = index.internalPointer().parent
            if p:
                return QtCore.QAbstractItemModel.createIndex(self, p.row, p.column, p)
        return QtCore.QModelIndex()

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return node.data(index.column())
        if role == QtCore.Qt.TextColorRole:
            return node.color(index.column(), index.row())
        return None
