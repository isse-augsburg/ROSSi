import pickle
from typing import List

import typing
from PyQt5 import QtCore, QtGui
from PyQt5.Qt import Qt
from PyQt5.QtCore import QRectF, QPoint, pyqtSignal
from PyQt5.QtWidgets import QGraphicsView, QGraphicsItem, QWidget
from ...utils import dynamic_import

from ..BaseGraphEntities.StandartGraphEntity import StandartGraphEntity
from ..BaseGraphEntities.AbstractGraphEntity import AbstractGraphEntity


class BaseItem(QGraphicsItem):
    def __init__(self):
        super(BaseItem, self).__init__(None)

    def boundingRect(self):
        return QRectF(0, 0, 0, 0)

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
        pass


class InteractiveGraphicsView(QGraphicsView):
    control_pressed = False
    baseItem: BaseItem
    hoverpresslist: List[QGraphicsItem]
    requestTabEvent = pyqtSignal(object)
    type: int

    def __init__(self, parent=None, node=None):
        super(InteractiveGraphicsView, self).__init__(parent)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setObjectName('InteractiveGraphicsView2')
        #self.setAcceptDrops(True)
        self._zoom = 0
        self.baseItem = BaseItem()
        self.scene().addItem(self.baseItem)
        self.hoverpresslist = []
        self.type = 0

    def dragEnterEvent(self, event):
        super(InteractiveGraphicsView, self).dragEnterEvent(event)

    def dropEvent(self, event):
        item = None
        data = pickle.loads(event.mimeData().data("bytes"))
        pos = self.mapToScene(QPoint(event.pos().x() - data.values["x"], event.pos().y() - data.values["y"]))
        klass = dynamic_import(data.key)
        item = klass.getObjectFromData(data)

        if item is not None:
            item.setX(pos.x())
            item.setY(pos.y())
            item.setParentItem(self.baseItem)
            self.update()
            self.addedItem(item)

    def addedItem(self, item):
        pass

    def removedItem(self, item):
        pass

    #returns true if the boundingrect of inner is completly inside the outer one
    #or in case completly if false if inner overlaps with outer
    def isInside(self, inner: QGraphicsItem, outer: QGraphicsItem, completely: bool = True):
        #print(outer.scenePos(), inner.scenePos())
        if completely:
            #return inner.isObscuredBy(outer)
            if outer.scenePos().x() <= inner.scenePos().x() and outer.scenePos().y() <= inner.scenePos().y():
                if inner.boundingRect().width() + inner.scenePos().x() <= outer.scenePos().x() + outer.boundingRect().width() and inner.boundingRect().height() + inner.scenePos().y() <= outer.scenePos().y() + outer.boundingRect().height():
                    return True
            return False
        else:
            if inner.scenePos().x() < outer.scenePos().x() + outer.boundingRect().width() and inner.scenePos().y() < outer.scenePos().y() + outer.boundingRect().height():
                if inner.scenePos().x() + inner.boundingRect().width()  > outer.scenePos().x() and inner.scenePos().y() + inner.boundingRect().height() > outer.scenePos().y():
                    return True
            return False

    def getAllStandardGraphEntities(self):
        items: List[StandartGraphEntity] = []
        for item in self.scene().items():
            if isinstance(item, StandartGraphEntity):
                if item.exportable:
                    print("added", item)
                    items.append(item)
        return items

    def dragMoveEvent(self, event):
        super(InteractiveGraphicsView, self).dragMoveEvent(event)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
        super(InteractiveGraphicsView, self).mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            print("right")
            self.setDragMode(QGraphicsView.RubberBandDrag)
            for item in self.scene().selectedItems():
                item.setSelected(False)
        elif event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        elif event.button() == Qt.MiddleButton:
            print("middle")
            self.setDragMode(2)

        super(InteractiveGraphicsView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, mouse_event):
        self.scene().update()
        self.setDragMode(0)
        self.update()
        super(InteractiveGraphicsView, self).mouseReleaseEvent(mouse_event)


    #TODO error in library window that opened after import of diagram in main window
    def mouseMoveEvent(self, mouse_event):
        items = self.items(mouse_event.pos())  # , QtGui.QTransform())

        for item in self.hoverpresslist:
            if item not in items and item is not None:
                item.hoverLeaveEvent(None)
                self.hoverpresslist.remove(item)

        for item in items:
            if item not in self.hoverpresslist:
                if item.acceptHoverEvents():
                    self.hoverpresslist.append(item)
                    item.hoverEnterEvent(None)
            else:
                item.hoverMoveEvent(None)
        super(InteractiveGraphicsView, self).mouseMoveEvent(mouse_event)

    def wheelEvent(self, wheel_event):
        #print("wheel2")
        if self.control_pressed:
            if wheel_event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            self.scale(factor, factor)
        else:
            super().wheelEvent(wheel_event)

    def removeItem(self, item):
        if isinstance(item, AbstractGraphEntity):
            item.onRemoveEvent()
        self.removedItem(item)
        self.scene().removeItem(item)
        if item in self.hoverpresslist:
            self.hoverpresslist.remove(item)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Control:
            self.control_pressed = True
        if event.key() == QtCore.Qt.Key_Delete:
            for item in self.scene().selectedItems():
                self.removeItem(item)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Control:
            self.control_pressed = False

    def addAll(self, items: List[StandartGraphEntity]):
        self.hoverpresslist = []
        self.scene().clear()
        self.baseItem = BaseItem()
        self.scene().addItem(self.baseItem)
        for item in items:
            item.setParentItem(self.baseItem)
            self.addedItem(item)

    # will be triggered if the "run" action is selected in the main window
    # we could start a process here for example
    def run(self):
        pass

    def getFileMenuBarEntries(self) -> typing.Dict[str, typing.Callable]:
        pass

    def getOwnMenuBarEntries(self) -> typing.Dict[str, typing.Callable]:
        pass

    @staticmethod
    def getEditor(parent=None, node=None):
        pass

    @staticmethod
    def getOwnMenuBarName() -> str:
        pass