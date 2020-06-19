#region imports + variables
import requests, zipfile, io
import time
import json
import queue
import sys
import os
from os import listdir
from os.path import isfile, join
from zipfile import ZipFile
import simplejson
from Klasses.CreateCSV import CreateCSV
import threading
import logging
import hashlib
import shutil
from gui import *
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon

dirname = ""
OutputDir = ""
SessionIdCookie = ""
user = "cedric.de.meester@student.howest.be"
pw = "school123"
collID = 63919
docID = 0
modelID = ""
pageids = []
uploadTitle = ""
year = ""
altoFolder = ""
loggedIn = False
progress = 0
jobDescription = ""
allowedToDownload = False
exportFinished = False
pagesCount = ""
running = False
#endregion
#region Login and logout
def login():
    try:
        url = "https://transkribus.eu/TrpServer/rest/auth/login"
        response = requests.post(url, data = {'user':user, 'pw':pw})
        if response.status_code == 200:
            global SessionIdCookie
            SessionIdCookie = response.cookies
            print("Logged in to Transkribus as " + user)
            loggedIn = True
            return True
        else:
            print("Failed to login as " + user)
            loggedIn = False
            return False
    except Exception as ex :
        print("Error logout", ex)

def logout():
    try:
        url = "https://transkribus.eu/TrpServer/rest/auth/logout"
        response = requests.post(url, cookies=SessionIdCookie)
        if response.status_code == 200:
            print("Current client logged out")
            loggedIn = False
        else:
            print("Logout failed")
    except Exception as ex:
        print("Error logout", ex)

#endregion

def addToBar(amount):
    #ui.centralwidget.painter = QtGui.QPainter()
    #ui.centralwidget.painter.begin(MainWindow)
    global progress
    amount = float(amount)
    progress += amount
    ui.progressBar.setProperty("value", progress)
    #ui.centralwidget.painter.end()

def setBarTo(amount):
    #ui.centralwidget.painter = QtGui.QPainter()
    #ui.centralwidget.painter.begin(MainWindow)
    global progress
    amount = float(amount)
    ui.progressBar.setMaximum(100)
    ui.progressBar.setProperty("value", amount)
    progress = amount
    #ui.centralwidget.painter.end()

def addJobDescription(desc, task=None):
    global jobDescription
    global pagesCount
    try:
        if jobDescription != desc:
            #ui.centralwidget.painter = QtGui.QPainter()
            #ui.centralwidget.painter.begin(MainWindow)
            ui.textEdit.append(desc)
            if task != None:
                if task == "upload":
                    progress = 14/pagesCount
                    if "Uploaded PAGE XML for page" in desc:
                        addToBar(progress)
                elif task == "htr":
                    progress = 48/pagesCount
                    if "HTR done on page:" in desc:
                        addToBar(progress)
                elif task == "export":
                    progress = 7/5
                    if "Starting" in desc:
                        addToBar(progress)
                    elif "Exporting document" in desc:
                        addToBar(progress)
                    elif "zip file" in desc:
                        addToBar(progress)
                    elif "wrapping up" in desc:
                        addToBar(progress)
                    elif "Done, duration:" in desc:
                        addToBar(progress)
                    elif "error" in desc:
                        setBarTo(86)
            #ui.centralwidget.painter.end()
    except Exception as ex:
        print("error in addJobDescription: ", ex)
    jobDescription = desc
    ui.textEdit.ensureCursorVisible()

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def start():
    global exportFinished
    dirname = ui.dirname
    OutputDir = ui.OutputDir
    running = True
    exportFinished = False
    allowedToDownload = False
    jobDescription = ""
    docID = 0
    modelID = ""
    pageids = []
    uploadTitle = ""
    year = ""
    altoFolder = ""
    threading.Thread(target=upload).start()

