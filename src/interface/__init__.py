from pathlib import PurePath
from PySide2 import QtGui
from PySide2.QtCore import QDir, QFile, QIODevice, Qt, QTextStream,\
    QStringListModel
from PySide2.QtWidgets import (
    QAction,
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QPlainTextEdit,
    QInputDialog,
    QStatusBar,
    QFormLayout,
    QLineEdit,
    QDialog,
    QTextEdit,
    QMessageBox
    
)

from PySide2.QtGui import QTextCharFormat, QIcon, QColor

from PySide2.QtCore import Slot, Qt
import verovio
import random
import re
import signal
import string
import sys
import os  
from PySide2.QtGui import QTextCursor, QFont
from _operator import index 
from lxml import etree 

signal.signal(signal.SIGINT, signal.SIG_DFL)

FONT_FAMILY = "Times New Roman"
FONT_SIZE = 14
MENLO_14_CHARACTER_WIDTH = 8
WIDEST_CHARACTER = "W"


 

class App(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        
         
        
         
        
        
        
        ''' streams '''
        self.initial_FileStream = None # initial stream: this will never bee changed
        self.temporaryWithTags = None # 
        self.temporaryWithoutTags = None
       
       
        ''' load styles '''
        
        
        
        ''' load dictionaries '''
         
         
        
        
        #
        # Stylesheet
        #

        self.setStyleSheet(
            """
        QPlainTextEdit, QLabel {
            font-family: Menlo;
            font-size: {FONT_SIZE}px;
        }
        QFrame {
            border: 0px solid rgba(0, 0, 0, 0.1);
        }
        """
        )

        #
        # Widgets
        #

        # The editor
        self.plaintexteditor = QPlainTextEdit() 
    
        
        # Status bar
        
        self.statusBar = QStatusBar()
        self.xmlTeiValidation = QWidget() 
        self.xmlStatusLabel = QLabel("XML status: ")
        self.teiStatusLabel = QLabel("TEI Compliance: ")
        self.xmlStatus = QLabel("")
        self.teiStatus = QLabel("")  
        self.statusBar.addPermanentWidget(self.xmlStatusLabel, 0)
        self.statusBar.addPermanentWidget(self.xmlStatus, 0)
        self.statusBar.addPermanentWidget(self.teiStatusLabel, 0)
        self.statusBar.addPermanentWidget(self.teiStatus, 0)
        self.setStatusBar(self.statusBar)
        
    
        #
        # Actions
        #
        
        #File
        self.import_action = QAction("&Import score", self, shortcut="Ctrl+I", statusTip="Import", triggered=self.import_file) # 
        self.open_action = QAction("&Open project", self, shortcut="Ctrl+O", statusTip="Open", triggered=self.open_file) # 
        self.save_action = QAction("&Save project", self, shortcut="Ctrl+S", statusTip="Save", triggered=self.save_file)
        self.saveAs_action = QAction("&Save project as", self, shortcut="", statusTip="Save as", triggered=self.saveAs_file)
        self.exit_action = QAction("&Quit", self, shortcut="Ctrl+Q", statusTip="Exit the application", triggered=self.close)
        
         
        
        
        #
        # Menus
        #

        
        # Menu bar
        self.menu_bar = self.menuBar()
        
        # File menu
        self.file_menu = self.menu_bar.addMenu("&File")
        self.file_menu.addAction(self.import_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.saveAs_action)
        self.file_menu.addAction(self.exit_action)
        
        

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_widget.layout)
        self.central_widget.layout.addWidget(self.menu_bar) 
         
         
        self.central_widget.layout.addWidget(self.plaintexteditor)
        
      
        
        
    def import_file (self):
        
        tk = verovio.toolkit()
        tk.loadFile("/Users/christophe/Downloads/mei.mei")
        print (tk.renderToSVG(1))
        
        
    
    
    
    def open_file(self):
            filename, filtr = QFileDialog.getOpenFileName(self, dir=self.last_opened_directory)
            selected_file = QFile(filename)
            if selected_file.open(QFile.ReadOnly):
                self.current_file = filename 
                self.last_opened_directory = str(PurePath(self.current_file).parent)
                 
                self.initial_FileStream = QTextStream(selected_file).readAll()
                print (len( self.initial_FileStream))
                
                 
                #===================================================================
                # if xmlString.isWellFormed():
                #     
                #     ''' remove white spaces between tags '''
                #     normalizedString = xmlString.getXMLString(mode="remove_blank_text")
                #     print (len(normalizedString))
                #     
                #     prettyXML = xmlString.getXMLString(mode="pretty_print")
                #     print (len(prettyXML))
                #     print (prettyXML)
                #     
                #     xmlString = parseXMLString(prettyXML)
                #     normalizedString = xmlString.getXMLString(mode="remove_blank_text")
                #     print (len(normalizedString))
                #     print (normalizedString)
                #===================================================================
                    
                
                
     
    def save_file(self):
        ''' update temporary with tags '''
        self.updateTemporaryWithTags()
        
        if self.current_file is not None:
            file = QFile(self.current_file)
            if not file.open(QIODevice.WriteOnly | QIODevice.Text):
                return
               
    def saveAs_file(self):
        
        ''' update temporary with tags'''
        self.updateTemporaryWithTags()
        
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        
        filename, filtr = dialog.getSaveFileName(self, "Save as", dir=self.last_opened_directory)
        selected_file = QFile(filename)
        self.current_file = filename
        self.last_opened_directory = str(PurePath(self.current_file).parent)
        
        if not selected_file.open(QIODevice.WriteOnly | QIODevice.Text):
            return
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    

    widget = App()
    widget.setWindowTitle("IReMus TEI Tagger")
    widget.resize(1111, 888)
    widget.show()
    sys.exit(app.exec_())