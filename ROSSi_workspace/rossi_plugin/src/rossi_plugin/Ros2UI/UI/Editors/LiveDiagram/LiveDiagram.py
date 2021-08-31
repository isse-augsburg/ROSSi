import _thread
from threading import Thread
from time import sleep
from typing import List

import typing
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QSlider, QWidget, QVBoxLayout, QLabel, QHBoxLayout

from ..RosNodeEditor.GraphEntities.RosPublisherGraphEntity import RosPublisherGraphEntity
from ...UIElements.InteractiveGraphicsScene import InteractiveGraphicsScene
from ....UI.Editors.LiveDiagram.GraphEntities.RosRunningNode import RosRunningNode
from ....Representations.Ros2Representations.RosTopic import RosPublisher, RosSubscriber
from ....UI.Editors.LaunchFileEditor.GraphEntities.RosNamespaceGraphEntity import RosNamespaceGraphEntity
from ....UI.Editors.LiveDiagram.GraphEntities.RosRunningNamespaceGraphEntity import RosRunningNamespaceGraphEntity
from ....UI.Editors.LiveDiagram.GraphEntities.RosRunningNodeGraphEntity import RosRunningNodeGraphEntity
from ....UI.UIElements.InteractiveGraphicsView import InteractiveGraphicsView
import rclpy


class LiveViewBackgroundWorker(QtCore.QThread):
    refresh_event = pyqtSignal(object)
    node: rclpy.node.Node

    def __init__(self, node, rate: float = 1):
        super(LiveViewBackgroundWorker, self).__init__()
        self.rate = rate  # seconds
        self.stop = False
        self.node = node
        self.counter = 0

    def update(self):
        self.ret: List[RosRunningNode] = []
        for name, namespace in self.node.get_node_names_and_namespaces():
            subs = self.node.get_subscriber_names_and_types_by_node(name, namespace)
            pubs = self.node.get_publisher_names_and_types_by_node(name, namespace)
            #print(name, self.node.get_name(), namespace, self.node.get_namespace())
            if not (name == self.node.get_name() and namespace == self.node.get_namespace()):
                self.ret.append(RosRunningNode(name, [RosPublisher(name, msg_type) for name, msg_type in pubs],
                                          [RosSubscriber(name, msg_type) for name, msg_type in subs],
                                          namespace))

        self.refresh_event.emit(self.ret)

    def resend(self):
        self.refresh_event.emit(self.ret)

    def __del__(self):
        self.wait()

    def run(self):
        while not self.stop:
            if self.node is not None and self.counter == 0:
                self.update()
            else:
                self.resend()

            self.counter += 1
            self.counter %= 10
            sleep(self.rate/10)


class LiveWindow(QWidget):
    def __init__(self, parent, node):
        super(LiveWindow, self).__init__(None)

        self.lay = QVBoxLayout()
        self.scene = parent
        #self.view = InteractiveGraphicsView(self.scene)
        #self.lay.addWidget(self.scene)
        self.setLayout(self.lay)

        self.sl = QSlider(Qt.Horizontal)
        self.sl.setMinimum(50)
        self.sl.setMaximum(1000)
        self.sl.setValue(300)
        self.sl.setTickPosition(QSlider.TicksBelow)
        self.sl.valueChanged.connect(self.l_valuechange)
        self.l_label = QLabel("distance")

        self.srep = QSlider(Qt.Horizontal)
        self.srep.setMinimum(50)
        self.srep.setMaximum(1000)
        self.srep.setValue(100)
        self.srep.setTickPosition(QSlider.TicksBelow)
        self.srep.valueChanged.connect(self.srep_valuechange)
        self.rep_label = QLabel("c rep")

        self.sspring = QSlider(Qt.Horizontal)
        self.sspring.setMinimum(1)
        self.sspring.setMaximum(100)
        self.sspring.setValue(10)
        self.sspring.setTickPosition(QSlider.TicksBelow)
        self.sspring.valueChanged.connect(self.sspring_valuechange)
        self.spring_label = QLabel("c spring")

        self.lay2 = QVBoxLayout()

        hb = QHBoxLayout()
        hb.addWidget(self.l_label)
        hb.addWidget(self.sl)
        self.lay2.addLayout(hb)

        hb = QHBoxLayout()
        hb.addWidget(self.rep_label)
        hb.addWidget(self.srep)
        self.lay2.addLayout(hb)

        hb = QHBoxLayout()
        hb.addWidget(self.spring_label)
        hb.addWidget(self.sspring)
        self.lay2.addLayout(hb)

        self.lay.addLayout(self.lay2)
        self.live = LiveDiagram(self.scene, node)
        self.lay.addWidget(self.live)
        self.view = self.live
        self.requestTabEvent = self.view.requestTabEvent

    def l_valuechange(self):
        size = self.sl.value()
        RosRunningNamespaceGraphEntity.l = size

    def srep_valuechange(self):
        size = self.srep.value()
        RosRunningNamespaceGraphEntity.c_rep = size

    def sspring_valuechange(self):
        size = self.sspring.value()
        RosRunningNamespaceGraphEntity.c_spring = size

    # cheating a little at this point.
    # Usually the PluginTab view is of type InteractiveGraphicsView
    # But because the live view need some extra controls, we add this class (LiveWindow) to the Plugintabs view
    # that's why we have to implement the same methods as the our view
    def run(self):
        self.view.run()

    def getFileMenuBarEntries(self) -> typing.Dict[str, typing.Callable]:
        self.view.getFileMenuBarEntries()

    def getOwnMenuBarEntries(self) -> typing.Dict[str, typing.Callable]:
        self.view.getOwnMenuBarEntries()

    @staticmethod
    def getOwnMenuBarName() -> str:
        LiveDiagram.getOwnMenuBarName()