def upload():
    global progress
    global uploadTitle
    global pagesCount
    dirname = ui.dirname    #deze dirnames zijn andere vars dan die helemaal vanboven omdat ze op een verschillende thread staan!
    OutputDir = ui.OutputDir
    try:
        pageNr = 0
        addToBar(1)
        url = ("https://transkribus.eu/TrpServer/rest/uploads?collId=%s" % collID)
        headers = {'Content-Type': 'application/json'}
        uploadTitle = ""
        data = ""
        allFiles = [f for f in listdir(dirname) if isfile(join(dirname, f)) and f.endswith('.tif')]
        pagesCount = len(allFiles)
        for file in allFiles:
            addJobDescription("Calculating cheksum...")
            checksum = md5(dirname + "/" + file)
            #pageNr = file[-7:-4].lstrip("0")
            pageNr += 1
            ext = file[-3:]
            if uploadTitle == "" and ext == "tif":
                uploadTitle = file[:-8]
                uploadBook = uploadTitle[-1:]
                data = ('{"md": {"title": "%s", "book": "%s"}, '
                        '"pageList": {"pages": ['
                        '{"fileName": "%s", "pageNr": "%s", "imgChecksum": "%s"} ' % (uploadTitle, uploadBook, file, pageNr, checksum))
            elif uploadTitle != "" and ext == "tif":
                data += (', {"fileName": "%s", "pageNr": "%s", "imgChecksum": "%s"}' %(file, pageNr, checksum))
        data += "]}}"
        data = eval(data)
        response = requests.post(url, cookies=SessionIdCookie, headers=headers, json=data)
        if response.status_code == 200:
            uploadID = str(response.content).split("uploadId")[1][1:-2]
            print("Upload process created!")
        else:
            print("Upload process creating failed!")    
        
        addJobDescription("Uploading " + str(pagesCount) + " pages...")
        url = ("https://transkribus.eu/TrpServer/rest/uploads/%s" % uploadID)
        for indx, file in enumerate(allFiles):
            with open(dirname + "/" + file, "rb") as f:
                response = requests.put(url, cookies=SessionIdCookie, files={"img": f})
                if response.status_code == 200:
                    addJobDescription(("Image uploaded! (%s of %s)"%(indx + 1, str(len(allFiles)))))
                    print("1 image uploaded!")
                else:
                    print("Upload of 1 image failed!")
                    addJobDescription(("Image upload failed (%s of %s)"%(indx + 1, str(len(allFiles)))))
                    addJobDescription(("Trying to upload again (%s of %s)"%(indx + 1, str(len(allFiles)))))
                    response = requests.put(url, cookies=SessionIdCookie, files={"img": f})
                    if response.status_code == 200:
                        addJobDescription(("Image uploaded! (%s of %s)"%(indx + 1, str(len(allFiles)))))
                        print("1 image uploaded!")
                    else:
                        print("Upload of 1 image failed AGAIN!")
                        addJobDescription(("Image upload failed AGAIN (%s of %s)"%(indx + 1, str(len(allFiles)))))
                progress_files = (23/len(allFiles))
                addToBar(progress_files)  #24% van de bar hierna
                
            if indx + 1 == len(allFiles):
                try:
                    addJobDescription("Performing image processing...")
                    jobId = str(response.content).split("jobId")[1][1:-2]
                    job_status(jobId, task="upload")
                    try:
                        urlPageId = ("https://transkribus.eu/TrpServer/rest/collections/%s/%s/pageIds" % (collID, docID))
                        response_page_id = requests.get(urlPageId, cookies=SessionIdCookie )
                        pageids = json.loads(response_page_id.content)
                        # layout_analysis(docID)
                        handwritten_text_recognition(docID)
                    except:
                        print("error getting pageIds")                    
                except Exception as ex:
                    print("Error ", ex)      
                
    except Exception as ex:
        addJobDescription(("Error: " + str(ex)))
        print("Error uploading", ex)
        
