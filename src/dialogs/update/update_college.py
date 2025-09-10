import csv

from PyQt5.QtWidgets import *

from ui.update_dialogs.updateCollege import Ui_UpdateCollegeDialog

STUDENT_CSV = "data/STUDENT.csv"
PROGRAM_CSV = "data/PROGRAM.csv"
COLLEGE_CSV = "data/COLLEGE.csv"

class UpdateCollegeDialog(QDialog, Ui_UpdateCollegeDialog):
    def __init__(self, collegeCode, collegeName):
        super().__init__()
        self.setupUi(self)

        self.originalCollegeCode = collegeCode
        self.originalCollegeName = collegeName
        
        # Input current data on to the line edits.
        self.collegeCodeEdit.setText(collegeCode)
        self.collegeNameEdit.setText(collegeName)

        self.confirmButton.clicked.connect(self.validateCollegeData)       
        self.cancelButton.clicked.connect(self.reject)

    def readCollegeCSV(self):
        with open(COLLEGE_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            data = [row for row in reader]
            self.collegeData = data

    def updatedCollegeData(self):
        self.readCollegeCSV()

        newCollegeCode = self.collegeCodeEdit.text().strip().replace(" ","").upper()
        newCollegeName = self.collegeNameEdit.text().strip().title()

        # If no changes were made, return the original values
        if (newCollegeCode == self.originalCollegeCode and newCollegeName == self.originalCollegeName):
            return [self.originalCollegeCode, self.originalCollegeName]
        
        if not newCollegeCode or not newCollegeName:
            QMessageBox.warning(self, "Input Error", "All fields must be filled up.")
            return None
        
        # Validates if the input contains numbers
        if not all(char.isalpha() or char.isspace() for char in newCollegeCode and newCollegeName):
            QMessageBox.warning(self, "Input Error", "Please input a valid college name.")
            return None

        for row in self.collegeData:
            existingCollegeCode = row[0].strip().upper()
            existingCollegeName = row[1].strip().replace(" ","").upper()

            if existingCollegeCode == self.originalCollegeCode:
                continue  

            # Check if the college code already exists
            if existingCollegeCode == newCollegeCode:
                QMessageBox.warning(self, "Input Error", "The college code you are trying to add already exists.")
                return None

            # Check if the college name already exists
            if existingCollegeName == newCollegeName.replace(" ", "").upper():
                QMessageBox.warning(self, "Input Error", "The college name you are trying to enter already exists.")
                return None

        return [newCollegeCode, newCollegeName]
    
    def validateCollegeData(self):
        updated_data = self.updatedCollegeData()
        if updated_data:
            self.accept()