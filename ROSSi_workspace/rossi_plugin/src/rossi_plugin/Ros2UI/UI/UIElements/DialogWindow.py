import os
import typing
from PyQt5 import QtWidgets, uic, QtCore, Qt, QtGui
from PyQt5.QtWidgets import QLabel, QTextEdit, QHBoxLayout, QVBoxLayout, QLineEdit, QCheckBox, QWidget, QGridLayout, \
    QSpacerItem, QSizePolicy, QPushButton, QFileDialog, QComboBox
from ament_index_python import get_resource


class AbstractOptionParameter:
    def __init__(self):
        pass

    def getGraphics(self) -> QHBoxLayout:
        raise NotImplementedError


class DisplayParameter(AbstractOptionParameter):
    def __init__(self, value: str):
        super(DisplayParameter, self).__init__()
        self.label = QLabel(value)

    def getGraphics(self):
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        return layout

    def setText(self, text: str):
        self.label.setText(text)


class SelectionParameter(AbstractOptionParameter):
    def __init__(self, values: typing.List, default: str, setter):
        super(SelectionParameter, self).__init__()
        self.combo = QComboBox()
        self.combo.addItems(values)
        self.combo.currentIndexChanged.connect(self.selectionchange)
        self.setter = setter
        self.combo.setCurrentText(default)

    def selectionchange(self):
        val = self.combo.currentText()
        self.setter(val)

    def getGraphics(self):
        layout = QHBoxLayout()
        layout.addWidget(self.combo)
        return layout


class FolderPathParameter(AbstractOptionParameter):
    def __init__(self, value: str, setter):
        super(FolderPathParameter, self).__init__()
        self.label = QLabel(value)
        self.name_label = QLabel("working directory:")
        self.buttom = QPushButton("select")
        self.buttom.pressed.connect(self.pressed)
        self.setter_func = setter

    def getGraphics(self):
        layout = QHBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.label)
        layout.addWidget(self.buttom)
        return layout

    def pressed(self):
        file = str(QFileDialog.getExistingDirectory(None, "Select Directory"))
        self.label.setText(file)
        self.setter_func(file)


class DoneParameter(AbstractOptionParameter):
    def __init__(self, callback):
        self.c = callback

    def callback(self):
        self.c()

    def getGraphics(self):
        layout = QHBoxLayout()
        return layout


class OptionParameter(AbstractOptionParameter):
    label: QLabel
    input: QtWidgets.QLineEdit
    check: QCheckBox

    #abable: whether sth can be dis- and enabled or not
    def __init__(self, name: str, value, setter, abable: bool = False, enabled: bool = False, ab_setter=None):
        super(OptionParameter, self).__init__()
        self.name = name
        self.value = value
        self.setter = setter
        self.label = QLabel(name)
        self.input = QLineEdit()
        self.input.setText(self.value)
        self.input.textChanged.connect(self.set)
        self.check = QCheckBox(name)
        self.check.setChecked(enabled)
        self.ab_setter = ab_setter
        self.abable = abable
        self.check.stateChanged.connect(self.set_ab)

    def set_ab(self):
        val = self.check.isChecked()
        self.ab_setter(not val)
        self.update()
        print(val)

    def set(self):
        ret = self.setter(self.input.text())

    def update(self):
        if not self.check.isChecked():
            self.input.setDisabled(True)
        else:
            self.input.setDisabled(False)

    def getGraphics(self):
        layout = QHBoxLayout()
        if self.abable:
            layout.addWidget(self.check)
            self.update()
        else:
            layout.addWidget(self.label)
        layout.addWidget(self.input)
        return layout


class ArgumentOption(AbstractOptionParameter):
    label: QLabel
    input: QtWidgets.QLineEdit
    check: QCheckBox

    constant: bool = True  # determines whether constant or user input at ros2 launch
    overwritten: bool = False  # if a line is connected to argument

    def __init__(self, name: str, value: str, overwritten: bool, inputt: bool, setter, const_setter):
        super(ArgumentOption, self).__init__()
        self.name = name
        self.value = value
        self.overwritten = overwritten
        self.label = QLabel(name)
        self.check = QCheckBox("command line argument")
        self.check.setChecked(inputt)
        self.constant = not inputt
        self.check.stateChanged.connect(self.redo)
        self.layout = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setText(self.value)
        self.input.textChanged.connect(self.set)
        self.setter = setter
        self.const_setter = const_setter
        self.layout = QHBoxLayout()

    def set(self):
        self.setter(self.input.text())

    def redo(self):
        self.constant = not self.check.isChecked()
        self.const_setter(self.constant)
        self.layout = self.getGraphics()

    def clearLayout(self, layout):
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            l = layout.itemAt(i).layout()
            if widget is not None:
                widget.setParent(None)
                layout.removeWidget(widget)
            if l is not None:
                self.clearLayout(l)
                l.setParent(None)
                layout.removeItem(l)

    def getGraphics(self):
        self.clearLayout(self.layout)
        if self.overwritten:
            self.layout.addWidget(self.label)
            self.label.setText(self.name + ": inherited value")
        else:
            grid = QGridLayout()
            grid.setSpacing(10)
            info = QLabel()
            if self.constant:
                info.setText("(constant value)")
            else:
                info.setText("(command line input)")
            lay = QHBoxLayout()
            lay.addWidget(self.label)
            lay.addWidget(info)
            grid.addLayout(lay, 0, 0)
            grid.addWidget(QLabel("default value:"), 2, 1)
            grid.addWidget(self.input, 2, 2)
            grid.addWidget(self.check, 3, 1)
            self.layout.addLayout(grid)

        return self.layout


class OptionsWindow(QtWidgets.QDialog):
    def __init__(self, options: typing.List[AbstractOptionParameter]):
        super(OptionsWindow, self).__init__()
        if options is not None:
            _, package_path = get_resource('packages', 'rossi_plugin')
            uic.loadUi(os.path.join(package_path, 'share', 'rossi_plugin', 'resource', 'settings.ui'), self)
            self.content: QVBoxLayout = self.findChild(QtWidgets.QVBoxLayout, 'content')
            self.options = options
            self.draw()

            self.findChild(QtWidgets.QPushButton, 'pushButton').clicked.connect(self.closeDialog)
            self.exec()

    def draw(self):
        for item in self.options:
            lay = item.getGraphics()
            self.content.addLayout(lay)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        for option in self.options:
            if isinstance(option, DoneParameter):
                option.callback()

    def closeDialog(self):
        for option in self.options:
            if isinstance(option, DoneParameter):
                option.callback()
        self.accept()
