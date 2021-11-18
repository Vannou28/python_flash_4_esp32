# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interface.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!

import serial.tools.list_ports
import subprocess
import sys
import glob
import threading


from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5 import QtCore, QtGui, QtWidgets
from interface_all import Ui_Form_All
from PyQt5.QtCore import QRunnable, Qt, QThreadPool


finishFlashNumber = 0

def resetLabelFinish():
    for listLabelFinish in listLabelsFinish:
        listLabelFinish.setText("")

def loadFile():
    nbError=0
    ui.listWidget_firmware.clear()
    fileNames = glob.glob('*.bin')
    for fileName in fileNames:
        if set('[~!@#$%^&*()_+{}":;\']+$').intersection(fileName):
            nbError += 1
            if nbError == 1:
                ui.label_error.setText('Il y a ' + str(nbError) + ' fichier avec des caractères spéciaux') 
            else:
                ui.label_error.setText('Il y a ' + str(nbError) + ' fichiers avec des caractères spéciaux') 
        else:
            ui.listWidget_firmware.addItem(fileName)


def loadPort(listWidgetsCom):
    
    ui.tabWidget.setTabEnabled(1,False)

    #recherche des ports com utilisés
    comlist = serial.tools.list_ports.comports()
    connected = []
    for element in comlist:
        connected.append(element.device)
    
    #chargement des ports com dans les listing
    for listWidgetCom in listWidgetsCom:
        listWidgetCom.clear()
        listWidgetCom.addItems(connected)


def loadViewFlash(listWidgetsCom):
    #verif si il y a fichier de selectionné
    fileSelected = ui.listWidget_firmware.currentItem();
    if(fileSelected==None):
        ui.label_error.setText('Veuillez selectionner un fichier')
        return
    ui.label_error.setText('')
    
    #verif si il y a un port com de selectionner
    listComSelected=[]
    flagComSelected = False
    nbComTrue=0
    numberComTrue=[]
    for index,listWidgetCom in enumerate(listWidgetsCom):
        itemSelected = listWidgetCom.currentItem();
        if (itemSelected == None):
            listComSelected.append(False)
        else:
            listComSelected.append(True)
            nbComTrue +=1
            flagComSelected =True
    
    if (flagComSelected == False):
        ui.label_error.setText('Veuillez selectionner au moins un port com')
        return

    
    ui.tabWidget.setTabEnabled(1,True)
    ui.tabWidget.setCurrentIndex(1)
    print(listComSelected)
    print(nbComTrue)

    #afficher le terminal qui correspond 

    #calcul de la hauteur frame et de terminal
    heightWindows = 340
    heightFrame = heightWindows / nbComTrue
    print(str(heightFrame))
    indexTrue = 0
    for index,listingFrameFlash in enumerate(listingFramesFlash):
        listingFrameFlash.setVisible(listComSelected[index])
        if (listComSelected[index]==True):
            listingFrameFlash.setGeometry(QtCore.QRect(20, int(((heightFrame)*indexTrue)+20), 611, int(heightFrame)))
            listWidgetFlashCarte[index].setGeometry(QtCore.QRect(170, 0, 441, int(heightFrame)))
            indexTrue+=1
 

def runTasks(self):
    threadCount = QThreadPool.globalInstance().maxThreadCount()
    self.label.setText(f"Running {threadCount} Threads")
    pool = QThreadPool.globalInstance()
    for i in range(threadCount):
        # 2. Instantiate the subclass of QRunnable
        runnable = Runnable(i)
        # 3. Call start()
        pool.start(runnable)


# 1. Subclass QRunnable
class Runnable(QRunnable):
    def __init__(self, threadID, threadName, commande, flashNumbersDoing):
        super().__init__()
        self.threadID = threadID
        self.threadName = threadName
        self.commande = commande
        self.flashNumbersDoing = flashNumbersDoing

    def run(self):
        """Long-running task."""
        flashComponent(self.threadID, self.threadName, self.commande, self.flashNumbersDoing)        

    


