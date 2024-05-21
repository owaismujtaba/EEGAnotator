import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QListWidgetItem

class DualListBox(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Layouts
        main_layout = QVBoxLayout()
        list_layout = QHBoxLayout()
        button_layout = QVBoxLayout()

        # List widgets
        self.available_list = QListWidget()
        self.selected_list = QListWidget()

        # Buttons
        add_button = QPushButton('Add >>')
        remove_button = QPushButton('<< Remove')
        add_all_button = QPushButton('Add All >>')
        remove_all_button = QPushButton('<< Remove All')

        # Connect buttons to functions
        add_button.clicked.connect(self.add_items)
        remove_button.clicked.connect(self.remove_items)
        add_all_button.clicked.connect(self.add_all_items)
        remove_all_button.clicked.connect(self.remove_all_items)

        # Add buttons to layout
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(add_all_button)
        button_layout.addWidget(remove_all_button)
        button_layout.addStretch()

        # Add list widgets and button layout to list layout
        list_layout.addWidget(self.available_list)
        list_layout.addLayout(button_layout)
        list_layout.addWidget(self.selected_list)

        # Add some example items to the available list
        for i in range(10):
            QListWidgetItem(f"Item {i}", self.available_list)

        # Add list layout to main layout
        main_layout.addLayout(list_layout)
        
        # Set main layout
        self.setLayout(main_layout)
        self.setWindowTitle('Dual List Box')
        self.show()

    def add_items(self):
        selected_items = self.available_list.selectedItems()
        for item in selected_items:
            self.available_list.takeItem(self.available_list.row(item))
            self.selected_list.addItem(item)

    def remove_items(self):
        selected_items = self.selected_list.selectedItems()
        for item in selected_items:
            self.selected_list.takeItem(self.selected_list.row(item))
            self.available_list.addItem(item)

    def add_all_items(self):
        count = self.available_list.count()
        for i in range(count):
            item = self.available_list.takeItem(0)
            self.selected_list.addItem(item)

    def remove_all_items(self):
        count = self.selected_list.count()
        for i in range(count):
            item = self.selected_list.takeItem(0)
            self.available_list.addItem(item)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DualListBox()
    sys.exit(app.exec_())
