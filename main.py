from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QLabel, QWidget, \
    QGridLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem
from PyQt6.QtGui import QAction
import sys
import sqlite3


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        grid = QGridLayout()

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")

        add_student_action = QAction("Add Student", self)
        file_menu_item.addAction(add_student_action)
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Mobile-No"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

    def load_table(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_num, row_data in enumerate(result):
            self.table.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

        connection.close()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_table()
sys.exit(app.exec())
