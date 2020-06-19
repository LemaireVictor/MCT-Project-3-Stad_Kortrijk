# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'first.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
import sys


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(963, 372)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.btnDirectory = QtWidgets.QPushButton(self.centralwidget)
        self.btnDirectory.setObjectName("btnDirectory")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.btnDirectory)
        self.txtDirectory = QtWidgets.QLineEdit(self.centralwidget)
        self.txtDirectory.setInputMask("")
        self.txtDirectory.setText("")
        self.txtDirectory.setMaxLength(32767)
        self.txtDirectory.setObjectName("txtDirectory")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.txtDirectory)
        self.btnOutput = QtWidgets.QPushButton(self.centralwidget)
        self.btnOutput.setObjectName("btnOutput")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.btnOutput)
        self.txtOutput = QtWidgets.QLineEdit(self.centralwidget)
        self.txtOutput.setObjectName("txtOutput")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.txtOutput)
        self.btnStartProcess = QtWidgets.QPushButton(self.centralwidget)
        self.btnStartProcess.setObjectName("btnStartProcess")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.SpanningRole, self.btnStartProcess)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.SpanningRole, self.progressBar)
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.SpanningRole, self.textEdit)
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)
        self.lblLoggedInAs = QtWidgets.QLabel(self.centralwidget)
        self.lblLoggedInAs.setObjectName("lblLoggedInAs")
        self.gridLayout.addWidget(self.lblLoggedInAs, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 963, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Kortrijk archives HTR app"))
        self.btnDirectory.setText(_translate("MainWindow", "Directory"))
        self.btnOutput.setText(_translate("MainWindow", "Output folder"))
        self.btnStartProcess.setText(_translate("MainWindow", "Start process"))
        self.lblLoggedInAs.setText(_translate("MainWindow", "Currently logged in as: "))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
