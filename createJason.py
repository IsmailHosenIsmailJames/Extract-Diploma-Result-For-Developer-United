#################### get data from pdf file ##################################
import json
import sys
import PyPDF2
import re
import os

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
    print("\nOpening PDF file...")
    reader = PyPDF2.PdfReader(fileName)
    print("PDF file is opened successfully...")
    individualResultList = []
    individualResultJson = {}
    totalPage = len(reader.pages)
    print("Processing data for Individual Result...")
    for pageNumber in range(totalPage):
        
        progress = pageNumber / totalPage
        sys.stdout.write("\rProgress: [{:<50}] {:.2f}%".format("=" * int(progress * 50), progress * 100))
        sys.stdout.flush()

        if pageNumber == totalPage - 1:
            sys.stdout.write("\n")
            sys.stdout.flush()
            print("Successful... All progress.")
        # getting a specific page from the pdf file
        page = reader.pages[pageNumber]
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
    totalPage = len(reader.pages)
    
    print("\n\nProcessing data for Institute Result...")
    for pageNumber in range(totalPage):
        progress = pageNumber / totalPage
        sys.stdout.write("\rProgress: [{:<50}] {:.2f}%".format("=" * int(progress * 50), progress * 100))
        sys.stdout.flush()

        if pageNumber == totalPage - 1:
            sys.stdout.write("\n")
            sys.stdout.flush()
            print("Successful... All progress.")
        # getting a specific pageNumber from the pdf file
        page = reader.pages[pageNumber]
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


# function for select a PDF file
def getFileName() -> str:
    print("\nLooking for PDF files...")
    
    listOfAllFiles =  os.listdir()
    pdfNameFiles = []
    for fileName in listOfAllFiles:
        if(fileName.endswith(".pdf")):
            pdfNameFiles.append(fileName)
            
    print(f'We found {len(pdfNameFiles)} pdf files.')
    print("---------------------------\n")
    print("Index\t- File Name")
    
    for i in range(len(pdfNameFiles)):
        print(f"{i}\t- {pdfNameFiles[i]}")
    
    indexOfFile = int(input("\nSelect a File by Enter Indexing : "))
    selectedPdfFileName = ""
    if(indexOfFile >= len(pdfNameFiles)):
        print("Out of range...")
        return
    
    selectedPdfFileName = pdfNameFiles[indexOfFile]
    print(f'You have selected this file :\t{fileName}')
    return selectedPdfFileName
    
        
# Call and get selected file name
fileName = getFileName()

if(fileName != None):
    print("\nExtracting Information From Data...\n")
    extractIndividualResult(fileName = fileName)
    extractInstituteResult(fileName= fileName)
    print("All Oparation is successfully complete...")