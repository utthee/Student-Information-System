import csv

from PyQt5.QtWidgets import *

from ui.add_dialogs.addProgram import Ui_AddProgramDialog

STUDENT_CSV = "data/STUDENT.csv"
PROGRAM_CSV = "data/PROGRAM.csv"
COLLEGE_CSV = "data/COLLEGE.csv"

class AddProgramDialog(QDialog, Ui_AddProgramDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.readProgramCSV()
        self.collegeChoices()

        # Resets college combo box default text to empty
        self.collegeCode.setCurrentIndex(-1)

        self.pushButton.clicked.connect(self.validateProgramData)
        self.pushButton_2.clicked.connect(self.reject)
    
    def collegeChoices(self):
        with open(COLLEGE_CSV, "r", newline='') as file:
            reader = csv.reader(file)
            next(reader, None)
            college_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))
            self.collegeCode.clear()
            self.collegeCode.addItems(college_codes)
    
    def readProgramCSV(self):
        with open(PROGRAM_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            data = [row for row in reader]
            self.programData = data

    def addProgramData(self):
        programCode = self.programCode.text().strip().replace(" ","").upper()
        programName = self.programName.text().strip().title()
        collegeCode = self.collegeCode.currentText()

        if not (programCode and programName and collegeCode):
            QMessageBox.warning(self, "Input Error", "All fields must be filled up.")
            return
        
        if not all(char.isalpha() or char.isspace() for char in programCode and programName):
            QMessageBox.warning(self, "Input Error", "Please input a valid program name.")
            return
        
        for row in self.programData:
            existingProgramCode = row[0].strip().upper()
            existingProgramName = row[1].strip().replace(" ", "").upper()

            # Check if the program code already exists
            if existingProgramCode == programCode:
                QMessageBox.warning(self, "Input Error", "The program code you are trying to add already exists.")
                return

            # Check if the program name already exists
            if existingProgramName == programName.replace(" ", "").upper():
                QMessageBox.warning(self, "Input Error", "The program name you are trying to enter already exists.")
                return
            
        return [programCode, programName, collegeCode]

    def validateProgramData(self):
        new_data = self.addProgramData()
        if new_data:
            self.accept()