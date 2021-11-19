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

from PyQt5 import QtCore, QtGui, QtWidgets
from interface_all import Ui_Form_All
from PyQt5.QtCore import QRunnable, Qt, QThreadPool



#vidange des labels de flash
def resetLabelFinish():
    for listLabelFinish in listLabelsFinish:
        listLabelFinish.setText("")

#chargement et verification des caracteres spéciaux
def loadFile():
    nbError=0
    #effacement avant chargement
    ui.listWidget_firmware.clear()
    #chargement des .bin
    fileNames = glob.glob('*.bin')
    for fileName in fileNames:
        #verification de non utilisation de caractères spéciaux pour le bon lancement de la commande
        if set('[~!@#$%^&*()_+{}":;\']+$').intersection(fileName):
            nbError += 1
            if nbError == 1:
                ui.label_error.setText('Il y a ' + str(nbError) + ' fichier avec des caractères spéciaux')
            else:
                ui.label_error.setText('Il y a ' + str(nbError) + ' fichiers avec des caractères spéciaux')
        else:
            ui.listWidget_firmware.addItem(fileName)

#chargement des ports com
def loadPort():

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


#click sur suivant : verification des bases avant de flasher
#(presence de fichier, port com selectionnés et pas en doublon)
def loadViewFlash():
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
    portsComselect = []
    for index,listWidgetCom in enumerate(listWidgetsCom):
        itemSelected = listWidgetCom.currentItem()
        if (itemSelected == None):
            listComSelected.append(False)
        else:
            listComSelected.append(True)
            itemSelected = listWidgetsCom[index].currentItem().text()
            # on enregistre les noms des ports com pour les comparer apres
            portsComselect.append(itemSelected)
            listLabelsFinish[index].setText(itemSelected)
            nbComTrue +=1
            flagComSelected =True

    #si le flag est toujours a false pas de port com selectionné
    if (flagComSelected == False):
        ui.label_error.setText('Veuillez selectionner au moins un port com')
        return

    #verification si 2x le meme port
    #set retire les doublon d'un tableau
    if (len(portsComselect) != len(set(portsComselect))):
        ui.label_error.setText('ATTENTION : Vous utilisez 2x le même port')
        return


    print("verification des ports Com similaire")

    ui.tabWidget.setTabEnabled(1,True)
    ui.tabWidget.setCurrentIndex(1)
    print(listComSelected)
    print(nbComTrue)

    #afficher le terminal qui correspond

    #calcul de la hauteur frame et de terminal
    heightWindows = 340
    heightFrame = heightWindows / nbComTrue

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



#flashage des cartes (flashNumber = numeros du boutons cliqué ou si c = 100 c'est flashAll)
def loadFlash(flashNumber):

    resetLabelFinish()

    flashNumbersDoing=[]
    if(flashNumber== 100):
        for index,listWidgetCom in enumerate(listWidgetsCom):
            itemSelected = listWidgetCom.currentItem();
            if (itemSelected != None):
                flashNumbersDoing.append(index)
    else : # si bouton solo
        flashNumbersDoing.append(flashNumber)


    for flashNumberDoing in flashNumbersDoing:
        itemSelected = listWidgetsCom[flashNumberDoing].currentItem().text();
        listLabelsFinish[flashNumberDoing].setText(itemSelected)
        fileSelected = ui.listWidget_firmware.currentItem().text();

        listWidgetFlashCarte[flashNumberDoing].clear()
        #print('esptool.py --port '+ str(itemSelected) +' erase_flash')
        #commande = 'esptool.py --port '+ str(itemSelected) +' erase_flash && esptool.py --chip esp32 --port '+ str(itemSelected) +' write_flash -z 0x1000 esp32-20210902-v1.17.bin'
        commande = 'esptool.py --port '+ str(itemSelected) +' erase_flash'
        commande2 = 'esptool.py --chip esp32 --port '+ str(itemSelected) + ' write_flash -z 0x1000 ' + str(fileSelected)

        #print(commande +' && ' + commande2)
        commande = commande +' && ' + commande2

        #threadCount = QThreadPool.globalInstance().maxThreadCount()
        pool = QThreadPool.globalInstance()
        # 2. Instantiate the subclass of QRunnable
        runnable = Runnable(flashNumberDoing, "Commande-"+str(flashNumberDoing), commande, flashNumbersDoing)
        # 3. Call start()
        pool.start(runnable)




