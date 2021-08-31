import math
from random import random
from typing import Dict, List

import typing

import rclpy
from PyQt5 import QtCore
from PyQt5.QtCore import QRectF, QTimeLine, QPointF, QPropertyAnimation, QRect
from PyQt5.QtWidgets import QGraphicsItem

from .RosRunningNode import RosRunningNode
from .....Representations.Ros2Representations.RosTopic import AbstractRosTopicUser
from ....BaseGraphEntities.AbstractGraphEntity import DataObject
from ....Editors.LiveDiagram.GraphEntities.RosRunningNodeGraphEntity import RosRunningNodeGraphEntity
from ....BaseGraphEntities.StandartGraphEntity import StandartGraphEntity
from ....Editors.LiveDiagram.GraphEntities.RosRunningTopicGraphEntity import RosRunningTopicGraphEntity


class RosRunningNamespaceGraphEntity(StandartGraphEntity):
    original_height: float = 0
    margin: int = 20
    c_rep: float = 100
    c_spring: float = 10.2
    l: float = 300

    def __init__(self, name: str, x: float, y: float, node=None, width: float = 0, height: float = 0, parent: QGraphicsItem = None, visible: bool = True, isBaseNamespace: bool = False):
        super().__init__(parent, -1, x, y, width, self.original_height)
        self.namespaceName = name
        self.isBaseNamespace = isBaseNamespace
        self.nodes: List[RosRunningNodeGraphEntity] = []
        self.topics: List[RosRunningTopicGraphEntity] = []
        self.namespaces: List[RosRunningNamespaceGraphEntity] = []
        self.container = QRectF(self.margin, self.margin, 0, 0)
        self.current_animations: List[QPropertyAnimation] = []
        self.node = node

    def paint(self, painter, option, widget):
        if not self.isBaseNamespace:# or self.isBaseNamespace:
            super(RosRunningNamespaceGraphEntity, self).paint(painter, option, widget)
            painter.drawText(QRectF(0, 0, self.width, self.height), QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft, self.namespaceName)
            painter.drawRect(self.container)

    def getData(self) -> DataObject:
        pass

    def _toDict(self) -> Dict:
        pass

    def toCode(self, intendLevel: int = 0):
        pass

    def getProperties(self):
        pass

    # makes the namespace wrap around it's children
    def updateSize(self):
        if len(self.childItems()) > 0:
            # min_x/y will tell us where to place the namespace so the top left item is inside of it
            min_x = self.childItems()[0].pos().x()
            min_y = self.childItems()[0].pos().y()

            # max_x/y will tell us the height and width of the namespace necessary tp fit all items in
            max_x = min_x
            max_y = min_y

            # get smallest/biggest x and y coordinate of all child elements relative to parent(!)
            for item in self.childItems():
                min_y = min(item.pos().y(), min_y)
                min_x = min(item.pos().x(), min_x)
                # coord + size = bottom right edge of item
                max_x = max(item.pos().x() + item.boundingRect().width(), max_x)
                max_y = max(item.pos().y() + item.boundingRect().height(), max_y)

            #print("updated", self.namespaceName)
            #print("changed size from (x, y, w, h)", self.pos().x(), self.pos().y(), self.width, self.height)

            # move top left edge to where smallest
            self.setX(self.pos().x() + min_x)
            self.setY(self.pos().y() + min_y)

            # now move all children min_x/y in the other direction
            for item in self.childItems():
                item.setX(item.pos().x() - min_x)
                item.setY(item.pos().y() - min_y + self.margin)

            # max_x/y - min_x/y = point of lower right corner -> adjust width and height
            self.width = max_x - min_x
            self.height = max_y - min_y + self.margin
            #print("to", self.pos().x(), self.pos().y(), self.width, self.height)

        if isinstance(self.parentItem(), RosRunningNamespaceGraphEntity):
            #print("calling update from ", self.namespaceName, "to", self.parentItem().namespaceName)
            self.parentItem().updateSize()

    def addTopic(self, topic: AbstractRosTopicUser) -> RosRunningTopicGraphEntity:
        for topping in self.topics:
            if topping.topic.equals(topic.topic):
                return topping
        else:
            top = RosRunningTopicGraphEntity(topic.topic, self.height, self.width, parent=self, node=self.node)
            self.updateSize()
            self.topics.append(top)
            return top

    # adds a node
    def addNode(self, node: RosRunningNodeGraphEntity):
        node.setParentItem(self)
        node.setY(self.height)
        node.setX(random() * self.height)
        self.nodes.append(node)
        self.updateSize()

        for pub in node.node.publishers:
            top = self.addTopic(pub)
            top.addPublisher(node)

        for sub in node.node.subscribers:
            top = self.addTopic(sub)
            top.addSubscriber(node)

    def updateNode(self, node: RosRunningNodeGraphEntity, new: RosRunningNode):
        #print(node.node.name, len(node.node.subscribers), len(new.subscribers))
        for nod in self.nodes:
            if node.equals(nod):
                for pub in new.publishers:
                    top = self.addTopic(pub)
                    if node not in top.getPublishers():
                        print("\tadded pub", top.topic.name, "to", node.node.name)
                        top.addPublisher(node)

                for sub in new.subscribers:
                    top = self.addTopic(sub)
                    if node not in top.getSubscribers():
                        print("\tadded sub", top.topic.name, "to", node.node.name)
                        top.addSubscriber(node)
            return

        for namespace in self.namespaces:
            return namespace.updateNode(node)


    # adds a namespace
    def addNamespace(self, namespace: 'RosRunningNamespaceGraphEntity'):
        namespace.setParentItem(self)
        namespace.setY(self.height)
        print("add namespace to", self.namespaceName, namespace.namespaceName, namespace.pos().x(), namespace.pos().y())
        #print("parent", self.pos().x(), self.pos().y(), self.width, self.height)
        #print("new", namespace.pos().x(), namespace.pos().y(), namespace.width, namespace.height)
        self.namespaces.append(namespace)
        #namespace.updateSize()

    # returns whether this namespace holds any important stuff
    def isEmpty(self) -> bool:
        return len(self.nodes) == 0 and len(self.namespaces) == 0

    # remove me if I am empty. Then tell my parents to check as well
    def checkIfHasToBeRemoved(self):
        if self.isEmpty() and not self.isBaseNamespace:
            pa = self.parentItem()
            pa.childItems().remove(self)
            self.scene().removeItem(self)
            if isinstance(pa, RosRunningNamespaceGraphEntity):
                pa.namespaces.remove(self)
                pa.checkIfHasToBeRemoved()

    def checkIfTopicsCanBeRemoved(self):
        for node in self.nodes:
            if node.node.name == self.node.get_name():
                for topic in self.topics:
                    if len(topic.getSubscribers()) + len(topic.getPublishers()) <= 0:
                        self.topics.remove(topic)
                        self.childItems().remove(topic)
                return

    # removes a node from itself or the child namespace that actually holds the node if a  match was found
    def removeNode(self, node: RosRunningNodeGraphEntity) -> bool:
        for n in self.nodes:
            if node.equals(n):

                for p in n.node.publishers:
                    for t in self.topics:
                        p.topic.equals(t.topic)
                        t.removePublisher(n)
                #TODO removing a subscriber causes trouble
                for p in n.node.subscribers:
                    for t in self.topics:
                        p.topic.equals(t.topic)
                        t.removeSubscriber(n)

                self.nodes.remove(n)
                self.checkIfTopicsCanBeRemoved()
                self.checkIfHasToBeRemoved()
                self.updateSize()
                return True

        for namespace in self.namespaces:
            return namespace.removeNode(node)
        return False

    # get all qgraphicitems inside this namespace
    def getGraphicItems(self) -> List[QGraphicsItem]:
        return self.childItems()

    # returns every node inside this namespace and all its sub-namespaces
    def getAllNodes(self) -> List[RosRunningNodeGraphEntity]:
        ret: List[RosRunningNodeGraphEntity] = []
        ret.extend(self.nodes)
        for namespace in self.namespaces:
            ret.extend(namespace.getAllNodes())
        return ret

    # returns every topic inside this namespace and all its sub-namespaces
    def getAllTopics(self) -> List[RosRunningTopicGraphEntity]:
        ret: List[RosRunningTopicGraphEntity] = []
        ret.extend(self.topics)
        for namespace in self.namespaces:
            ret.extend(namespace.getAllTopics())
        return ret

    # iterates recursively over child namespaces and returns the innermost of given namespaces-list or creates a new one
    def getNamespace(self, namespaces: List[str]) -> 'RosRunningNamespaceGraphEntity':
        if len(namespaces) == 0:
            return self
        else:
            if namespaces[0] == self.namespaceName.replace("/", ""):
                return self
            else:
                for namespace in self.namespaces:
                    if namespace.namespaceName == namespaces[0]:
                        if len(namespaces) > 0:
                            return namespace.getNamespace(namespaces[1:])
                # case no namespace was found with that name, create len(namespaces) many stacked namespaceGraphEntities add
                # them to self and return inner most:
                base = RosRunningNamespaceGraphEntity(namespaces[0], 0, 0, parent=self, node=self.node)
                self.addNamespace(base)
                #self.namespaces.append(base)
                for name in namespaces[1:]:
                    last = RosRunningNamespaceGraphEntity(name, 0, 0, parent=base, node=self.node)
                    base.addNamespace(last)
                    base = last
                return base

    # returns distance from item's mid to item2's mid
    def _dist(self, item: QGraphicsItem, item2: QGraphicsItem) -> float:
        x1 = item.pos().x() + item.boundingRect().width()/2
        x2 = item2.pos().x() + item2.boundingRect().width()/2
        y1 = item.pos().y() + item.boundingRect().height()/2
        y2 = item2.pos().y() + item2.boundingRect().height()/2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    # returns normalized vector from item to item2
    def einheits(self, item: QGraphicsItem, item2: QGraphicsItem) -> typing.Tuple:
        ret = [item.pos().x() - item2.pos().x(), item.pos().y() - item2.pos().y()]
        d = self._dist(item, item2)
        d = d if d > 0 else 1
        ret[0] /= d
        ret[1] /= d
        return tuple(ret)

    def isNeighbour(self, item: QGraphicsItem, item2: QGraphicsItem) -> bool:
        # always stay away from namespaces
        if isinstance(item, RosRunningNamespaceGraphEntity) or isinstance(item2, RosRunningNamespaceGraphEntity):
            return False
        # make force between two namespaces TODO check if right
        elif isinstance(item, RosRunningNamespaceGraphEntity) and isinstance(item2, RosRunningNamespaceGraphEntity):
            return True
        # check if Node connected to Topic
        elif isinstance(item, RosRunningNodeGraphEntity):
            if isinstance(item2, RosRunningTopicGraphEntity):
                return item2.entry.is_conencted_to(item.exit)
        # for both directions
        elif isinstance(item2, RosRunningNodeGraphEntity):
            if isinstance(item, RosRunningTopicGraphEntity):
                return item.entry.is_conencted_to(item2.exit)
        return False# random() > 0.5

    def pspring(self, item: QGraphicsItem, item2: QGraphicsItem) -> typing.Tuple:
        d = self._dist(item, item2)
        d = d if d > 0 else 1
        v = self.c_spring * math.log(d / self.l)
        e = list(self.einheits(item, item2))
        e[0] *= v
        e[1] *= v
        return tuple(e)

    def prep(self, item: QGraphicsItem, item2: QGraphicsItem) -> typing.Tuple:
        d = self._dist(item, item2)
        d = d if d > 0 else 1
        v = self.c_rep / d
        e = list(self.einheits(item, item2))
        e[0] *= v
        e[1] *= v
        return tuple(e)

    def go_mid(self, item: QGraphicsItem) -> typing.Tuple:
        pass

    def springembed(self, animation_length: int):
        self.current_animations.clear()

        sums = []
        for i, item in enumerate(self.childItems()):
            sum = [0, 0]
            if isinstance(item, RosRunningNamespaceGraphEntity):
                item.springembed(animation_length)
            for item2 in self.childItems():
                if item is not item2:
                    b = self.isNeighbour(item, item2)
                    if b:
                        v = self.pspring(item, item2)
                        sum[0] -= v[0]
                        sum[1] -= v[1]
                    else:
                        v = self.prep(item, item2)
                        sum[0] += v[0]
                        sum[1] += v[1]
            sums.append(tuple(sum))

        for i, item in enumerate(self.childItems()):
            #print(sums[i], abs(sums[i][0]) + abs(sums[i][1]))
            if abs(sums[i][0]) + abs(sums[i][1]) > 3:
                if not item.isSelected():
                    anim = QPropertyAnimation(item, b"pos")
                    anim.setDuration(animation_length)
                    anim.setStartValue(item.pos())
                    anim.setEndValue(QPointF(item.pos().x() + sums[i][0], item.pos().y() + sums[i][1]))
                    #anim.finished.connect(lambda: self.removeAnimation(anim))
                    anim.start()
                    self.current_animations.append(anim)

        #print(len(self.current_animations))
            #item.setX(item.pos().x() + sums[i][0])
            #item.setY(item.pos().x() + sums[i][1])
        #self.updateSize()

