import csv

from PyQt5.QtWidgets import *

from ui.update_dialogs.updateProgram import Ui_UpdateProgramDialog

STUDENT_CSV = "data/STUDENT.csv"
PROGRAM_CSV = "data/PROGRAM.csv"
COLLEGE_CSV = "data/COLLEGE.csv"

class UpdateProgramDialog(QDialog, Ui_UpdateProgramDialog):
    def __init__(self, programCode, programName, collegeCode):
        super().__init__()
        self.setupUi(self)
        self.collegeChoices()

        # Store the original values for comparison
        self.originalProgramCode = programCode
        self.originalProgramName = programName
        self.originalCollegeCode = collegeCode

        # Input current data on to the line edits.
        self.programCodeEdit.setText(programCode)
        self.programNameEdit.setText(programName)
        self.collegeCodeBox.setCurrentText(collegeCode)

        # Validates if input is not empty
        self.confirmButton.clicked.connect(self.validateProgramData)       
        self.cancelButton.clicked.connect(self.reject)

    def collegeChoices(self):
        with open(COLLEGE_CSV, "r", newline='') as file:
            reader = csv.reader(file)
            next(reader, None)
            college_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))

            self.collegeCodeBox.clear()
            self.collegeCodeBox.addItems(college_codes)
    
    def readProgramCSV(self):
        with open(PROGRAM_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            data = [row for row in reader]
            self.programData = data

    def updatedProgramData(self):
        self.readProgramCSV()

        newProgramCode = self.programCodeEdit.text().strip().replace(" ", "").upper()
        newProgramName = self.programNameEdit.text().strip().title()
        newCollegeCode = self.collegeCodeBox.currentText()

        # If no changes are made, return the original values
        if (newProgramCode == self.originalProgramCode and
            newProgramName == self.originalProgramName and
            newCollegeCode == self.originalCollegeCode):
            return [self.originalProgramCode, self.originalProgramName, self.originalCollegeCode]

        if not (newProgramCode and newProgramName and newCollegeCode):
            QMessageBox.warning(self, "Input Error", "All fields must be filled up.")
            return None
        
        # Validates if program code and name contains digits
        if not all(char.isalpha() or char.isspace() for char in newProgramCode and newProgramName):
            QMessageBox.warning(self, "Input Error", "Please input a valid program name.")
            return None

        for row in self.programData:
            existingProgramCode = row[0].strip().upper()
            existingProgramName = row[1].strip().replace(" ", "").upper()

            if existingProgramCode == self.originalProgramCode:
                continue  

            # Check if the program code already exists
            if existingProgramCode == newProgramCode:
                QMessageBox.warning(self, "Input Error", "The program code you are trying to add already exists.")
                return None

            # Check if the program name already exists
            if existingProgramName == newProgramName.replace(" ", "").upper():
                QMessageBox.warning(self, "Input Error", "The program name you are trying to enter already exists.")
                return None

        return [newProgramCode, newProgramName, newCollegeCode]
    
    def validateProgramData(self):
        updated_data = self.updatedProgramData()
        if updated_data:
            self.accept()