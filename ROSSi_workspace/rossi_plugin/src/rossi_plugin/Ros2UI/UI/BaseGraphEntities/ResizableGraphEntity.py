from typing import Dict

from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QBrush, QPainterPath, QPainter, QColor, QPen

from ..BaseGraphEntities.StandartGraphEntity import StandartGraphEntity


class ResizableGraphEntity(StandartGraphEntity):
    handleTopLeft = 1
    handleTopMiddle = 2
    handleTopRight = 3
    handleMiddleLeft = 4
    handleMiddleRight = 5
    handleBottomLeft = 6
    handleBottomMiddle = 7
    handleBottomRight = 8

    handleSize = +6.0

    handleCursors = {
        handleTopLeft: Qt.SizeFDiagCursor,
        handleTopMiddle: Qt.SizeVerCursor,
        handleTopRight: Qt.SizeBDiagCursor,
        handleMiddleLeft: Qt.SizeHorCursor,
        handleMiddleRight: Qt.SizeHorCursor,
        handleBottomLeft: Qt.SizeBDiagCursor,
        handleBottomMiddle: Qt.SizeVerCursor,
        handleBottomRight: Qt.SizeFDiagCursor,
    }

    def __init__(self, x: float, y: float, width: float, height: float, parent=None, id: int = -1):
        super().__init__(parent, id, x, y, width, height)
        self.handles = {}
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.updateHandlesPos()

    def handleAt(self, point):
        """
        Returns the resize handle below the given point.
        """
        for k, v, in self.handles.items():
            if v.contains(point):
                return k
        return None

    def hoverMoveEvent(self, moveEvent):
        """
        Executed when the mouse moves over the shape (NOT PRESSED).
        """
        if moveEvent is not None:
            if self.isSelected():
                handle = self.handleAt(moveEvent.pos())
                cursor = Qt.ArrowCursor if handle is None else self.handleCursors[handle]
                self.setCursor(cursor)
            super().hoverMoveEvent(moveEvent)

    def hoverLeaveEvent(self, moveEvent):
        """
        Executed when the mouse leaves the shape (NOT PRESSED).
        """
        if moveEvent is not None:
            self.setCursor(Qt.ArrowCursor)
            super().hoverLeaveEvent(moveEvent)

    def mousePressEvent(self, mouseEvent):
        """
        Executed when the mouse is pressed on the item.
        """
        self.handleSelected = self.handleAt(mouseEvent.pos())
        if self.handleSelected:
            self.mousePressPos = mouseEvent.pos()
            self.mousePressRect = self.boundingRect()
        super().mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        """
        Executed when the mouse is being moved over the item while being pressed.
        """
        if self.handleSelected is not None and not self.dragable:
            self.interactiveResize(mouseEvent.pos())
        else:
            super().mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        """
        Executed when the mouse is released from the item.
        """
        super().mouseReleaseEvent(mouseEvent)
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.update()

    def boundingRect(self):
        """
        Returns the bounding rect of the shape (including the resize handles).
        """
        o = self.handleSize - self.handleSize/2
        return super().boundingRect().adjusted(-o, -o, o, o)

    def updateHandlesPos(self):
        """
        Update current resize handles according to the shape size and position.
        """
        s = self.handleSize
        b = self.boundingRect()
        self.handles[self.handleTopLeft] = QRectF(b.left(), b.top(), s, s)
        self.handles[self.handleTopMiddle] = QRectF(b.center().x() - s / 2, b.top(), s, s)
        self.handles[self.handleTopRight] = QRectF(b.right() - s, b.top(), s, s)
        self.handles[self.handleMiddleLeft] = QRectF(b.left(), b.center().y() - s / 2, s, s)
        self.handles[self.handleMiddleRight] = QRectF(b.right() - s, b.center().y() - s / 2, s, s)
        self.handles[self.handleBottomLeft] = QRectF(b.left(), b.bottom() - s, s, s)
        self.handles[self.handleBottomMiddle] = QRectF(b.center().x() - s / 2, b.bottom() - s, s, s)
        self.handles[self.handleBottomRight] = QRectF(b.right() - s, b.bottom() - s, s, s)

    def interactiveResize(self, mousePos):
        """
        Perform shape interactive resize.
        """
        self.prepareGeometryChange()

        fromX = self.mousePressRect.right()
        fromY = self.mousePressRect.bottom()
        toX = fromX + mousePos.x() - self.mousePressPos.x()
        toY = fromY + mousePos.y() - self.mousePressPos.y()
        diff = QPointF(0, 0)
        diff.setX(toX - fromX)
        diff.setY(toY - fromY)

        if self.handleSelected == self.handleTopLeft:
            super().setX(super().x() + diff.x())
            super().setY(super().y() + diff.y())
            self.width -= diff.x()
            self.height -= diff.y()

        elif self.handleSelected == self.handleTopMiddle:
            super().setY(super().y() + diff.y())
            self.height -= diff.y()

        elif self.handleSelected == self.handleTopRight:
            super().setY(super().y() + diff.y())
            self.height -= diff.y()
            self.width += diff.x()
            self.mousePressPos.setX(mousePos.x())

        elif self.handleSelected == self.handleMiddleLeft:
            super().setX(super().x() + diff.x())
            self.width -= diff.x()

        elif self.handleSelected == self.handleMiddleRight:
            self.width += diff.x()
            self.mousePressPos.setX(mousePos.x())

        elif self.handleSelected == self.handleBottomLeft:
            super().setX(super().x() + diff.x())
            self.height += diff.y()
            self.mousePressPos.setY(mousePos.y())
            self.width -= diff.x()

        elif self.handleSelected == self.handleBottomMiddle:
            self.height += diff.y()
            self.mousePressPos.setY(mousePos.y())

        elif self.handleSelected == self.handleBottomRight:
            self.width += diff.x()
            self.height += diff.y()
            self.mousePressPos = mousePos

        self.onResize()

    def onResize(self):
        self.updateHandlesPos()

    def shape(self):
        """
        Returns the shape of this item as a QPainterPath in local coordinates.
        """
        path = QPainterPath()
        path.addRect(super().boundingRect())
        if self.isSelected():
            for shape in self.handles.values():
                path.addEllipse(shape)
        return path

    def paint(self, painter, option, widget=None):
        """
        Paint the node in the graphic view.
        """
        super(ResizableGraphEntity, self).paint(painter=painter, option=option, widget=widget)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 255, 255, 255)))
        painter.setPen(QPen(QColor(0, 0, 0, 255), 2.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        for handle, rect in self.handles.items():
            if not self.dragable:
                if self.isSelected() or handle == self.handleSelected:
                    painter.drawRect(rect)

    def getData(self):
        raise NotImplementedError


    def _toDict(self) -> Dict:
        pass

    def toCode(self, intendLevel: int = 0):
        pass

    def getProperties(self):
        pass