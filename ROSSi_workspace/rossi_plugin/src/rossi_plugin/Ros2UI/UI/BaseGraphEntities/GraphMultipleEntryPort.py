import typing

from PyQt5.QtWidgets import QGraphicsItem

from .GraphEntryPort import GraphEntryPort


class GraphMultipleEntryPort(GraphEntryPort):

    def __init__(self, parent, x: float, y: float):
        super(GraphMultipleEntryPort, self).__init__(parent, x, y)
        #replaces the connected_to from Connect superclass
        self.connected_to_n = []

    def connect(self, port: typing.Union['Connect', 'AbstractGraphPortEntity', 'ValueHolder'], fire_events: bool = True) -> None:
        if self.canConnectTo(type(port)) and self.isConnectable():
            self.connected_to_n.append(port)
            print("connect to ", port)
            #print(self.connected_to.id, self.connected_to, self.connected_to.getValue())
            if fire_events:
                for callback in self.connect_observers:
                    callback(port)

    def disconnect(self, port: typing.Union['Connect', 'AbstractGraphPortEntity', 'ValueHolder']):
        if port in self.connected_to_n:
            self.connected_to_n.remove(port)
        for callback in self.connect_observers:
            callback(None)

    def is_conencted_to(self, item: QGraphicsItem):
        return item in self.connected_to_n