class LiveDiagram(InteractiveGraphicsView):
    def __init__(self, parent, node):
        super(LiveDiagram, self).__init__(parent)

        self.worker: LiveViewBackgroundWorker = LiveViewBackgroundWorker(node)
        self.worker.start()
        #self.worker = LiveViewBackgroundWorker()
        self.type = 2
        self.worker.refresh_event.connect(self.update_callback)

        self.baseNamespace = RosRunningNamespaceGraphEntity("/", 0, 0, parent=self.baseItem, node=node, isBaseNamespace=True)
        for node in self.getTestNodesAndStuff():
            self.addRunningNodeToScene(node)

        self.node = node

        #self.t = Thread(target=self.springembedder)
        #self.t.setDaemon(True)
        #self.t.start()

    def addRunningNodeToScene(self, node: RosRunningNodeGraphEntity):
        # add all new nodes to old_nodes
        namespace = self.baseNamespace.getNamespace(node.node.namespace.split("/")[1:])  # remove '' before first /
        #tmp = "parent " + namespace.parentItem().namespaceName if isinstance(namespace.parentItem(), RosRunningNamespaceGraphEntity) else ""
        #print("added node" , node.node.name, " to ", namespace.namespaceName, tmp)
        namespace.addNode(node)
        self.update()
        self.scene().update()
        #self.scene().addItem(node)
        #self.makeTopicLines(node, subset, namespace)

    def makeTopicLines(self, new: RosRunningNodeGraphEntity, check_nodes: List[RosRunningNodeGraphEntity], namespace: RosNamespaceGraphEntity = None):
        for node in check_nodes:
            # get matching topics
            pubs, subs = node.node.getMatchingTopics(new.node)

            # check for each topic in subs and pubs if topic

            # connect both ( node and new ) to new or existing topic

    def removeNodeFromScene(self, node: RosRunningNodeGraphEntity):
        #TODO throws warning
        self.scene().removeItem(node)
        self.baseNamespace.removeNode(node)
        self.update()
        self.scene().update()

    def getTestNodesAndStuff(self) -> List[RosRunningNodeGraphEntity]:
        ret = []
        for i in range(0):
            node = RosRunningNode(str(i), [], [], "/")
            ret.append((RosRunningNodeGraphEntity(node, x=0, y=0)))
        return ret

    def update_node(self, node: RosRunningNodeGraphEntity, up: RosRunningNode):
        self.baseNamespace.updateNode(node, up)

        #for pub in up.publishers:
        #    for pub2 in node.node.publishers:
        #        if not pub.topic.equals(pub2.topic):
        #            node.node.publishers.append(pub2)

    @QtCore.pyqtSlot(List[str])
    def update_callback(self, nodes: List[RosRunningNode]):
        new_nodes = []
        still_there = []
        #TODO if two nodes with same name are running only one will be displayed
        # check list of retrieved node names for matches in already existing BaseGraphEntities
        # or maybe just keep track of the numbers of same nodes
        old_nodes = self.baseNamespace.getAllNodes()
        #for node in old_nodes:
        #    if node.node.name == self.node.get_name():
        #        print(node.node.name, len(node.node.publishers), len(node.node.subscribers))
        #TODO tmp
        #for n in self.getTestNodesAndStuff():
        #    nodes.append(n.node)

        for node in nodes:
            found = False
            # fill still_there array, to know what nodes do not have to be updated
            for old in old_nodes:
                if old.node.namespace == node.namespace and old.node.name == node.name:
                    found = True
                    if old not in still_there:
                        still_there.append(old)

                        #print(node.name, old.node.name)
                        self.update_node(old, node)

            # fill new_node array to add new BaseGraphEntities later
            if not found:
                new_nodes.append(RosRunningNodeGraphEntity(node, x=0, y=0))

        # gone_nodes = old_nodes - still_there
        gone_nodes = []
        for node in old_nodes:
            if node not in still_there:
                gone_nodes.append(node)
        # to get nodes out that produced an error on last fetch
        #for node in old_nodes:
        #    for gone in nodes[1]: # nodes[1] = list of RosRunningNode objects
        #        if node.node.name == gone.name and node.node.namespace is gone.namespace:
        #            if gone not in gone_nodes:
        #                gone_nodes.append(node)

        # remove gone nodes from scene and old_node list
        for node in gone_nodes:
            if node in old_nodes:
                self.removeNodeFromScene(node)

        # add all new nodes to scene
        for node in new_nodes:
            self.addRunningNodeToScene(node)

        self.springembedder()
    # start a cycle to recursively spring embed child items
    # https://scholar.google.de/scholar?q=A+heuristic+for+graph+drawing&hl=de&as_sdt=0&as_vis=1&oi=scholart

    def springembedder(self):
        self.baseNamespace.springembed(100)

    @staticmethod
    def getOwnMenuBarName() -> str:
        return "Live Diagram"

    @staticmethod
    def getEditor(parent=None, node=None):
        return LiveWindow(parent, node)