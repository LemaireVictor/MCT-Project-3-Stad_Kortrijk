import guiApp, sys, requests, os, hashlib, threading, json, time, shutil
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSignal
from os import listdir, path
from os.path import isfile, join
from zipfile import ZipFile
from Klasses.CreateCSV import CreateCSV

user = "project.kortrijk@gmail.com"
pw = "Howest123"
SessionIdCookie = ""
loggedIn = False
gotDir = False
dirname = ""
OutputDir = ""
collID = 63919
progress = 0
uploadTitle = ""
pagesCount = ""
jobDescription = ""
docID = 0
year = ""
modelID = ""
pageids = []
exportFinished = False
running = False

class MainUIClass(QtWidgets.QMainWindow, guiApp.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainUIClass, self).__init__(parent)
        self.setupUi(self)
        #thread
        self.threadApp = ThreadClass()
        self.threadApp.start()
        #signals
        self.threadApp.signalBar.connect(self.updateProgressBar)
        self.threadApp.signalTextEdit.connect(self.addToTextEdit)
        self.threadApp.signalLog.connect(self.loginout)
        self.threadApp.signalCursor.connect(self.cursor)
        self.threadApp.signalStartButton.connect(self.setStartButton)
        #buttons
        self.btnDirectory.clicked.connect(self.FileDirectory)
        self.btnOutput.clicked.connect(self.OutputDirectory)
        self.btnStartProcess.clicked.connect(self.StartClicked)

        self.txtDirectory.setDisabled(True)
        self.txtOutput.setDisabled(True)
    
    def updateProgressBar(self, val):
        self.progressBar.setValue(val)
    
    def addToTextEdit(self, val):
        self.textEdit.append(val)
    
    def cursor(self, val):
        if val == "down":
            self.textEdit.ensureCursorVisible()
    
    def loginout(self, val, name):
        _translate = QtCore.QCoreApplication.translate
        if(val == "login"):
            self.lblLoggedInAs.setText(_translate("MainWindow", "Currently logged in as: " + str(name)))
    
    def setStartButton(self, val):
        _translate = QtCore.QCoreApplication.translate
        self.btnStartProcess.setText(_translate("MainWindow", val))
        self.btnStartProcess.setEnabled(True)
        self.btnDirectory.setEnabled(True)
        self.btnOutput.setEnabled(True)
    
    def FileDirectory(self):
        global dirname, OutputDir, gotDir
        _translate = QtCore.QCoreApplication.translate
        dirname = QFileDialog.getExistingDirectory(caption='Find directory',directory=os.getcwd())
        self.txtDirectory.setText(_translate("MainWindow", dirname))
        if dirname != "" and OutputDir != "":
            gotDir = True
    
    def OutputDirectory(self):
        global dirname, OutputDir, gotDir
        _translate = QtCore.QCoreApplication.translate
        OutputDir = QFileDialog.getExistingDirectory(caption='Select the folder where you want the output to go',directory=os.getcwd())
        self.txtOutput.setText(_translate("MainWindow", OutputDir))
        if dirname != "" and OutputDir != "":
            gotDir = True
    
    def StartClicked(self):
        global running, progress, gotDir, dirname, OutputDir
        dirnameValid = False
        OutputDirValid = False
        if gotDir == True:
            if path.exists(dirname):
                try:
                    allFiles = [f for f in listdir(dirname) if isfile(join(dirname, f)) and f.endswith('.tif')]
                    if len(allFiles) != 0:
                        dirnameValid = True
                    else:
                        self.addToTextEdit("There are no .tif files in the directory")
                except:
                    self.addToTextEdit("There are no .tif files in the directory")
            else:
                self.addToTextEdit("Directory does not exist")
            if path.exists(OutputDir):
                OutputDirValid = True
            else:
                self.addToTextEdit("Output directory does not exist")

            if dirnameValid == True and OutputDirValid == True:
                _translate = QtCore.QCoreApplication.translate
                if running == False:
                    self.btnStartProcess.setText(_translate("MainWindow", "Running..."))
                    self.btnStartProcess.setEnabled(False)
                    self.btnDirectory.setEnabled(False)
                    self.btnOutput.setEnabled(False)
                    self.threadApp.StartMain()
                elif running == "finished":
                    self.resetVars()
                    self.textEdit.clear()
                    self.txtDirectory.setText("")
                    self.txtOutput.setText("")
                    self.btnStartProcess.setText(_translate("MainWindow", "Start process"))
                    progress = 0
                    self.progressBar.setValue(0)
                    self.progressBar.setVisible(True)
                    running = False
        else:
            self.addToTextEdit("Please select directory!")
    
    def resetVars(self):
        global running, progress, gotDir, dirname, OutputDir, uploadTitle, pagesCount, jobDescription, docID, year, modelID, pageids, exportFinished
        gotDir = False
        dirname = ""
        OutputDir = ""
        progress = 0
        uploadTitle = ""
        pagesCount = ""
        jobDescription = ""
        docID = 0
        year = ""
        modelID = ""
        pageids = []
        exportFinished = False

