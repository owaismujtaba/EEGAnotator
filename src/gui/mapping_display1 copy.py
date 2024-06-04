import sys
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

class TableWidgetDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        
        # Create a QTableWidget
        self.tableWidget = QTableWidget()
        
        # Set the number of rows and columns
        self.tableWidget.setRowCount(4)
        self.tableWidget.setColumnCount(3)
        
        # Set the table headers
        self.tableWidget.setHorizontalHeaderLabels(['Column 1', 'Column 2', 'Column 3'])
        
        # Populate the table
        for row in range(4):
            for column in range(3):
                item = QTableWidgetItem(f"Item {row+1},{column+1}")
                self.tableWidget.setItem(row, column, item)
        
        # Connect the cellClicked signal to the handler method
        self.tableWidget.cellClicked.connect(self.handleCellClicked)
        
        # Add the table to the layout
        self.layout.addWidget(self.tableWidget)
        
        # Set the layout to the window
        self.setLayout(self.layout)
        
        self.setWindowTitle("QTableWidget Demo")
        self.setGeometry(300, 300, 400, 300)
    
    def handleCellClicked(self, row, column):
        # Extract data from the clicked row
        row_data = []
        for col in range(self.tableWidget.columnCount()):
            item = self.tableWidget.item(row, col)
            if item is not None:
                row_data.append(item.text())
            else:
                row_data.append('')  # Handle case where the cell is empty

        print(f"Row {row} clicked. Data: {row_data}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = TableWidgetDemo()
    demo.show()
    sys.exit(app.exec_())
