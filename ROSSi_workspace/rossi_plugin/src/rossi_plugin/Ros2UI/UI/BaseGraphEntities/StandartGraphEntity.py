import pickle
from typing import Dict, List

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent

#from python_qt_binding.QtCore import QRectF
from ..UIElements.DialogWindow import OptionsWindow
from ..BaseGraphEntities.AbstractGraphEntity import AbstractGraphEntity, DataObject, Sticky


class StandartGraphEntity(AbstractGraphEntity):
    dragable: bool = False
    exportable: bool = False
    data: DataObject

    def __init__(self, parent: QGraphicsItem, id: int, x: float, y: float, width: float, height: float):
        super(StandartGraphEntity, self).__init__(parent, id)
        self.setX(x)
        self.setY(y)
        self.width = width
        self.height = height
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        if not self.dragable:
            self.setFlag(QGraphicsItem.ItemIsMovable, True)

    def getPixmap(self):
        pixmap = QPixmap(self.boundingRect().width(), self.boundingRect().height())
        painter = QPainter(pixmap)
        pixmap.fill(QColor(255, 255, 255))
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawRect(self.boundingRect())
        rect = QRectF(self.x(), self.y(), self.boundingRect().width(), self.boundingRect().height())
        self.scene().render(painter, QRectF(), rect)
        painter.end()
        return pixmap

    def _checkForStickyChilds(self, children: List[QGraphicsItem], event: QGraphicsSceneMouseEvent) -> None:
        for child in children:
            if isinstance(child, Sticky):
                child.move(event.lastPos().x() - event.pos().x(), event.lastPos().y() - event.pos().y())
            elif child.childItems() is not None:
                self._checkForStickyChilds(child.childItems(), event)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        if self.dragable:
            self.createDrag(event)
        else:
            self._checkForStickyChilds(self.childItems(), event)
            super(StandartGraphEntity, self).mouseMoveEvent(event)

    def createDrag(self, e: 'QGraphicsSceneMouseEvent'):
        mimeData = QtCore.QMimeData()
        data = self.getData()
        data.values["width"] = self.width
        data.values["height"] = self.height
        data.values["x"] = e.pos().x()
        data.values["y"] = e.pos().y()
        data = pickle.dumps(data)
        print(data)
        mimeData.setData("bytes", data)
        pixmap = self.getPixmap()
        painter = QtGui.QPainter(pixmap)
        painter.setCompositionMode(painter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 127))
        painter.end()
        drag = QtGui.QDrag(e.widget())
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(e.pos().toPoint())
        # drag.exec()
        drag.exec_(QtCore.Qt.CopyAction)

    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.RightButton:
            self.createDrag(e)
        QGraphicsItem.mousePressEvent(self, e)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
        if not self.dragable:
            OptionsWindow(self.getProperties())

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def area(self):
        return self.width * self.height

    def paint(self, painter, option, widget):
        painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
        if self.isSelected() and not self.dragable:
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 3))
        else:
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
        painter.setBackground(QtGui.QColor(255, 255, 255))
        painter.drawRect(0, 0, self.width, self.height)

    def getData(self) -> DataObject:
        raise NotImplementedError

    @staticmethod
    def getObjectFromData(data: DataObject) -> 'StandartGraphEntity':
        raise NotImplementedError

    def toJson(self):
        ret = self._toDict()
        ret["x"] = self.scenePos().x()
        ret["y"] = self.scenePos().y()
        ret["width"] = self.width
        ret["height"] = self.height
        ret["id"] = self.id
        return {self.__class__.__name__: ret}
        #return json.dumps({self.__class__.__name__: ret})

    @staticmethod
    def fromJson(json: Dict) -> 'StandartGraphEntity':
        raise NotImplementedError

    def _toDict(self) -> Dict:
        raise NotImplementedError

    def toCode(self, intendLevel: int = 0):
        raise NotImplementedError

    def getProperties(self):
        raise NotImplementedError