#region LA
# def layout_analysis(docID):
#     print("nu LA uitvoeren")
#     addJobDescription("Performing Layout Analysis...")
#     # nodige parameters aanmaken
#     urlPageId = ("https://transkribus.eu/TrpServer/rest/collections/%s/%s/pageIds" % (collID, docID))
#     response_page_id = requests.get(urlPageId, cookies=SessionIdCookie )
#     pageids = json.loads(response_page_id.content)
#     data = ('{"docList":{"docs":[{"docId" : %s , "pageList" : { "pages":[' % (docID))
#     for id in pageids:
#         if id == (pageids[len(pageids)-1]):
#             data += ('{"pageId" : %s}' % (id))
#         else:
#             data += ('{"pageId" : %s},' % (id))
#     data += "]}}]}}"
#     data = eval(data)
#     params = {'collId': collID}
#     url = "https://transkribus.eu/TrpServer/rest/LA"
#     headers = {'Content-Type': 'application/json'}
#     try:
#         response = requests.post(url, headers=headers, cookies=SessionIdCookie, params=params, json=data)
#         print(response.content)
#         if response.status_code == 200:
#             addJobDescription("Layout Analysis done!")
#             print("layout analysis worked")
#             print("jobid eruithalen", response.content)
#             jobId = str(response.content).split("jobId")[1][1:-2]
#             print(jobId)
#             job_status(jobId)

#         else:
#             print("layout analysis failed")
#             addJobDescription("Layout Analysis failed!")
#     except:
#         print("Error in layout analysis")
#endregion

def job_status(jobId, link=None, task=None):
    try:
        global docID 
        if jobId != "":
            print("waiting for job to finish")
            urlJob = ("https://transkribus.eu/TrpServer/rest/jobs/%s" % jobId)
            responseJob = requests.get(urlJob, cookies=SessionIdCookie)
            docID = json.loads(responseJob.content)
            docID = docID["docId"]
            print("job content: --- ", str(responseJob.content))
            success = False
            #ui.centralwidget.painter = QtGui.QPainter()
            #ui.centralwidget.painter.begin(MainWindow)
            counter = 0
            while success == False:
                #ui.centralwidget.painter = QtGui.QPainter()
                #ui.centralwidget.painter.begin(MainWindow)
                responseJob = requests.get(urlJob, cookies=SessionIdCookie)
                result = json.loads(responseJob.content)
                try:
                    addJobDescription(str(result["description"]), task)
                except:
                    pass
                #time.sleep(0.2)
                success = result["success"]
                counter += 1
                if counter == 10:
                    #ui.centralwidget.painter.end()
                    counter = 0
                
            if link == True:
                print("getting link")
                answer = False
                while answer == False:
                    print("getting link")
                    responseJob = requests.get(urlJob, cookies=SessionIdCookie)
                    result = json.loads(responseJob.content)
                    print("responsejob in getting link: ---------------------- ", str(responseJob.content))
                    if "error" in str(responseJob.content):
                        print("error in response job for export: -------------------------- ")
                        print(str(responseJob.content))
                        return False
                    else:
                        return True
                    try:
                        print("download link: --- ", str(result["result"]))
                        answer = True
                        time.sleep(1)
                    except Exception as ex:
                        print("Error getting download link ", ex)
    except Exception as ex:
        print("Error in job status: ", ex)

def handwritten_text_recognition(docID):
    try:
        # nodige parameters aanmaken
        get_pageids(docID)
        pageidslen = len(pageids)
        print("lengte van pages :" , pageidslen)
        data = ('{"docId" : %s , "pageList" : { "pages":[' % (docID))
        for id in pageids:
            if id == (pageids[len(pageids)-1]):
                data += ('{"pageId" : %s}' % (id))
            else:
                data += ('{"pageId" : %s},' % (id))
        data += "]}}"
        data = eval(data)
        year = uploadTitle[0:4]
        if year == "1846":
            print("HTR model for year 1846")
            modelID = 24569
        elif year == "1866":
            print("HTR model for year 1866")
            modelID = 24471
        elif year == "1880": 
            print("HTR model for year 1880")
            modelID = 24107
        else:
            print("HTR model for all years")
            modelID = 24563
        url = ("https://transkribus.eu/TrpServer/rest/recognition/%s/%s/htrCITlab" % (collID, modelID))
        headers = {'Content-Type': 'application/json'}
        setBarTo(38)
        try:
            #ui.centralwidget.painter = QtGui.QPainter()
            #ui.centralwidget.painter.begin(MainWindow)
            #ui.centralwidget.painter.end()
            addJobDescription("Performing HTR...")
            #ui.centralwidget.painter.end()
            response = requests.post(url, headers=headers, cookies=SessionIdCookie, json=data)
            print("HTR response : ---- ", response.content)
            if response.status_code == 200:
                print("htr started")
                filtered_jobID = str(response.content)
                filtered_jobID2 = filtered_jobID.replace("b","").replace("'","")
                type(filtered_jobID2)
                print("filtered job : ---- ",filtered_jobID2)
                job_status(filtered_jobID2, task="htr")
                print("going to export function now")
                export_to_xml(docID, pageidslen)
            else:
                print("htr failed")
                addJobDescription("HTR failed!")
            #pass
        except:
            print("HTR failed")
    except Exception as ex:
        print("Error in HTR: ", ex)

