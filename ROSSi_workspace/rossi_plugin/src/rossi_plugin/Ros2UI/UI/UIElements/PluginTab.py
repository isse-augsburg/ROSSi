from PyQt5.QtWidgets import QWidget, QHBoxLayout

from ..UIElements.InteractiveGraphicsScene import InteractiveGraphicsScene
from ..UIElements.InteractiveGraphicsView import InteractiveGraphicsView


class PluginTab(QWidget):
    def __init__(self):
        super(PluginTab, self).__init__()
        self.lay = QHBoxLayout()
        self.scene = InteractiveGraphicsScene()
        self.setLayout(self.lay)

    def setView(self, view: InteractiveGraphicsView):
        self.view = view
        self.lay.addWidget(self.view)
