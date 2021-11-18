## Interface de flashage ESP32
	
## Index
1. [Description](#Description)
2. [Prerequisites](#Prerequisites)
3. [Installation](#Installation)
4. [Built-With](#Built-With)
5. [Authors](#Authors)

## Description

Interface for flashing several electronic boards at the same time

## Prerequisites
* [PYTHON3.8.*](https://www.python.org/downloads/)
* [ESPTOOL.*](https://github.com/espressif/esptool) (pip install esptool)
* [PYSERIAL.*](https://pypi.org/project/pyserial/) (pip install pyserial)
* [PYTHON QT Designer.*](https://pypi.org/project/PyQt5Designer/) (pip install PyQt5Designer)
* [PYTHON QT Library.*](https://pythonbasics.org/install-pyqt/) (sudo apt-get install python3-pyqt5)

## Installation
If you meet the prerequisites, you can proceed to the installation of the project 

1. Clone the project from [Github](https://github.com/Vannou28/python_flash_4_esp32.git)
2. Open the project folder with your code editor
3. Open the terminal and run the following commands:
4. Run `pip install esptool` to install ESP TOOLS
5. Run `pip install pyserial` to install PYSERIAL to search for used ports
6. Run `python3 interface_4_V1.2.py` to launch interface


if you want to modify the interface :
1. Open the terminal and run the following commands:
2. Run `pip install PyQt5Designer` to install PYTHON QT Designer.
3. Open `interface_flash_all.ui`
4. Modify your interface
5. transform a .ui into .py :
`python3 -m PyQt5.uic.pyuic -x interface_flash_all.ui -o interface_all.py`
6. Modify your code

## Built-With

* [PYTHON QT Designer.*](https://pypi.org/project/PyQt5Designer/) (pip install PyQt5Designer)
* [PYTHON3.8.*](https://www.python.org/downloads/)

## Authors

* [Aurélien Vannier](https://github.com/Vannou28)
