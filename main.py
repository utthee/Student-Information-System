import sys
import csv

from src.dialogs.update.update_college import UpdateCollegeDialog
from src.dialogs.update.update_program import UpdateProgramDialog
from src.dialogs.update.update_student import UpdateStudentDialog

from src.dialogs.add.add_college import AddCollegeDialog
from src.dialogs.add.add_program import AddProgramDialog
from src.dialogs.add.add_student import AddStudentDialog

from src.mainUI import Ui_MainWindow

from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets

STUDENT_CSV = "data/STUDENT.csv"
PROGRAM_CSV = "data/PROGRAM.csv"
COLLEGE_CSV = "data/COLLEGE.csv"

class MainClass(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.rows_per_page = 20
        self.current_page = 0
        self.setupUi(self)

        self.file_paths = [STUDENT_CSV, PROGRAM_CSV, COLLEGE_CSV]
        self.headers = [[], [], []]  # Store CSV headers
        self.current_table_index = self.displayComboBox.currentIndex()  # Track the current table being displayed
        self.data = [[], [], []]  # Store CSV data for each table
        self.loadCSVFiles()    

        self.deleteButton.clicked.connect(self.deleteEntry)
        self.editButton.clicked.connect(self.updateEntry)
        self.addButton.clicked.connect(self.addEntry)
        self.refreshButton.clicked.connect(self.displayTable)
        
        self.sortComboBox.currentIndexChanged.connect(self.sortLayout)
        self.searchButton.clicked.connect(self.searchEntry)

        self.displayComboBox.currentIndexChanged.connect(self.displayTable)

        self.prevPageButton.clicked.connect(self.goToPreviousPage)
        self.nextPageButton.clicked.connect(self.goToNextPage)

#------------------------------------------------------------------------------      MAJOR FUNCTIONS     ------------------------------------------------------------------------------------

#------------------------------------------------------------------------------      MAJOR FUNCTIONS     ------------------------------------------------------------------------------------
    # Previous and Next buttons
    def goToPreviousPage(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.showTable()

    def goToNextPage(self):
        if (self.current_page + 1) * self.rows_per_page < len(self.data[self.current_table_index]):
            self.current_page += 1
            self.showTable()
    
    # Delete and update buttons are unclickable whenever no row has been selected
    def updateButtonState(self):
        has_selection = self.tableWidget.currentRow() >= 0
        self.deleteButton.setEnabled(has_selection)
        self.editButton.setEnabled(has_selection)

    def updateSearchButtonState(self):
        selected_index = self.searchComboBox.currentIndex()
        search_text = self.searchBox.text().strip()
        # Enable only if an actual filter is selected (e.g., index > 0)
        self.searchButton.setEnabled(selected_index >= 0 and bool(search_text))

    def loadCSVFiles(self):
        for i, file_path in enumerate(self.file_paths):
            try:
                with open(file_path, newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    self.headers[i] = next(reader)
                    self.data[i] = [row for row in reader]
            except FileNotFoundError:
                print(f"Error: {file_path} not found.")
        
        self.displayTable()

    def displayTable(self):
        self.current_table_index = self.displayComboBox.currentIndex()
        self.clearHeaderBox()

        self.deleteButton.setEnabled(False)
        self.deleteButton.setDown(False)
        self.deleteButton.clearFocus()
        self.editButton.setEnabled(False)
        self.editButton.setDown(False)
        self.editButton.clearFocus()
        self.tableWidget.itemSelectionChanged.connect(self.updateButtonState)

        self.searchButton.setEnabled(False)
        self.searchComboBox.currentIndexChanged.connect(self.updateSearchButtonState)
        self.searchBox.textChanged.connect(self.updateSearchButtonState)

        # Resets current page when switching tables
        self.current_page = 0

        # Reset hidden rows
        for row in range(self.tableWidget.rowCount()):
            self.tableWidget.setRowHidden(row, False)

        # Reset selected row after every operation
        self.tableWidget.clearSelection()
        self.tableWidget.setCurrentItem(None)

        if self.current_table_index == 0:      
            self.readStudentCSV()
            self.showTable()
            return

        elif self.current_table_index == 1:  
            self.readProgramCSV()
            self.showTable()
            return

        elif self.current_table_index == 2:
            self.readCollegeCSV()
            self.showTable()
            return
    
    def clearHeaderBox(self):
        # Resets header items whenever a different table is shown
        self.sortComboBox.clear()
        self.sortComboBox.addItems(self.headers[self.current_table_index])
        self.sortComboBox.setCurrentIndex(-1)
        
        self.searchBox.clear()
        self.searchComboBox.clear()
        self.searchComboBox.addItems(self.headers[self.current_table_index])
        self.searchComboBox.setCurrentIndex(-1)

    def showTable(self):
        # Get the sorted data from self.data for the current table
        full_data = self.data[self.current_table_index]
        headers = self.headers[self.current_table_index]
        
        total_rows = len(full_data)
        total_pages = (total_rows - 1) // self.rows_per_page + 1

        # Pagination boundaries
        start_row = self.current_page * self.rows_per_page
        end_row = min(start_row + self.rows_per_page, total_rows)
        page_data = full_data[start_row:end_row]

        # Set headers
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)

        # Fill table with current page's data
        self.tableWidget.setRowCount(len(page_data))
        for row_idx, row in enumerate(page_data):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.tableWidget.setItem(row_idx, col_idx, item)

        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Update pagination label
        self.pageLabel.setText(f"Page {self.current_page + 1} of {total_pages}")
        
        # Enable/disable navigation buttons
        self.prevPageButton.setEnabled(self.current_page > 0)
        self.nextPageButton.setEnabled(end_row < total_rows)
    
    def searchEntry(self):
        searched_item = self.searchBox.text().lower()
        search_filter = self.searchComboBox.currentText()

        if not searched_item or not search_filter:
            self.searchInputError()
            return

        header_labels = self.headers[self.current_table_index]

        try:
            filter_col_index = header_labels.index(search_filter)
        except ValueError:
            self.searchInputError()
            return

        # Search through the full data (not just the current page)
        full_data = self.data[self.current_table_index]
        filtered_data = []

        for row in full_data:
            if filter_col_index < len(row):
                cell_text = row[filter_col_index].lower()
                if searched_item in cell_text:
                    filtered_data.append(row)

        if not filtered_data:
            self.displayTable()  # resets to full view
            self.searchError()
            return

        # Set the filtered data and reset pagination
        self.filtered_data = filtered_data
        self.current_page = 0
        self.showSearchedTable()

    # Displays searched data
    def showSearchedTable(self):
        headers = self.headers[self.current_table_index]
        data_to_display = self.filtered_data

        total_rows = len(data_to_display)
        total_pages = (total_rows - 1) // self.rows_per_page + 1

        start_row = self.current_page * self.rows_per_page
        end_row = min(start_row + self.rows_per_page, total_rows)
        page_data = data_to_display[start_row:end_row]

        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)

        self.tableWidget.setRowCount(len(page_data))
        for row_idx, row in enumerate(page_data):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.tableWidget.setItem(row_idx, col_idx, item)

        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.pageLabel.setText(f"Page {self.current_page + 1} of {total_pages}")
        self.prevPageButton.setEnabled(self.current_page > 0)
        self.nextPageButton.setEnabled(end_row < total_rows)

    def searchError(self):
        searchErrorMsg = QtWidgets.QMessageBox(self)
        searchErrorMsg.setWindowTitle("No Results")
        searchErrorMsg.setText("The item you are trying to search does not exist.")
        searchErrorMsg.setIcon(QtWidgets.QMessageBox.Warning)
        searchErrorMsg.exec_()

    def deleteEntry(self):
        if self.displayComboBox.currentIndex() == 0:
            self.deleteStudentConfirmation()
            return
        
        elif self.displayComboBox.currentIndex() == 1:
            self.deleteProgramConfirmation()
            return
        
        elif self.displayComboBox.currentIndex() == 2:
            self.deleteCollegeConfirmation()
            return

    def deleteStudentConfirmation(self):
        deleteStudentMsg = QtWidgets.QMessageBox(self)
        deleteStudentMsg.setWindowTitle("Delete Confirmation")
        deleteStudentMsg.setText("Are you sure you want to delete this student entry?")
        deleteStudentMsg.setIcon(QtWidgets.QMessageBox.Warning)
        deleteStudentMsg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
        deleteStudentMsg.setDefaultButton(QMessageBox.Cancel)
        
        confirm = deleteStudentMsg.exec_()

        if confirm == QMessageBox.Yes:
            self.deleteStudentEntry()

    def deleteStudentSuccess(self):
        deleteStudentSuccessMsg = QtWidgets.QMessageBox(self)
        deleteStudentSuccessMsg.setWindowTitle("Delete Success")
        deleteStudentSuccessMsg.setText("The student entry has been successfully deleted.")
        deleteStudentSuccessMsg.setIcon(QtWidgets.QMessageBox.Information)
        deleteStudentSuccessMsg.exec_()

    def deleteProgramConfirmation(self):
        deleteProgramMsg = QtWidgets.QMessageBox(self)
        deleteProgramMsg.setWindowTitle("Delete Confirmation")
        deleteProgramMsg.setText("Are you sure you want to delete this program entry? Students enrolled in this program will be affected.")
        deleteProgramMsg.setIcon(QtWidgets.QMessageBox.Warning)
        deleteProgramMsg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
        deleteProgramMsg.setDefaultButton(QMessageBox.Cancel)
        
        confirm = deleteProgramMsg.exec_()

        if confirm == QMessageBox.Yes:
            self.deleteProgramEntry()

    def deleteProgramSuccess(self):
        deleteProgramSuccessMsg = QtWidgets.QMessageBox(self)
        deleteProgramSuccessMsg.setWindowTitle("Delete Success")
        deleteProgramSuccessMsg.setText(f"The program has been successfully deleted. {self.studentCounter} student(s) were affected.")
        deleteProgramSuccessMsg.setIcon(QtWidgets.QMessageBox.Information)
        deleteProgramSuccessMsg.exec_()

    def deleteCollegeConfirmation(self):
        deleteCollegeMsg = QtWidgets.QMessageBox(self)
        deleteCollegeMsg.setWindowTitle("Delete Confirmation")
        deleteCollegeMsg.setText("Are you sure you want to delete this college entry? All programs under this college will also be deleted.")
        deleteCollegeMsg.setIcon(QtWidgets.QMessageBox.Warning)
        deleteCollegeMsg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
        deleteCollegeMsg.setDefaultButton(QMessageBox.Cancel)

        confirm = deleteCollegeMsg.exec_()

        if confirm == QMessageBox.Yes:
            self.deleteCollegeEntry()

    def deleteCollegeSuccess(self):
        deleteCollegeSuccessMsg = QtWidgets.QMessageBox(self)
        deleteCollegeSuccessMsg.setWindowTitle("Delete Success")
        deleteCollegeSuccessMsg.setText(f"The college has been successfully deleted. {self.programCounter} program(s) were also deleted. {self.studentCounter} student(s) were affected.")
        deleteCollegeSuccessMsg.setIcon(QtWidgets.QMessageBox.Information)
        deleteCollegeSuccessMsg.exec_()

    def addStudentSuccess(self):
        addStudentMsg = QtWidgets.QMessageBox(self)
        addStudentMsg.setWindowTitle("Input Added")
        addStudentMsg.setText("Student entry has been successfully added")
        addStudentMsg.setIcon(QtWidgets.QMessageBox.Information)
        addStudentMsg.exec_()

    def addProgramSuccess(self):
        addProgramMsg = QtWidgets.QMessageBox(self)
        addProgramMsg.setWindowTitle("Input Added")
        addProgramMsg.setText("Program entry has been successfully added")
        addProgramMsg.setIcon(QtWidgets.QMessageBox.Information)
        addProgramMsg.exec_()

    def addCollegeSuccess(self):
        addCollegeMsg = QtWidgets.QMessageBox(self)
        addCollegeMsg.setWindowTitle("Input Added")
        addCollegeMsg.setText("Program entry has been successfully added")
        addCollegeMsg.setIcon(QtWidgets.QMessageBox.Information)
        addCollegeMsg.exec_()
        
    def updateEntry(self):
        if self.displayComboBox.currentIndex() == 0:
            self.updateStudentEntry()
            return
        elif self.displayComboBox.currentIndex() == 1:
            self.updateProgramEntry()
            return
        elif self.displayComboBox.currentIndex() == 2:
            self.updateCollegeEntry()
            return

    def updateStudentSuccess(self):
        updateStudentMsg = QtWidgets.QMessageBox(self)
        updateStudentMsg.setWindowTitle("Input Updated")
        updateStudentMsg.setText("Student entry has been successfully updated")
        updateStudentMsg.setIcon(QtWidgets.QMessageBox.Information)
        updateStudentMsg.exec_()

    def updateProgramSuccess(self):
        updateProgramMsg = QtWidgets.QMessageBox(self)
        updateProgramMsg.setWindowTitle("Input Updated")
        updateProgramMsg.setText("Program entry has been successfully updated")
        updateProgramMsg.setIcon(QtWidgets.QMessageBox.Information)
        updateProgramMsg.exec_()

    def updateCollegeSuccess(self):
        updateCollegeMsg = QtWidgets.QMessageBox(self)
        updateCollegeMsg.setWindowTitle("Input Updated")
        updateCollegeMsg.setText("College entry has been successfully updated")
        updateCollegeMsg.setIcon(QtWidgets.QMessageBox.Information)
        updateCollegeMsg.exec_()

    def updateStudentEntry(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row < 0:
            return

        if hasattr(self, "filtered_data") and self.filtered_data:
            data_source = self.filtered_data
            is_filtered = True
        else:
            data_source = self.data[self.current_table_index]
            is_filtered = False

        updateIDNumber = self.tableWidget.item(selected_row, 0).text()
        updateFirstName = self.tableWidget.item(selected_row, 1).text()
        updateLastName = self.tableWidget.item(selected_row, 2).text()
        updateYearLevel = self.tableWidget.item(selected_row, 3).text()
        updateGender = self.tableWidget.item(selected_row, 4).text()
        updateProgramCode = self.tableWidget.item(selected_row, 5).text()

        studentEditor = UpdateStudentDialog(updateIDNumber, updateFirstName, updateLastName,
                                            updateYearLevel, updateGender, updateProgramCode)
        if studentEditor.exec_():
            updated_values = studentEditor.updatedStudentData()

            if updated_values != [updateIDNumber, updateFirstName, updateLastName,
                                updateYearLevel, updateGender, updateProgramCode]:

                data_source[selected_row] = updated_values

                if is_filtered:
                    full_data = self.data[self.current_table_index]
                    for i, row in enumerate(full_data):
                        if row[0] == updateIDNumber:
                            full_data[i] = updated_values
                            break

                self.saveStudentCSV(self.data[self.current_table_index])
                self.readStudentCSV()
                self.displayTable()
                self.updateStudentSuccess()


    def updateProgramEntry(self):
        selected_row = self.tableWidget.currentRow()

        data = getattr(self, "filtered_data", None) or self.data[1]

        if 0 <= selected_row < len(data):
            updateProgramCode = self.tableWidget.item(selected_row, 0).text()
            updateProgramName = self.tableWidget.item(selected_row, 1).text()
            updateCollegeCode = self.tableWidget.item(selected_row, 2).text()

            programEditor = UpdateProgramDialog(updateProgramCode, updateProgramName, updateCollegeCode)
            if programEditor.exec_():
                updated_values = programEditor.updatedProgramData()

                if updated_values != [updateProgramCode, updateProgramName, updateCollegeCode]:
                    data[selected_row] = updated_values

                    for i, row in enumerate(self.data[1]):
                        if row[0] == updateProgramCode:
                            self.data[1][i] = updated_values
                            break

                    for row in self.data[0]:
                        if row[5] == updateProgramCode:
                            row[5] = updated_values[0]

                    self.saveProgramCSV(self.data[1])
                    self.saveStudentCSV(self.data[0])

                    self.readProgramCSV()
                    self.readStudentCSV()
                    self.displayTable()
                    self.updateProgramSuccess()

    # def updateCollegeEntry(self):
    #     self.readCollegeCSV()
    #     selected_row = self.tableWidget.currentRow()

    #     data = self.data[2]

    #     if 0 <= selected_row < len(data):
    #         updateCollegeCode = self.tableWidget.item(selected_row, 0).text()
    #         updateCollegeName = self.tableWidget.item(selected_row, 1).text()

    #         collegeEditor = UpdateCollegeDialog(updateCollegeCode, updateCollegeName)
    #         if collegeEditor.exec_():
    #             updated_values = collegeEditor.updatedCollegeData()
                
    #             if updated_values != [updateCollegeCode, updateCollegeName]:
    #                 data[selected_row] = updated_values

    #                 for row in self.data[1]:
    #                     if row[2] == updateCollegeCode:
    #                         row[2] = updated_values[0]

    #                 self.saveCollegeCSV(data)
    #                 self.saveProgramCSV(self.data[1])
    #                 self.displayTable()
    #                 self.updateCollegeSuccess()

    def updateCollegeEntry(self):
        selected_row = self.tableWidget.currentRow()

        # Work with filtered data if available
        data = getattr(self, "filtered_data", None) or self.data[2]

        if 0 <= selected_row < len(data):
            updateCollegeCode = self.tableWidget.item(selected_row, 0).text()
            updateCollegeName = self.tableWidget.item(selected_row, 1).text()

            collegeEditor = UpdateCollegeDialog(updateCollegeCode, updateCollegeName)
            if collegeEditor.exec_():
                updated_values = collegeEditor.updatedCollegeData()

                if updated_values != [updateCollegeCode, updateCollegeName]:
                    # Update the row in the filtered/full dataset
                    data[selected_row] = updated_values

                    # Sync the change back to master self.data[2]
                    for i, row in enumerate(self.data[2]):
                        if row[0] == updateCollegeCode:  # Match old CollegeCode
                            self.data[2][i] = updated_values
                            break

                    # Update all program rows that reference this CollegeCode
                    for row in self.data[1]:
                        if row[2] == updateCollegeCode:
                            row[2] = updated_values[0]

                    # Save both datasets
                    self.saveCollegeCSV(self.data[2])
                    self.saveProgramCSV(self.data[1])

                    # Reload so UI stays in sync
                    self.readCollegeCSV()
                    self.readProgramCSV()
                    self.displayTable()
                    self.updateCollegeSuccess()
    
    def addEntry(self):
        if self.displayComboBox.currentIndex() == 0:
            self.addStudentEntry()
            return
        elif self.displayComboBox.currentIndex() == 1:
            self.addProgramEntry()
            return
        elif self.displayComboBox.currentIndex() == 2:
            self.addCollegeEntry()
            return
    
    def sortLayout(self):
        column_index = self.sortComboBox.currentIndex()
        if column_index >= 0:
            self.sortData(column_index)
            self.showTable()

    
    def sortData(self, column_index):
        full_data = self.data[self.current_table_index]

        self.data[self.current_table_index] = sorted(full_data, key=lambda row: row[column_index])

#--------------------------------------------------------------------------------     STUDENT     ----------------------------------------------------------------------

#--------------------------------------------------------------------------------     STUDENT     ----------------------------------------------------------------------
    def addStudentEntry(self):
        studentAdder = AddStudentDialog()
        if studentAdder.exec_():
            new_values = studentAdder.addStudentData()
            self.data[0].append(new_values)

            self.saveStudentCSV(self.data[0])
            self.readStudentCSV() 
            self.displayTable()
            self.addStudentSuccess()

    def readStudentCSV(self):
        with open(STUDENT_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            self.headers[0] = next(reader)
            self.data[0] = [row for row in reader] 
    
    def saveStudentCSV(self, data):
        with open(STUDENT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.headers[0])
            writer.writerows(data)
    
    def deleteStudentEntry(self):
        selected_row = self.tableWidget.currentRow()
        self.readStudentCSV()
        
        data = self.data[0]
                
        # Remove selected row from data list
        if 0 <= selected_row < len(data):
            del data[selected_row]

        self.saveStudentCSV(data)
        self.displayTable()
        self.deleteStudentSuccess()

    
#--------------------------------------------------------------------------------     PROGRAM     ----------------------------------------------------------------------

#--------------------------------------------------------------------------------     PROGRAM     ----------------------------------------------------------------------

    def addProgramEntry(self):
        self.readProgramCSV()

        programAdder = AddProgramDialog()
        if programAdder.exec_():
            new_values = programAdder.addProgramData()
            self.data[1].append(new_values)

            self.saveProgramCSV(self.data[1])
            self.displayTable()
            self.addProgramSuccess()

    def readProgramCSV(self):
        with open(PROGRAM_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            self.headers[1] = next(reader)
            data = [row for row in reader]
            self.data[1] = data

    def saveProgramCSV(self, data):
        with open(PROGRAM_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.headers[1])
            writer.writerows(data)
    
    def deleteProgramEntry(self):
        selected_row = self.tableWidget.currentRow()
        self.readProgramCSV()

        program_code_to_replace = self.tableWidget.item(selected_row, 0).text()

        data = self.data[1]
        if 0 <= selected_row < len(data):
            del data[selected_row]

        self.studentCounter = 0
        for row in self.data[0]:
            if row[5] == program_code_to_replace:
                row[5] = "UNENROLLED"
                self.studentCounter += 1
            
        self.saveProgramCSV(data)
        self.saveStudentCSV(self.data[0])
        self.displayTable()
        self.deleteProgramSuccess()

#--------------------------------------------------------------------------------     COLLEGE     ----------------------------------------------------------------------

#--------------------------------------------------------------------------------     COLLEGE     ----------------------------------------------------------------------

    def addCollegeEntry(self):
        self.readCollegeCSV()

        collegeAdder = AddCollegeDialog()
        if collegeAdder.exec_():
            new_values = collegeAdder.addCollegeData()
            self.data[2].append(new_values)

            self.saveCollegeCSV(self.data[2])
            self.displayTable()
            self.addCollegeSuccess()
    
    def readCollegeCSV(self):
        with open(COLLEGE_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            self.headers[2] = next(reader)
            data = [row for row in reader]
            self.data[2] = data

    def saveCollegeCSV(self, data):
        with open(COLLEGE_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.headers[2])
            writer.writerows(data)
    
    def deleteCollegeEntry(self):
        selected_row = self.tableWidget.currentRow()
        self.readProgramCSV()
        self.readCollegeCSV()

        college_code = self.tableWidget.item(selected_row, 0).text()
        
        # Remove from college data
        for row_idx in reversed(range(len(self.data[2]))):  
            if self.data[2][row_idx][0] == college_code:
                del self.data[2][row_idx]

        # Find programs linked to the deleted college
        program_codes_to_remove = set()
        for row in self.data[1]:
            if row[2] == college_code:
                program_codes_to_remove.add(row[0])

        # Delete related programs
        self.programCounter = 0
        for row_idx in reversed(range(len(self.data[1]))):  
            if self.data[1][row_idx][0] in program_codes_to_remove:
                del self.data[1][row_idx]
                self.programCounter += 1

        # Update related students to be 'UNENROLLED'
        self.studentCounter = 0
        for row in self.data[0]:
            if row[5] in program_codes_to_remove:
                row[5] = "UNENROLLED"
                self.studentCounter += 1
        
        self.saveCollegeCSV(self.data[2])
        self.saveProgramCSV(self.data[1])
        self.saveStudentCSV(self.data[0])
        self.displayTable()
        self.deleteCollegeSuccess()

#----------------------------------------------------------------------- EDIT STUDENT ----------------------------------------------------------------------

#----------------------------------------------------------------------- EDIT STUDENT ------------------------------------------------------------------

# class UpdateStudentDialog(QDialog, Ui_UpdateStudentDialog):
#     def __init__(self, idNumber, firstName, lastName, yearLevel, gender, programCode):
#         super().__init__()
#         self.setupUi(self)

#         self.programChoices()

#         self.updateIDNumber.setText(idNumber)
#         self.updateFirstName.setText(firstName)
#         self.updateLastName.setText(lastName)
#         self.updateYearLevelComboBox.setCurrentText(yearLevel)
#         self.updateGender.setText(gender)
#         self.updateProgramCodeComboBox.setCurrentText(programCode)
        
#         self.updateFirstName.setReadOnly(True)
#         self.updateLastName.setReadOnly(True)
#         self.updateIDNumber.setReadOnly(True)
#         self.updateGender.setReadOnly(True)

#         self.pushButton.clicked.connect(self.accept)       
#         self.pushButton_2.clicked.connect(self.reject)

#     def programChoices(self):
#         with open(PROGRAM_CSV, "r", newline='') as file:
#             reader = csv.reader(file)
#             next(reader, None)
#             program_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))

#             self.updateProgramCodeComboBox.clear()
#             self.updateProgramCodeComboBox.addItems(program_codes)

#     def updatedStudentData(self):
#         return [
#             self.updateIDNumber.text(),
#             self.updateFirstName.text(),
#             self.updateLastName.text(),
#             self.updateYearLevelComboBox.currentText(),
#             self.updateGender.text(),
#             self.updateProgramCodeComboBox.currentText(),
#         ]

# class AddStudentDialog(QDialog, Ui_AddStudentDialog):
#     def __init__(self):
#         super().__init__()
#         self.setupUi(self)

#         regex = QRegExp(r"^\d{4}-\d{4}$")
#         validator = QRegExpValidator(regex)
#         self.IDNumber.setValidator(validator)

#         self.programChoices()
#         self.readStudentCSV()

#         # Sets combo box default text to empty
#         self.yearLevel.setCurrentIndex(-1)
#         self.gender.setCurrentIndex(-1)
#         self.programCode.setCurrentIndex(-1)

#         self.pushButton.clicked.connect(self.validateStudentData)
#         self.pushButton_2.clicked.connect(self.reject)
    
#     def programChoices(self):
#         with open(PROGRAM_CSV, "r", newline='') as file:
#             reader = csv.reader(file)
#             next(reader, None)
#             program_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))
#             self.programCode.clear()
#             self.programCode.addItems(program_codes)

#     def readStudentCSV(self):
#         with open(STUDENT_CSV, newline="", encoding='utf-8') as csvfile:
#             reader = csv.reader(csvfile)
#             next(reader, None)
#             data = [row for row in reader]
#             self.studentData = data

#     def addStudentData(self):
#         IDNumber = self.IDNumber.text()
#         firstName = self.firstName.text().strip().title()
#         lastName = self.lastName.text().strip().title()
#         yearLevel = self.yearLevel.currentText()
#         gender = self.gender.currentText()
#         programCode = self.programCode.currentText()
        
#         if not (IDNumber and firstName and lastName and yearLevel and gender and programCode):
#             QMessageBox.warning(self, "Input Error", "All required fields must be field up.")
#             return

#         if not re.fullmatch(r'20\d{2}-\d{4}', IDNumber):
#             QMessageBox.warning(self, "Input Error", "Input a valid ID Number.")
#             return
        
#         # Validates first name and last name, should not contain any numbers
#         if not all(char.isalpha() or char.isspace() for char in firstName and lastName):
#             QMessageBox.warning(self, "Input Error", "Input a valid name.")
#             return
        
#         for row in self.studentData:
#             existingIDNumber = row[0]

#             if existingIDNumber == IDNumber:
#                 QMessageBox.warning(self, "Input Error", "The ID Number you're trying to enter already exists.")
#                 return

#         return [
#             IDNumber, firstName, lastName, yearLevel, gender, programCode
#         ]
    
#     def validateStudentData(self):
#         new_data = self.addStudentData()
#         if new_data:
#             self.accept()

#----------------------------------------------------------------------- EDIT PROGRAM ----------------------------------------------------------------------

#----------------------------------------------------------------------- EDIT PROGRAM ------------------------------------------------------------------
             
# class UpdateProgramDialog(QDialog, Ui_UpdateProgramDialog):
#     def __init__(self, programCode, programName, collegeCode):
#         super().__init__()
#         self.setupUi(self)
#         self.collegeChoices()

#         # Store the original values for comparison
#         self.originalProgramCode = programCode
#         self.originalProgramName = programName
#         self.originalCollegeCode = collegeCode

#         # Input current data on to the line edits.
#         self.programCodeEdit.setText(programCode)
#         self.programNameEdit.setText(programName)
#         self.collegeCodeBox.setCurrentText(collegeCode)

#         # Validates if input is not empty
#         self.confirmButton.clicked.connect(self.validateProgramData)       
#         self.cancelButton.clicked.connect(self.reject)

#     def collegeChoices(self):
#         with open(COLLEGE_CSV, "r", newline='') as file:
#             reader = csv.reader(file)
#             next(reader, None)
#             college_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))

#             self.collegeCodeBox.clear()
#             self.collegeCodeBox.addItems(college_codes)
    
#     def readProgramCSV(self):
#         with open(PROGRAM_CSV, newline='', encoding='utf-8') as csvfile:
#             reader = csv.reader(csvfile)
#             next(reader, None)
#             data = [row for row in reader]
#             self.programData = data

#     def updatedProgramData(self):
#         self.readProgramCSV()

#         newProgramCode = self.programCodeEdit.text().strip().replace(" ", "").upper()
#         newProgramName = self.programNameEdit.text().strip().title()
#         newCollegeCode = self.collegeCodeBox.currentText()

#         # If no changes are made, return the original values
#         if (newProgramCode == self.originalProgramCode and
#             newProgramName == self.originalProgramName and
#             newCollegeCode == self.originalCollegeCode):
#             return [self.originalProgramCode, self.originalProgramName, self.originalCollegeCode]

#         if not (newProgramCode and newProgramName and newCollegeCode):
#             QMessageBox.warning(self, "Input Error", "All fields must be filled up.")
#             return None
        
#         # Validates if program code and name contains digits
#         if not all(char.isalpha() or char.isspace() for char in newProgramCode and newProgramName):
#             QMessageBox.warning(self, "Input Error", "Please input a valid program name.")
#             return None

#         for row in self.programData:
#             existingProgramCode = row[0].strip().upper()
#             existingProgramName = row[1].strip().replace(" ", "").upper()

#             if existingProgramCode == self.originalProgramCode:
#                 continue  

#             # Check if the program code already exists
#             if existingProgramCode == newProgramCode:
#                 QMessageBox.warning(self, "Input Error", "The program code you are trying to add already exists.")
#                 return None

#             # Check if the program name already exists
#             if existingProgramName == newProgramName.replace(" ", "").upper():
#                 QMessageBox.warning(self, "Input Error", "The program name you are trying to enter already exists.")
#                 return None

#         return [newProgramCode, newProgramName, newCollegeCode]
    
#     def validateProgramData(self):
#         updated_data = self.updatedProgramData()
#         if updated_data:
#             self.accept()

# class AddProgramDialog(QDialog, Ui_AddProgramDialog):
#     def __init__(self):
#         super().__init__()
#         self.setupUi(self)

#         self.readProgramCSV()
#         self.collegeChoices()

#         # Resets college combo box default text to empty
#         self.collegeCode.setCurrentIndex(-1)

#         self.pushButton.clicked.connect(self.validateProgramData)
#         self.pushButton_2.clicked.connect(self.reject)
    
#     def collegeChoices(self):
#         with open(COLLEGE_CSV, "r", newline='') as file:
#             reader = csv.reader(file)
#             next(reader, None)
#             college_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))
#             self.collegeCode.clear()
#             self.collegeCode.addItems(college_codes)
    
#     def readProgramCSV(self):
#         with open(PROGRAM_CSV, newline='', encoding='utf-8') as csvfile:
#             reader = csv.reader(csvfile)
#             next(reader, None)
#             data = [row for row in reader]
#             self.programData = data

#     def addProgramData(self):
#         programCode = self.programCode.text().strip().replace(" ","").upper()
#         programName = self.programName.text().strip().title()
#         collegeCode = self.collegeCode.currentText()

#         if not (programCode and programName and collegeCode):
#             QMessageBox.warning(self, "Input Error", "All fields must be filled up.")
#             return
        
#         if not all(char.isalpha() or char.isspace() for char in programCode and programName):
#             QMessageBox.warning(self, "Input Error", "Please input a valid program name.")
#             return
        
#         for row in self.programData:
#             existingProgramCode = row[0].strip().upper()
#             existingProgramName = row[1].strip().replace(" ", "").upper()

#             # Check if the program code already exists
#             if existingProgramCode == programCode:
#                 QMessageBox.warning(self, "Input Error", "The program code you are trying to add already exists.")
#                 return

#             # Check if the program name already exists
#             if existingProgramName == programName.replace(" ", "").upper():
#                 QMessageBox.warning(self, "Input Error", "The program name you are trying to enter already exists.")
#                 return
            
#         return [programCode, programName, collegeCode]

#     def validateProgramData(self):
#         new_data = self.addProgramData()
#         if new_data:
#             self.accept()
#----------------------------------------------------------------------- EDIT COLLEGE -----------------------------------------------------------------------------------------------

#----------------------------------------------------------------------- EDIT COLLEGE -----------------------------------------------------------------------------------------------

# class UpdateCollegeDialog(QDialog, Ui_UpdateCollegeDialog):
#     def __init__(self, collegeCode, collegeName):
#         super().__init__()
#         self.setupUi(self)

#         self.originalCollegeCode = collegeCode
#         self.originalCollegeName = collegeName
        
#         # Input current data on to the line edits.
#         self.collegeCodeEdit.setText(collegeCode)
#         self.collegeNameEdit.setText(collegeName)

#         self.confirmButton.clicked.connect(self.validateCollegeData)       
#         self.cancelButton.clicked.connect(self.reject)

#     def readCollegeCSV(self):
#         with open(COLLEGE_CSV, newline='', encoding='utf-8') as csvfile:
#             reader = csv.reader(csvfile)
#             next(reader, None)
#             data = [row for row in reader]
#             self.collegeData = data

#     def updatedCollegeData(self):
#         self.readCollegeCSV()

#         newCollegeCode = self.collegeCodeEdit.text().strip().replace(" ","").upper()
#         newCollegeName = self.collegeNameEdit.text().strip().title()

#         # If no changes were made, return the original values
#         if (newCollegeCode == self.originalCollegeCode and newCollegeName == self.originalCollegeName):
#             return [self.originalCollegeCode, self.originalCollegeName]
        
#         if not newCollegeCode or not newCollegeName:
#             QMessageBox.warning(self, "Input Error", "All fields must be filled up.")
#             return None
        
#         # Validates if the input contains numbers
#         if not all(char.isalpha() or char.isspace() for char in newCollegeCode and newCollegeName):
#             QMessageBox.warning(self, "Input Error", "Please input a valid college name.")
#             return None

#         for row in self.collegeData:
#             existingCollegeCode = row[0].strip().upper()
#             existingCollegeName = row[1].strip().replace(" ","").upper()

#             if existingCollegeCode == self.originalCollegeCode:
#                 continue  

#             # Check if the college code already exists
#             if existingCollegeCode == newCollegeCode:
#                 QMessageBox.warning(self, "Input Error", "The college code you are trying to add already exists.")
#                 return None

#             # Check if the college name already exists
#             if existingCollegeName == newCollegeName.replace(" ", "").upper():
#                 QMessageBox.warning(self, "Input Error", "The college name you are trying to enter already exists.")
#                 return None

#         return [newCollegeCode, newCollegeName]
    
#     def validateCollegeData(self):
#         updated_data = self.updatedCollegeData()
#         if updated_data:
#             self.accept()

# class AddCollegeDialog(QDialog, Ui_AddCollegeDialog):
#     def __init__(self):
#         super().__init__()
#         self.setupUi(self)

#         self.readCollegeCSV()

#         self.pushButton.clicked.connect(self.validateCollegeData)
#         self.pushButton_2.clicked.connect(self.reject)

#     def readCollegeCSV(self):
#         with open(COLLEGE_CSV, newline='', encoding='utf-8') as csvfile:
#             reader = csv.reader(csvfile)
#             next(reader, None)
#             data = [row for row in reader]
#             self.collegeData = data
    
#     def addCollegeData(self):
#         collegeCode = self.collegeCode.text().strip().replace(" ","").upper()
#         collegeName = self.collegeName.text().strip().title()

#         if not collegeCode or not collegeName:
#             QMessageBox.warning(self, "Input Error", "All fields must be filled up.")
#             return
        
#         if not all(char.isalpha() or char.isspace() for char in collegeCode and collegeName):
#             QMessageBox.warning(self, "Input Error", "Please input a valid college name.")
#             return

#         for row in self.collegeData:
#             existingCollegeCode = row[0].strip().upper()
#             existingCollegeName = row[1].strip().replace(" ", "").upper()

#             # Check if the college code already exists
#             if existingCollegeCode == collegeCode:
#                 QMessageBox.warning(self, "Input Error", "The program code you are trying to add already exists.")
#                 return

#             # Check if the college name already exists
#             if existingCollegeName == collegeName.replace(" ", "").upper():
#                 QMessageBox.warning(self, "Input Error", "The program name you are trying to enter already exists.")
#                 return
        
#         return [collegeCode, collegeName]
        
#     def validateCollegeData(self):
#         new_values = self.addCollegeData()
#         if new_values:
#             self.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainClass()
    main.show()
    app.exec_()