def export_to_xml(docID, aantal_bestanden):
    try:
        global exportFinished
        while exportFinished != True:
            addJobDescription("Performing server export...")
            print("exporteren van bestanden naar xml files")
            url_exports = ("https://transkribus.eu/TrpServer/rest/collections/%s/%s/export" % (collID, docID))
            pages = ('1-%s' % (aantal_bestanden))
            params = { 'pages': pages,'doWriteMets' : True , 'doWriteImages': False, 'doExportAltoXml':False,'splitIntoWordsInAltoXml': True, 'doPdfImagesPlusText': False, 'doTeiWithZonePerLine': False, 'doTeiWithLineTags':False, 'doDocxKeepAbbrevs': False}
            header = {'Content-Type': 'application/json'}
            data = ('{"docId" : %s , "pageList" : { "pages":[' % (docID))
            for id in pageids:
                if id == (pageids[len(pageids)-1]):
                    data += ('{"pageId" : %s}' % (id))
                else:
                    data += ('{"pageId" : %s},' % (id))
            data += "]}}"
            data = eval(data)
            setBarTo(86)
            try:
                response_exports = requests.post(url_exports, headers=header, cookies=SessionIdCookie, json=data ,params=params)
                print("Export response : ---- ", response_exports.content)
                if response_exports.status_code == 200:
                    filtered_jobID = str(response_exports.content)
                    filtered_jobID2 = filtered_jobID.replace("b","").replace("'","")
                    print(filtered_jobID2)
                    # print(jobId)
                    if job_status(filtered_jobID2, True, task="export") == False:
                        exportFailed()
                    else:
                        print("Export worked without failes!")
                        print("klaar voor download")
                        exportFinished = True
                        get_downloadurl(filtered_jobID2)
                        #pass
                else:
                    print("export gefaald")
                    addJobDescription("Server export failed!")
                    #pass
            except:
                print("export gefaald")
    except Exception as ex:
        print("Error in export: ", ex)

def exportFailed():
    print("export failed function")
    time.sleep(5)
    #export_to_xml(docID, pageidslen)

def get_pageids(docID):
    try:
        global pageids
        urlPageId = ("https://transkribus.eu/TrpServer/rest/collections/%s/%s/pageIds" % (collID, docID))
        response_page_id = requests.get(urlPageId, cookies=SessionIdCookie )
        pageids = json.loads(response_page_id.content)
        pageidslen = len(pageids)
        print(pageids)
        return True
    except Exception as ex:
        print("Error in getting page ids: ", ex)

def get_downloadurl(jobID):
    try:
        download_url = ("https://transkribus.eu/TrpServer/rest/jobs/%s" %(jobID))
        setBarTo(93)
        try:
            response_download = requests.get(download_url, cookies=SessionIdCookie)
            if response_download.status_code == 200:
                downloadlink = json.loads(response_download.content)
                download_link = downloadlink["result"]
                print("Download link : ---- ",download_link)
                setBarTo(94)
                download_exports(download_link)
                return True
            else:
                print("ophalen van download had geen connectie met server")
                return False
            
        except:
            print("get van download link werd niet uitgevoerd, fout in parameters")
            return False
    except Exception as ex:
        print("Error in getting download url: ", ex)

