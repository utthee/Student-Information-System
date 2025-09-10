import re
import csv

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp

from ui.add_dialogs.addStudent import Ui_AddStudentDialog

STUDENT_CSV = "data/STUDENT.csv"
PROGRAM_CSV = "data/PROGRAM.csv"
COLLEGE_CSV = "data/COLLEGE.csv"

class AddStudentDialog(QDialog, Ui_AddStudentDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        regex = QRegExp(r"^\d{4}-\d{4}$")
        validator = QRegExpValidator(regex)
        self.IDNumber.setValidator(validator)

        self.programChoices()
        self.readStudentCSV()

        # Sets combo box default text to empty
        self.yearLevel.setCurrentIndex(-1)
        self.gender.setCurrentIndex(-1)
        self.programCode.setCurrentIndex(-1)

        self.pushButton.clicked.connect(self.validateStudentData)
        self.pushButton_2.clicked.connect(self.reject)
    
    def programChoices(self):
        with open(PROGRAM_CSV, "r", newline='') as file:
            reader = csv.reader(file)
            next(reader, None)
            program_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))
            self.programCode.clear()
            self.programCode.addItems(program_codes)

    def readStudentCSV(self):
        with open(STUDENT_CSV, newline="", encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            data = [row for row in reader]
            self.studentData = data

    def addStudentData(self):
        IDNumber = self.IDNumber.text()
        firstName = self.firstName.text().strip().title()
        lastName = self.lastName.text().strip().title()
        yearLevel = self.yearLevel.currentText()
        gender = self.gender.currentText()
        programCode = self.programCode.currentText()
        
        if not (IDNumber and firstName and lastName and yearLevel and gender and programCode):
            QMessageBox.warning(self, "Input Error", "All required fields must be field up.")
            return

        if not re.fullmatch(r'20\d{2}-\d{4}', IDNumber):
            QMessageBox.warning(self, "Input Error", "Input a valid ID Number.")
            return
        
        # Validates first name and last name, should not contain any numbers
        if not all(char.isalpha() or char.isspace() for char in firstName and lastName):
            QMessageBox.warning(self, "Input Error", "Input a valid name.")
            return
        
        for row in self.studentData:
            existingIDNumber = row[0]

            if existingIDNumber == IDNumber:
                QMessageBox.warning(self, "Input Error", "The ID Number you're trying to enter already exists.")
                return

        return [
            IDNumber, firstName, lastName, yearLevel, gender, programCode
        ]
    
    def validateStudentData(self):
        new_data = self.addStudentData()
        if new_data:
            self.accept()