def loadFlash(flashNumber):
    listPushButton_Flash = [ui.pushButton_Flash_1,ui.pushButton_Flash_22,ui.pushButton_Flash_33,ui.pushButton_Flash_44]
    resetLabelFinish()

    
    flashNumbersDoing=[]
    if(flashNumber== 100):
        for index,listWidgetCom in enumerate(listWidgetsCom):
            itemSelected = listWidgetCom.currentItem();
            if (itemSelected != None):
                flashNumbersDoing.append(index)
    else :
        flashNumbersDoing.append(flashNumber)

    threads = []

    for flashNumberDoing in flashNumbersDoing:
        ui.pushButton_flashAll.setEnabled(False)
        itemSelected = listWidgetsCom[flashNumberDoing].currentItem().text();
        fileSelected = ui.listWidget_firmware.currentItem().text();
        listPushButton_Flash[flashNumberDoing].setEnabled(False)
        listWidgetFlashCarte[flashNumberDoing].clear()
        #print('esptool.py --port '+ str(itemSelected) +' erase_flash')
        #commande = 'esptool.py --port '+ str(itemSelected) +' erase_flash && esptool.py --chip esp32 --port '+ str(itemSelected) +' write_flash -z 0x1000 esp32-20210902-v1.17.bin'
        commande = 'esptool.py --port '+ str(itemSelected) +' erase_flash'
        commande2 = 'esptool.py --chip esp32 --port '+ str(itemSelected) + ' write_flash -z 0x1000 ' + str(fileSelected) 

        print(commande +' && ' + commande2)
        commande = commande +' && ' + commande2
       
        #threadCount = QThreadPool.globalInstance().maxThreadCount()
        pool = QThreadPool.globalInstance()
        # 2. Instantiate the subclass of QRunnable
        runnable = Runnable(flashNumberDoing, "Commande-"+str(flashNumberDoing), commande, flashNumbersDoing)
        # 3. Call start()
        pool.start(runnable)
 



def flashComponent(threadID, threadName, commande, flashNumbersDoing):
    global finishFlashNumber
    #onglet cofiguration e disable
    ui.tabWidget.setTabEnabled(0,False)

    procExe = subprocess.Popen(commande, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    while procExe.poll() is None:
        line = procExe.stdout.readline()
        print("Print:" + threadName + ' ' + line)
        listWidgetFlashCarte[threadID].addItem(str(line))
        listWidgetFlashCarte[threadID].scrollToBottom()

    listWidgetFlashCarte[threadID].addItem(commande + ' : effectuée')
    listWidgetFlashCarte[threadID].scrollToBottom()
    
    ui.label_error.setText('Flash terminé') 
    ui.tabWidget.widget(0)

    finishFlashNumber += 1
    listLabelsFinish[threadID].setText("Terminé")
    listPushButton_Flash[threadID].setEnabled(True)

    if(len(flashNumbersDoing)== finishFlashNumber):
        ui.tabWidget.setTabEnabled(0,True)
        for flashNumberDoing in flashNumbersDoing:
            ui.pushButton_flashAll.setEnabled(True)
            #listPushButton_Flash[flashNumberDoing].setEnabled(True)


        

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form_All = QtWidgets.QWidget()
    ui = Ui_Form_All()
    ui.setupUi(Form_All)
    # variable global pour le thread
    listingFramesFlash= [ui.frame_1,ui.frame_2,ui.frame_3,ui.frame_4]
    listWidgetFlashCarte = [ui.listWidget_flash_carte_1,ui.listWidget_flash_carte_22,ui.listWidget_flash_carte_33,ui.listWidget_flash_carte_44]
    listWidgetsCom = [ui.listWidget_com_1,ui.listWidget_com_2,ui.listWidget_com_3,ui.listWidget_com_4]
    listPushButton_Flash = [ui.pushButton_Flash_1,ui.pushButton_Flash_22,ui.pushButton_Flash_33,ui.pushButton_Flash_44]
    listLabelsFinish =[ui.label_finish_1, ui.label_finish_22, ui.label_finish_33, ui.label_finish_44] 
    # queue where results are placed



    Form_All.show()

    resetLabelFinish()
    loadFile()
    loadPort(listWidgetsCom)
    ui.pushButton_firmware_refresh.clicked.connect(loadFile)
    ui.pushButton_refreshAll.clicked.connect(lambda : loadPort(listWidgetsCom))
    ui.pushButton_next.clicked.connect(lambda : loadViewFlash(listWidgetsCom))

    ui.pushButton_Flash_1.clicked.connect(lambda :loadFlash(0))
    ui.pushButton_Flash_22.clicked.connect(lambda :loadFlash(1))
    ui.pushButton_Flash_33.clicked.connect(lambda :loadFlash(2))
    ui.pushButton_Flash_44.clicked.connect(lambda :loadFlash(3))

    ui.pushButton_flashAll.clicked.connect(lambda :loadFlash(100))
    


    sys.exit(app.exec_())


