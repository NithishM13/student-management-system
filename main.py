# Importing required libraries and classes
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QLabel, QWidget, \
    QGridLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QDialog, \
    QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3


# Class for connecting to database
class DatabaseConnection:
    def __init__(self, database_path = "database.db"):
        self.database_path = database_path

    def connect(self):
        connection = sqlite3.connect(self.database_path)
        return connection


# Main window
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 400)
        grid = QGridLayout()

        # Code related to Menu-Bar
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.about)
        help_menu_item.addAction(about_action)

        search_student_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_student_action.triggered.connect(self.search)
        help_menu_item.addAction(search_student_action)

        # Code related to Table widget
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Mobile-No"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Code related to Tool-Bar
        tool_bar = QToolBar()
        tool_bar.setMovable(True)
        self.addToolBar(tool_bar)
        tool_bar.addAction(add_student_action)
        tool_bar.addAction(search_student_action)

        # Code related to Status-Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.table.cellClicked.connect(self.cell_clicked)

    # Function to add widget to status-bar if cell clicked
    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)

    # Function for loading existing data in DataBase
    def load_table(self):
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_num, row_data in enumerate(result):
            self.table.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

        connection.close()

    # Create insert dialog window
    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    # Create search dialog window
    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    # Create edit dialog window
    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    # Create delete dialog window
    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    # Create about dialog window
    def about(self):
        dialog = AboutDialog()
        dialog.exec()


# Class for inserting data into database
class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add dropdown menu for courses
        self.course_drop_down = QComboBox()
        courses = ["Artificial Intelligence", "Computer Science", "Electrical Communication Engineering",
                   "Civil Engineering", "Electrical Electronic Engineering"]
        self.course_drop_down.addItems(courses)
        layout.addWidget(self.course_drop_down)

        # Add mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile-Number")
        layout.addWidget(self.mobile)

        # Submit button widget
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_drop_down.itemText(self.course_drop_down.currentIndex())
        mobile = self.mobile.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()

        main_window.load_table()


# Class for searching student records
class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText("Name")
        layout.addWidget(self.search)

        button = QPushButton("Search")
        button.clicked.connect(self.search_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def search_student(self):
        name = self.search.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        findings = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        rows = list(findings)
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


# Class for editing or updating the records
class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        index = main_window.table.currentRow()
        selected_name = main_window.table.item(index, 1).text()

        self.student_id = main_window.table.item(index, 0).text()

        # Add student name widget
        self.student_name = QLineEdit(selected_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Update course
        prev_course = main_window.table.item(index, 2).text()
        self.course_drop_down = QComboBox()
        courses = ["Artificial Intelligence", "Computer Science", "Electrical Communication Engineering",
                   "Civil Engineering", "Electrical Electronic Engineering"]
        self.course_drop_down.addItems(courses)
        self.course_drop_down.setCurrentText(prev_course)
        layout.addWidget(self.course_drop_down)

        # Update mobile
        prev_mobile = main_window.table.item(index, 3).text()
        self.mobile = QLineEdit(prev_mobile)
        self.mobile.setPlaceholderText("Mobile-Number")
        layout.addWidget(self.mobile)

        # Submit button widget
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (self.student_name.text(),
                        self.course_drop_down.itemText(self.course_drop_down.currentIndex()),
                        self.mobile.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh data table and close the current dialog
        main_window.load_table()
        self.close()


# Class for deleting records
class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()

        confirmation = QLabel("Are you sure you want to delete the student record?")
        yes = QPushButton("YES")
        no = QPushButton("NO")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)

        self.setLayout(layout)

        yes.clicked.connect(self.delete_record)
        no.clicked.connect(self.close)

    def delete_record(self):
        index = main_window.table.currentRow()
        student_id = main_window.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh data table and close the current dialog
        main_window.load_table()
        self.close()

        successful_message = QMessageBox()
        successful_message.setWindowTitle("Success")
        successful_message.setText("The record was deleted successfully!")
        successful_message.exec()


# About dialog window
class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        A Student Management System (SMS) is a comprehensive software application designed to efficiently manage and 
        organize various aspects of student information within an educational institution. The system is typically 
        built using Python and SQL to facilitate data storage, retrieval, and manipulation.
        """
        self.setText(content)


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_table()
sys.exit(app.exec())
