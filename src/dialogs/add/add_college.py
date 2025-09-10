import csv

from PyQt5.QtWidgets import *

from ui.add_dialogs.addCollege import Ui_AddCollegeDialog

STUDENT_CSV = "data/STUDENT.csv"
PROGRAM_CSV = "data/PROGRAM.csv"
COLLEGE_CSV = "data/COLLEGE.csv"

class AddCollegeDialog(QDialog, Ui_AddCollegeDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.readCollegeCSV()

        self.pushButton.clicked.connect(self.validateCollegeData)
        self.pushButton_2.clicked.connect(self.reject)

    def readCollegeCSV(self):
        with open(COLLEGE_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            data = [row for row in reader]
            self.collegeData = data
    
    def addCollegeData(self):
        collegeCode = self.collegeCode.text().strip().replace(" ","").upper()
        collegeName = self.collegeName.text().strip().title()

        if not collegeCode or not collegeName:
            QMessageBox.warning(self, "Input Error", "All fields must be filled up.")
            return
        
        if not all(char.isalpha() or char.isspace() for char in collegeCode and collegeName):
            QMessageBox.warning(self, "Input Error", "Please input a valid college name.")
            return

        for row in self.collegeData:
            existingCollegeCode = row[0].strip().upper()
            existingCollegeName = row[1].strip().replace(" ", "").upper()

            # Check if the college code already exists
            if existingCollegeCode == collegeCode:
                QMessageBox.warning(self, "Input Error", "The program code you are trying to add already exists.")
                return

            # Check if the college name already exists
            if existingCollegeName == collegeName.replace(" ", "").upper():
                QMessageBox.warning(self, "Input Error", "The program name you are trying to enter already exists.")
                return
        
        return [collegeCode, collegeName]
        
    def validateCollegeData(self):
        new_values = self.addCollegeData()
        if new_values:
            self.accept()