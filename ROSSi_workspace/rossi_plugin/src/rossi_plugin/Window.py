import os

import typing
from PyQt5 import QtCore
from ament_index_python import get_resource
from python_qt_binding import QtWidgets
from python_qt_binding.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QDialogButtonBox, QVBoxLayout, \
    QComboBox, QWidget, QMainWindow, QMenu, QAction
from python_qt_binding import loadUi
import sys

from .Ros2UI.UI.Editors.LiveDiagram.LiveDiagram import LiveDiagram
from .Ros2UI.utils import import_submodules
from .Ros2UI.UI import Editors as Editors

from .Ros2UI.UI.UIElements.PluginTab import PluginTab

from .Ros2UI.UI.UIElements.InteractiveGraphicsView import InteractiveGraphicsView
from .Ros2UI.UI.UIElements.LibraryWindow import LibraryWindow

from rqt_gui_py.plugin import Plugin


class ROSSi(Plugin):
    name = "ROSSi"

    def __init__(self, context):
        super(ROSSi, self).__init__(context)

        self._node = context.node
        self._logger = self._node.get_logger().get_child('rossi_plugin.Window.ROSSi')
        self._widget = QWidget()
        _, package_path = get_resource('packages', 'rossi_plugin')
        ui_file = os.path.join(package_path, 'share', 'rossi_plugin', 'resource', 'main.ui')
        loadUi(ui_file, self._widget)
        self._widget.setObjectName('ROSSi')

        if context.serial_number() > 1: # in case another windows is already open
            self._widget.setWindowTitle(
                self._widget.windowTitle() + (' (%d)' % context.serial_number()))

        self.menuFile = self._widget.findChild(QtWidgets.QMenu, 'menuFile')
        self.menuDyn = self._widget.findChild(QtWidgets.QMenu, 'dyn')

        self.action_run = self._widget.findChild(QtWidgets.QAction, 'actionrun')

        self.menuLibrary = self._widget.findChild(QtWidgets.QAction, 'actionshow')
        self.menuLibrary.triggered.connect(self.show_library)

        self._widget.findChild(QtWidgets.QAction, 'actionrun').triggered.connect(self.run)
        self._widget.findChild(QtWidgets.QAction, 'actionstop').triggered.connect(self.stop)

        self.tabWidget: QtWidgets.QTabWidget = self._widget.findChild(QtWidgets.QTabWidget, 'tabWidget')
        self.tabWidget.currentChanged.connect(self.onTabChange)
        self.dialogs = []

        context.add_widget(self._widget)

        self.editorComboboxDict = {}
        self.checkForEditors()
        self.load_current_tab()

        # -
        tab = PluginTab()
        view = self.editorComboboxDict[LiveDiagram.getOwnMenuBarName()].getEditor(tab.scene, self._node)
        tab.setView(view)
        self.tabWidget.addTab(tab, LiveDiagram.getOwnMenuBarName())
        view.requestTabEvent.connect(self.add_new_tab)
        tab = self.tabWidget.currentWidget()
        self.tabWidget.removeTab(0)
        self.tabWidget.addTab(tab, "+")
        # -

    def checkForEditors(self):
        # to find editor subclasses
        import_submodules(Editors.__name__)
        for cls in InteractiveGraphicsView.__subclasses__():
            self.editorComboboxDict[cls.getOwnMenuBarName()] = cls

    def __openPluginBrowser(self, index: int):
        dialog = QtWidgets.QDialog()
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.reject)

        layout = QVBoxLayout()
        combo = QComboBox()
        for key in self.editorComboboxDict:
            combo.addItem(key)
        layout.addWidget(combo)
        layout.addWidget(buttonBox)
        dialog.setLayout(layout)
        if dialog.exec_():
            t = combo.itemText(combo.currentIndex())
            tab = PluginTab()
            view = self.editorComboboxDict[t].getEditor(tab.scene, self._node)
            tab.setView(view)
            self.tabWidget.addTab(tab, t)
            view.requestTabEvent.connect(self.add_new_tab)
            tab = self.tabWidget.currentWidget()
            self.tabWidget.removeTab(index)
            self.tabWidget.addTab(tab, "+")

    def onTabChange(self, index: int):
        if self.tabWidget.tabText(index) == "+":
            self.__openPluginBrowser(index)
        self.load_current_tab()

    @QtCore.pyqtSlot(typing.Tuple)
    def add_new_tab(self, tuple: typing.Tuple):
        # tuple(class, tab_name, q_items)
        tab = PluginTab()
        view = tuple[0].getEditor(tab.scene, self._node)
        view.addAll(tuple[2])
        tab.setView(view)
        tab2 = self.tabWidget.widget(self.tabWidget.count()-1)
        self.tabWidget.removeTab(self.tabWidget.count()-1)
        self.tabWidget.addTab(tab, tuple[1])
        self.tabWidget.addTab(tab2, "+")
        pass

    def load_current_tab(self):
        self.menuFile.clear()
        self.menuDyn.clear()
        self.menuDyn.setTitle("unknown")

        if isinstance(self.tabWidget.currentWidget(), PluginTab):
            if self.tabWidget.currentWidget().view.getFileMenuBarEntries() is not None:
                for key in self.tabWidget.currentWidget().view.getFileMenuBarEntries():
                    a = self.menuFile.addAction(key)
                    a.triggered.connect(self.tabWidget.currentWidget().view.getFileMenuBarEntries()[key])

            self.menuDyn.setTitle(self.tabWidget.currentWidget().view.getOwnMenuBarName())
            if self.tabWidget.currentWidget().view.getOwnMenuBarEntries() is not None:
                for key in self.tabWidget.currentWidget().view.getOwnMenuBarEntries():
                    a = self.menuDyn.addAction(key)
                    a.triggered.connect(self.tabWidget.currentWidget().view.getOwnMenuBarEntries()[key])

    def run(self):
        if isinstance(self.tabWidget.currentWidget(), PluginTab):
            if hasattr(self.tabWidget.currentWidget().view, "run"):
                self.tabWidget.currentWidget().view.run()

    def stop(self):
        if isinstance(self.tabWidget.currentWidget(), PluginTab):
            if hasattr(self.tabWidget.currentWidget().view, "stop"):
                self.tabWidget.currentWidget().view.stop()

    def show_library(self):
        window = LibraryWindow()
        self.dialogs.append(window)

    def focusInEvent(self, event):
        self.label.setText('Got focus')

    def focusOutEvent(self, event):
        self.label.setText('Lost focus')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    a = ROSSi(None)
    sys.exit(app.exec_())