def download_exports(urlFile):
    try:
        addJobDescription("Performing download...")
        dirname = ui.dirname
        OutputDir = ui.OutputDir
        global running
        global altoFolder
        global docID
        global uploadTitle
        try:
            url = urlFile
            response = requests.get(url, stream=True)
            print("downloading en unzipping")
            with open(dirname + '/' + uploadTitle + ".zip", 'wb') as fd:
                for chunk in response.iter_content(chunk_size=128):
                    if chunk:
                        fd.write(chunk)
            fd.close()
            with ZipFile(dirname + '/' + uploadTitle + ".zip", 'r') as zipObj:
                zipObj.extractall(dirname)
            setBarTo(95)
            docID = str(docID)
            altoFolder = (dirname + "/" + docID + "/" + uploadTitle + "/alto/")
            print("altofolder : ---- ",altoFolder)
            addJobDescription("Performing post-processing...")
            create = CreateCSV(altoFolder,OutputDir)
            setBarTo(96)
            create.select_file()
            shutil.rmtree(dirname + "/" + docID)
            os.remove(dirname + "/" + uploadTitle + ".zip")
            os.remove(dirname + "/" + "log.txt")
            print("done")
            setBarTo(99)
            ui.progressBar.setVisible(False)
            addJobDescription("Finished.")
            running = "finished"
            _translate = QtCore.QCoreApplication.translate
            ui.btnStartProcess.setText(_translate("MainWindow", "Finished, Reset"))
            ui.btnStartProcess.setEnabled(True)
            ui.btnDirectory.setEnabled(True)
            ui.btnOutput.setEnabled(True)

        except Exception as ex:
            addJobDescription("Download or Post-processing failed!")
            print("Error downloading ", ex)
    except Exception as ex:
        print("Error in downloadingen en post processing: ", ex)

sys._excepthook = sys.excepthook 
def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback) 
    sys.exit(1) 
sys.excepthook = exception_hook 


class UIHandler(Ui_MainWindow):
    dirname = ""
    OutputDir = ""

    def __init__(self, window):
        self.setupUi(window)
        self.setlabels()
        self.btnDirectory.clicked.connect(self.directory)
        self.btnOutput.clicked.connect(self.OutputDirectory)
        self.btnStartProcess.clicked.connect(self.StartClicked)
        self.progressBar.setVisible(True)
        #self.progressBar.setRange(0, 100.1)
        
    def setlabels(self):
        _translate = QtCore.QCoreApplication.translate
        self.textEdit.append("Logging in as: " + user)
        if login() == True: # hier wordt de login() uitgevoerd!!!
            self.lblLoggedInAs.setText(_translate("MainWindow", "Currently logged in as: " + user))
            self.textEdit.append("Logged in successfully!")
        else:
            self.lblLoggedInAs.setText(_translate("MainWindow", "Currently logged in as: " + "failed to login"))
            self.textEdit.append("Login failed! Please contact administrator!")
    
    def directory(self):
        _translate = QtCore.QCoreApplication.translate
        self.dirname = QFileDialog.getExistingDirectory(caption='Find directory',directory=os.getcwd())
        self.txtDirectory.setText(_translate("MainWindow", self.dirname))
    
    def OutputDirectory(self):
        _translate = QtCore.QCoreApplication.translate
        self.OutputDir = QFileDialog.getExistingDirectory(caption='Select the folder where you want the output to go',directory=os.getcwd())
        self.txtOutput.setText(_translate("MainWindow", self.OutputDir))
    
    def StartClicked(self):
        global running
        _translate = QtCore.QCoreApplication.translate
        if running == False:
            self.btnStartProcess.setText(_translate("MainWindow", "Running..."))
            self.btnStartProcess.setEnabled(False)
            self.btnDirectory.setEnabled(False)
            self.btnOutput.setEnabled(False)
            start()
        elif running == "finished":
            self.textEdit.clear()
            self.txtDirectory.setText("")
            self.txtOutput.setText("")
            self.btnStartProcess.setText(_translate("MainWindow", "Start process"))
            setBarTo(0)
            self.progressBar.setVisible(True)
            running = False

app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = UIHandler(MainWindow)
MainWindow.show()
app.exec_()


