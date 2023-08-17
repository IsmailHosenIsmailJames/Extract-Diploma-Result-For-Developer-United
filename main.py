#################### get data from pdf file ##################################
import json
import PyPDF2
import re

# ------------------- pattern for diffrent data -------------------------------
# 74042 - Chakria Polytechnic Institute ,Cox's Bazar
instituteNamePattern = r'\d{5} - .+'
# 668779 (3.67)
passedrollPattern = r'\d{6} \(\d+\.\d+\)'
# 688999 { 25722(T), 25912(T),25913(T), 25921(T), 26711(T),26911(T) }
refaredRollPattern = r'\d{6} \{[^}]+\}'
# ------------------- pattern for diffrent data -------------------------------

# individual data extractor function
def extractIndividualResult(fileName:str) -> dict:
    """It will take the name of the path of PDFfile and return extracted dict with all individual results.

    Args:
        fileName (str): the name of the path of pdf file

    Returns:
        dict: It conatins the Rolls as key and data as value.
    """
    reader = PyPDF2.PdfReader(fileName)
    individualResultList = []
    individualResultJson = {}
    for page in range(len(reader.pages)):
        # getting a specific page from the pdf file
        page = reader.pages[page]
        # extracting text from page
        text = page.extract_text()
        # extracting data from text
        passed = re.findall(passedrollPattern, text)
        refeared = re.findall(refaredRollPattern, text)
        for i in range(len(refeared)):
            refeared[i] = str(refeared[i]).replace("\n", " ")

        individualResultList += (passed + refeared)
        
    # push all data into a dict for sent to server
    for i in individualResultList:
        if(len(re.findall(passedrollPattern, i)) > 0):
            roll, result = str(i).split(" ")
            result = result.replace("(", "").replace(")", "")
            individualResultJson[roll] = {"pass": True, "result": result}
        else:
            data = str(i).replace("{", ",").replace("}", "").replace(" ", "").split(",")
            individualResultJson[data[0]] = {"pass" : False, "failed" : data[1:]}
    
    # write the jason file in local dir
    with open(f"{fileName}_individual.json", "w") as file:
        json.dump(individualResultJson, file, indent= 2,sort_keys= True)
    
    return individualResultJson

# institute data extractor
def extractInstituteResult(fileName:str) -> tuple:
    """It will take input the name of the path of PDF file and extract all results from that and then it will return two dict object.
    One dict is contain all the institution results and another dict contain the code of institution as key and value is institution name.

    Args:
        fileName (str): The path name of PDF file

    Returns:
        tuple: (dict, dict)
    """
    reader = PyPDF2.PdfReader(fileName)
    instituteResultList = []
    instituteResultJson = {}
    instituteCode = {}

    futureInstituteName = ""
    for page in range(len(reader.pages)):
        # getting a specific page from the pdf file
        page = reader.pages[page]
        # extracting text from page
        text = page.extract_text()
        # extracting data from text
        instituteName = re.findall(instituteNamePattern, text)

        if(len(instituteName) > 0):
            futureInstituteName = instituteName[0]
            if(len(instituteResultList) > 0):
                temJson = {}
                # push data for every institute on the dict
                for i in instituteResultList:
                    if(len(re.findall(passedrollPattern, i)) > 0):
                        roll, result = str(i).split(" ")
                        result = result.replace("(", "").replace(")", "")
                        temJson[roll] = {"pass": True, "result": result}
                    else:
                        data = str(i).replace("{", ",").replace("}", "").replace(" ", "").split(",")
                        temJson[data[0]] = {"pass" : False, "failed" : data[1:]}
                code, name = str(instituteName[0]).split(" - ")
                instituteCode[code] = name
                instituteResultJson[code] = temJson

            instituteResultList = []
            passed = re.findall(passedrollPattern, text)
            refeared = re.findall(refaredRollPattern, text)
            for i in range(len(refeared)):
                refeared[i] = str(refeared[i]).replace("\n", " ")
            instituteResultList += (passed + refeared)
        else:
            passed = re.findall(passedrollPattern, text)
            refeared = re.findall(refaredRollPattern, text)
            for i in range(len(refeared)):
                refeared[i] = str(refeared[i]).replace("\n", " ")
            instituteResultList += (passed + refeared)
    
    if(len(instituteResultList) > 0):
        temJson = {}
        # push data for last institute on the dict
        for i in instituteResultList:
            if(len(re.findall(passedrollPattern, i)) > 0):
                roll, result = str(i).split(" ")
                result = result.replace("(", "").replace(")", "")
                temJson[roll] = {"pass": True, "result": result}
            else:
                data = str(i).replace("{", ",").replace("}", "").replace(" ", "").split(",")
                temJson[data[0]] = {"pass" : False, "failed" : data[1:]}
        instituteResultJson[futureInstituteName] = temJson
    # write the jason file in local dir
    with open(f"{fileName}_institute.json", "w") as file:
        json.dump(instituteResultJson, file, indent= 2,sort_keys= True)
        
    return (instituteResultJson, instituteCode)

#################### get data from pdf file ##################################


#################### Firebase database #######################################
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Fetch the service account key JSON file contents
cred = credentials.Certificate('C:/Users/mdism/extract diploma result/developersunited-firebase-adminsdk-jx3em-7880ffac1c.json')
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {'databaseURL': "https://developersunited-default-rtdb.asia-southeast1.firebasedatabase.app/"})


import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QFileDialog, QLineEdit, QMessageBox
class FilePicker(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('File Picker')
        self.setGeometry(300, 300, 400, 250)

        self.file_label = QLabel(self)
        self.file_label.setGeometry(20, 20, 360, 40)

        self.text_input = QLineEdit(self)
        self.text_input.setGeometry(20, 80, 360, 40)

        pick_button = QPushButton('Pick a PDF File', self)
        pick_button.setGeometry(20, 140, 360, 40)
        pick_button.clicked.connect(self.pickFile)

        ok_button = QPushButton('Ok', self)
        ok_button.setGeometry(20, 200, 360, 40)
        ok_button.clicked.connect(self.okClicked)

    def pickFile(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter('PDF files (*.pdf)')
        file_dialog.exec_()
        file_paths = file_dialog.selectedFiles()

        if file_paths:
            file_path = file_paths[0]
            self.file_label.setText(file_path)


    def okClicked(self):
        text = self.text_input.text()
        file = self.file_label.text()

        try:
            individualRef = db.reference(f'individual/{text}/')
            institutionRef = db.reference(f'institutuin/{text}/')
        
            individualRef.set(extractIndividualResult(fileName=file))
            institutionRef.set(extractInstituteResult(fileName=file))
            QMessageBox.information(self, 'Success', 'Operation successful!')
        except:
            QMessageBox.critical(self, 'Error', 'Operation failed!')
            


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FilePicker()
    window.show()
    sys.exit(app.exec_())