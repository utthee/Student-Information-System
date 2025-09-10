import csv

from PyQt5.QtWidgets import *

from ui.update_dialogs.updateStudent import Ui_UpdateStudentDialog

STUDENT_CSV = "data/STUDENT.csv"
PROGRAM_CSV = "data/PROGRAM.csv"
COLLEGE_CSV = "data/COLLEGE.csv"


class UpdateStudentDialog(QDialog, Ui_UpdateStudentDialog):
    def __init__(self, idNumber, firstName, lastName, yearLevel, gender, programCode):
        super().__init__()
        self.setupUi(self)

        self.programChoices()

        self.updateIDNumber.setText(idNumber)
        self.updateFirstName.setText(firstName)
        self.updateLastName.setText(lastName)
        self.updateYearLevelComboBox.setCurrentText(yearLevel)
        self.updateGender.setText(gender)
        self.updateProgramCodeComboBox.setCurrentText(programCode)
        
        self.updateFirstName.setReadOnly(True)
        self.updateLastName.setReadOnly(True)
        self.updateIDNumber.setReadOnly(True)
        self.updateGender.setReadOnly(True)

        self.pushButton.clicked.connect(self.accept)       
        self.pushButton_2.clicked.connect(self.reject)

    def programChoices(self):
        with open(PROGRAM_CSV, "r", newline='') as file:
            reader = csv.reader(file)
            next(reader, None)
            program_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))

            self.updateProgramCodeComboBox.clear()
            self.updateProgramCodeComboBox.addItems(program_codes)

    def updatedStudentData(self):
        return [
            self.updateIDNumber.text(),
            self.updateFirstName.text(),
            self.updateLastName.text(),
            self.updateYearLevelComboBox.currentText(),
            self.updateGender.text(),
            self.updateProgramCodeComboBox.currentText(),
        ]