class ThreadClass(QtCore.QThread):
    #global app
    signalBar = pyqtSignal(float)
    signalTextEdit = pyqtSignal(str)
    signalLog = pyqtSignal(str, str)
    signalCursor = pyqtSignal(str)
    signalStartButton = pyqtSignal(str)
    def __init__(self, parent=None):
        super(ThreadClass, self).__init__(parent)
    
    def run(self):
        global loggedIn
        self.login()
        if(loggedIn == True):
            self.signalTextEdit.emit("Logged in successfully!")
        else:
            self.signalTextEdit.emit("Unable to log in to Transkribus, please contact administrator.")
    
    def StartMain(self):
        threading.Thread(target=self.upload).start()
        #self.upload()
    
    def updateBar(self, action, amount):
        global progress
        if action == "set":
            self.signalBar.emit(float(amount))
        elif action == "add":
            amount = float(amount)
            progress += amount
            self.signalBar.emit(float(progress))
    
    def addJobDescription(self, desc, task=None):
        global jobDescription, pagesCount
        try:
            if jobDescription != desc:
                self.signalTextEdit.emit(desc)
                if task != None:
                    if task == "upload":
                        progressLocal = 14/pagesCount
                        if "Uploaded PAGE XML for page" in desc:
                            self.updateBar("add",progressLocal)
                    elif task == "htr":
                        progressLocal = 48/pagesCount
                        if "HTR done on page:" in desc:
                            self.updateBar("add",progressLocal)
                    elif task == "export":
                        progressLocal = 7/5
                        if "Starting" in desc:
                            self.updateBar("add",progressLocal)
                        elif "Exporting document" in desc:
                            self.updateBar("add",progressLocal)
                        elif "zip file" in desc:
                            self.updateBar("add",progressLocal)
                        elif "wrapping up" in desc:
                            self.updateBar("add",progressLocal)
                        elif "Done, duration:" in desc:
                            self.updateBar("add",progressLocal)
                        elif "error" in desc:
                            self.updateBar("set",86)
                self.signalCursor.emit("down")
        except Exception as ex:
            print("error in addJobDescription: ", ex)
        jobDescription = desc
    
    def md5(self, fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def upload(self):
        global progress, uploadTitle, pagesCount, dirname, OutputDir, collID
        try:
            pageNr = 0
            self.updateBar("set", 1)
            url = ("https://transkribus.eu/TrpServer/rest/uploads?collId=%s" % collID)
            headers = {'Content-Type': 'application/json'}
            uploadTitle = ""
            data = ""
            allFiles = [f for f in listdir(dirname) if isfile(join(dirname, f)) and f.endswith('.tif')]
            pagesCount = len(allFiles)
            for file in allFiles:
                self.addJobDescription("Calculating cheksum...")
                checksum = self.md5(dirname + "/" + file)
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
            
            self.addJobDescription("Uploading " + str(pagesCount) + " pages...")
            url = ("https://transkribus.eu/TrpServer/rest/uploads/%s" % uploadID)
            for indx, file in enumerate(allFiles):
                with open(dirname + "/" + file, "rb") as f:
                    response = requests.put(url, cookies=SessionIdCookie, files={"img": f})
                    if response.status_code == 200:
                        self.addJobDescription(("Image uploaded! (%s of %s)"%(indx + 1, str(len(allFiles)))))
                        print("1 image uploaded!")
                    else:
                        print("Upload of 1 image failed!")
                        self.addJobDescription(("Image upload failed (%s of %s)"%(indx + 1, str(len(allFiles)))))
                        self.addJobDescription(("Trying to upload again (%s of %s)"%(indx + 1, str(len(allFiles)))))
                        response = requests.put(url, cookies=SessionIdCookie, files={"img": f})
                        if response.status_code == 200:
                            self.addJobDescription(("Image uploaded! (%s of %s)"%(indx + 1, str(len(allFiles)))))
                            print("1 image uploaded!")
                        else:
                            print("Upload of 1 image failed AGAIN!")
                            self.addJobDescription(("Image upload failed AGAIN (%s of %s)"%(indx + 1, str(len(allFiles)))))
                    progress_files = (23/len(allFiles))
                    self.updateBar("add", progress_files)  #24% van de bar hierna
                    
                if indx + 1 == len(allFiles):
                    try:
                        self.addJobDescription("Performing image processing...")
                        jobId = str(response.content).split("jobId")[1][1:-2]
                        self.job_status(jobId, task="upload")
                        try:
                            urlPageId = ("https://transkribus.eu/TrpServer/rest/collections/%s/%s/pageIds" % (collID, docID))
                            response_page_id = requests.get(urlPageId, cookies=SessionIdCookie )
                            pageids = json.loads(response_page_id.content)
                            self.handwritten_text_recognition(docID)
                        except:
                            print("error getting pageIds")                    
                    except Exception as ex:
                        print("Error ", ex)      
                    
        except Exception as ex:
            self.addJobDescription(("Error uploading: " + str(ex)))
            print("Error uploading", ex)

    def job_status(self, jobId, link=None, task=None):
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
                counter = 0
                while success == False:
                    responseJob = requests.get(urlJob, cookies=SessionIdCookie)
                    result = json.loads(responseJob.content)
                    try:
                        self.addJobDescription(str(result["description"]), task)
                    except:
                        pass
                    #time.sleep(0.2)
                    success = result["success"]
                    counter += 1
                    if counter == 10:
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

    def handwritten_text_recognition(self, docID):
        try:
            # nodige parameters aanmaken
            self.get_pageids(docID)
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
                modelID = 24692
            elif year == "1866":
                print("HTR model for year 1866")
                modelID = 24471
            elif year == "1880": 
                print("HTR model for year 1880")
                modelID = 24107
            else:
                print("HTR model for all years")
                modelID = 24691
            url = ("https://transkribus.eu/TrpServer/rest/recognition/%s/%s/htrCITlab" % (collID, modelID))
            headers = {'Content-Type': 'application/json'}
            self.updateBar("set",38)
            try:
                self.addJobDescription("Performing HTR...")
                response = requests.post(url, headers=headers, cookies=SessionIdCookie, json=data)
                print("HTR response : ---- ", response.content)
                if response.status_code == 200:
                    print("htr started")
                    filtered_jobID = str(response.content)
                    filtered_jobID2 = filtered_jobID.replace("b","").replace("'","")
                    type(filtered_jobID2)
                    print("filtered job : ---- ",filtered_jobID2)
                    self.job_status(filtered_jobID2, task="htr")
                    print("going to export function now")
                    self.export_to_xml(docID, pageidslen)
                else:
                    print("htr failed")
                    self.addJobDescription("HTR failed!")
                #pass
            except:
                print("HTR failed")
        except Exception as ex:
            print("Error in HTR: ", ex)

    def get_pageids(self, docID):
        try:
            global pageids
            urlPageId = ("https://transkribus.eu/TrpServer/rest/collections/%s/%s/pageIds" % (collID, docID))
            response_page_id = requests.get(urlPageId, cookies=SessionIdCookie )
            pageids = json.loads(response_page_id.content)
            print(pageids)
            return True
        except Exception as ex:
            print("Error in getting page ids: ", ex)
    
    def export_to_xml(self, docID, aantal_bestanden):
        try:
            global exportFinished
            while exportFinished != True:
                self.addJobDescription("Performing server export...")
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
                self.updateBar("set", 86)
                try:
                    response_exports = requests.post(url_exports, headers=header, cookies=SessionIdCookie, json=data ,params=params)
                    print("Export response : ---- ", response_exports.content)
                    if response_exports.status_code == 200:
                        filtered_jobID = str(response_exports.content)
                        filtered_jobID2 = filtered_jobID.replace("b","").replace("'","")
                        print(filtered_jobID2)
                        # print(jobId)
                        if self.job_status(filtered_jobID2, True, task="export") == False:
                            self.exportFailed()
                        else:
                            print("Export worked without failes!")
                            print("klaar voor download")
                            exportFinished = True
                            self.get_downloadurl(filtered_jobID2)
                            #pass
                    else:
                        print("export gefaald")
                        self.addJobDescription("Server export failed!")
                        #pass
                except:
                    print("export gefaald")
        except Exception as ex:
            print("Error in export: ", ex)

    def exportFailed(self):
        print("export failed function")
        time.sleep(5)
        #export_to_xml(docID, pageidslen)
    
    def get_downloadurl(self, jobID):
        try:
            download_url = ("https://transkribus.eu/TrpServer/rest/jobs/%s" %(jobID))
            self.updateBar("set", 93)
            try:
                response_download = requests.get(download_url, cookies=SessionIdCookie)
                if response_download.status_code == 200:
                    downloadlink = json.loads(response_download.content)
                    download_link = downloadlink["result"]
                    print("Download link : ---- ",download_link)
                    self.updateBar("set", 94)
                    self.download_exports(download_link)
                    return True
                else:
                    print("ophalen van download had geen connectie met server")
                    return False
                
            except:
                print("get van download link werd niet uitgevoerd, fout in parameters")
                return False
        except Exception as ex:
            print("Error in getting download url: ", ex)

    def download_exports(self, urlFile):
        global running
        try:
            self.addJobDescription("Performing download...")
            global running, altoFolder, docID, uploadTitle, dirname, OutputDir
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
                self.updateBar("set", 95)
                docID = str(docID)
                altoFolder = (dirname + "/" + docID + "/" + uploadTitle + "/alto/")
                print("altofolder : ---- ",altoFolder)
                self.addJobDescription("Performing post-processing...")
                create = CreateCSV(altoFolder,OutputDir)
                self.updateBar("set", 96)
                create.select_file()
                shutil.rmtree(dirname + "/" + docID)
                os.remove(dirname + "/" + uploadTitle + ".zip")
                os.remove(dirname + "/" + "log.txt")
                print("done")
                self.updateBar("set", 100)
                self.addJobDescription("Finished.")
                running = "finished"
                self.signalStartButton.emit("Finished, Reset")

            except Exception as ex:
                self.addJobDescription("Download or Post-processing failed!")
                print("Error downloading ", ex)
        except Exception as ex:
            print("Error in downloadingen en post processing: ", ex)
        
#region Login and logout
    def login(self):
        global SessionIdCookie, loggedIn, user, pw
        try:
            url = "https://transkribus.eu/TrpServer/rest/auth/login"
            response = requests.post(url, data = {'user':user, 'pw':pw})
            if response.status_code == 200:
                SessionIdCookie = response.cookies
                print("Logged in to Transkribus as " + user)
                loggedIn = True
                self.signalLog.emit("login", str(user))
                return True
            else:
                print("Failed to login as " + user)
                loggedIn = False
                return False
        except Exception as ex :
            print("Error logout", ex)

    def logout(self):
        global loggedIn
        try:
            url = "https://transkribus.eu/TrpServer/rest/auth/logout"
            response = requests.post(url, cookies=SessionIdCookie)
            if response.status_code == 200:
                print("Current client logged out")
                loggedIn = False
                self.signalLog.emit("logout", str(user))
            else:
                print("Logout failed")
        except Exception as ex:
            print("Error logout", ex)

#endregion

if __name__ == '__main__':
    a = QtWidgets.QApplication(sys.argv)
    app = MainUIClass()
    app.show()
    a.exec_()