def flashComponent(threadID, threadName, commande, flashNumbersDoing):

    #true met la carte en process et sera retirer a la fin
    listFlashInProcess[threadID] = True

    ui.pushButton_flashAll.setEnabled(False)
    #onglet configuration e disable
    ui.tabWidget.setTabEnabled(0,False)
    # on retire l'utilisation la liste de port com et le bouton flash
    listWidgetsCom[threadID].setEnabled(False)
    listPushButton_Flash[threadID].setEnabled(False)

    #envoie de la commande dans le terminal
    procExe = subprocess.Popen(commande, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    #recuperation du buffer des reponse du terminal
    while procExe.poll() is None:
        line = procExe.stdout.readline()
        print("Print:" + threadName + ' ' + line)
        listWidgetFlashCarte[threadID].addItem(str(line))
        listWidgetFlashCarte[threadID].scrollToBottom()

    #gestion des affichages après le flashage terminé
    listWidgetFlashCarte[threadID].addItem(commande + ' : effectuée')
    listWidgetFlashCarte[threadID].scrollToBottom()
    listLabelsFinish[threadID].setText("Terminé")

    listPushButton_Flash[threadID].setEnabled(True)
    ui.tabWidget.setTabEnabled(0,True)
    listFlashInProcess[threadID] = False
    listWidgetsCom[threadID].setEnabled(True)

    #on verifie en retirant les doublons si on a que des false soit 1 case
    if (len(set(listFlashInProcess)) == 1):
        ui.pushButton_flashAll.setEnabled(True)



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form_All = QtWidgets.QWidget()
    ui = Ui_Form_All()
    ui.setupUi(Form_All)

    # listing de ensemble a modifier en valeur global
    listingFramesFlash= [ui.frame_1,ui.frame_2,ui.frame_3,ui.frame_4]
    listWidgetFlashCarte = [ui.listWidget_flash_carte_1,ui.listWidget_flash_carte_22,ui.listWidget_flash_carte_33,ui.listWidget_flash_carte_44]
    listWidgetsCom = [ui.listWidget_com_1,ui.listWidget_com_2,ui.listWidget_com_3,ui.listWidget_com_4]
    listPushButton_Flash = [ui.pushButton_Flash_1,ui.pushButton_Flash_22,ui.pushButton_Flash_33,ui.pushButton_Flash_44]
    listLabelsFinish =[ui.label_finish_1, ui.label_finish_22, ui.label_finish_33, ui.label_finish_44]
    listFlashInProcess=[False,False,False,False]

    #initialistion des message erreurs dnas config
    ui.label_error.setText('')
    #reset des affichages
    resetLabelFinish()
    #chargement des fichiers dans la liste
    loadFile()
    #chargement des ports dans les liste
    loadPort()

    Form_All.show()

    ui.pushButton_firmware_refresh.clicked.connect(loadFile)
    ui.pushButton_refreshAll.clicked.connect(lambda : loadPort())
    ui.pushButton_next.clicked.connect(lambda : loadViewFlash())

    ui.pushButton_Flash_1.clicked.connect(lambda :loadFlash(0))
    ui.pushButton_Flash_22.clicked.connect(lambda :loadFlash(1))
    ui.pushButton_Flash_33.clicked.connect(lambda :loadFlash(2))
    ui.pushButton_Flash_44.clicked.connect(lambda :loadFlash(3))

    ui.pushButton_flashAll.clicked.connect(lambda :loadFlash(100))

    sys.exit(app.exec_())


