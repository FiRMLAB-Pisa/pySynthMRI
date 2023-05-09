from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QGridLayout, QVBoxLayout, QSizePolicy, QListWidget, \
    QAbstractItemView, QLabel


class psQDoubleQListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Moving Items Between List Widgets")
        # self.window_width, self.window_height = 1200, 800
        # self.setMinimumSize(self.window_width, self.window_height)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.initUI()

        self._updateButtonStatus()
        self._setButtonConnections()

    def initUI(self):
        subLayouts = {}

        subLayouts['LeftColumn'] = QGridLayout()
        subLayouts['RightColumn'] = QVBoxLayout()
        self.layout.addLayout(subLayouts['LeftColumn'], 1)
        self.layout.addLayout(subLayouts['RightColumn'], 1)

        self.buttons = {}
        self.buttons['>>'] = QPushButton('&>>')
        self.buttons['>'] = QPushButton('>')
        self.buttons['<'] = QPushButton('<')
        self.buttons['<<'] = QPushButton('&<<')

        for k in self.buttons:
            self.buttons[k].setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)

        """
        First Column
        """
        self.listWidgetLeft = QListWidget()
        self.listWidgetLeft.setSelectionMode(QAbstractItemView.ExtendedSelection)

        subLayouts['LeftColumn'].addWidget(QLabel("Available methods"), 1, 0, 1, 4)
        subLayouts['LeftColumn'].addWidget(self.listWidgetLeft, 2, 0, 4, 4)

        subLayouts['LeftColumn'].setRowStretch(5, 1)
        subLayouts['LeftColumn'].addWidget(self.buttons['>>'], 2, 4, 1, 1, alignment=Qt.AlignTop)
        subLayouts['LeftColumn'].addWidget(self.buttons['>'], 3, 4, 1, 1, alignment=Qt.AlignTop)
        subLayouts['LeftColumn'].addWidget(self.buttons['<'], 4, 4, 1, 1, alignment=Qt.AlignTop)
        subLayouts['LeftColumn'].addWidget(self.buttons['<<'], 5, 4, 1, 1, alignment=Qt.AlignTop)


        """
        Second Column
        """
        self.listWidgetRight = QListWidget()
        self.listWidgetRight.setSelectionMode(QAbstractItemView.ExtendedSelection)

        hLayout = QVBoxLayout()
        subLayouts['RightColumn'].addLayout(hLayout)
        hLayout.addWidget(QLabel("Selected methods"))

        hLayout.addWidget(self.listWidgetRight, 4)

        vLayout = QVBoxLayout()
        hLayout.addLayout(vLayout, 1)

        # vLayout.addStretch(1)

    def _setButtonConnections(self):
        self.listWidgetLeft.itemSelectionChanged.connect(self._updateButtonStatus)
        self.listWidgetRight.itemSelectionChanged.connect(self._updateButtonStatus)

        self.buttons['>'].clicked.connect(self._buttonAddClicked)
        self.buttons['<'].clicked.connect(self._buttonRemoveClicked)
        self.buttons['>>'].clicked.connect(self._buttonAddAllClicked)
        self.buttons['<<'].clicked.connect(self._buttonRemoveAllClicked)


    def _buttonAddClicked(self):
        selected_items = self.listWidgetLeft.selectedItems()
        for item in selected_items:
            idx = self.listWidgetLeft.indexFromItem(item).row()
            rowItem = self.listWidgetLeft.takeItem(idx)
            self.listWidgetRight.addItem(rowItem)

    def _buttonRemoveClicked(self):
        selected_items = self.listWidgetRight.selectedItems()
        for item in selected_items:
            idx = self.listWidgetRight.indexFromItem(item).row()
            rowItem = self.listWidgetRight.takeItem(idx)
            self.listWidgetLeft.addItem(rowItem)

    def _buttonAddAllClicked(self):
        for i in range(self.listWidgetLeft.count()):
            self.listWidgetRight.addItem(self.listWidgetLeft.takeItem(0))

    def _buttonRemoveAllClicked(self):
        for i in range(self.listWidgetRight.count()):
            self.listWidgetLeft.addItem(self.listWidgetRight.takeItem(0))

    def _updateButtonStatus(self):
        self.buttons['>'].setDisabled(not bool(self.listWidgetLeft.selectedItems()) or self.listWidgetLeft.count() == 0)
        self.buttons['<'].setDisabled(not bool(self.listWidgetRight.selectedItems()) or self.listWidgetRight.count() == 0)

    def insertItems(self, items):
        self.listWidgetLeft.addItems(items)

    def clear(self):
        self.listWidgetLeft.clear()
        # self.listWidgetRight.clear()

    def selectedItems(self):
        return [self.listWidgetRight.item(x).text() for x in range(self.listWidgetRight.count())]

