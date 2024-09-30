import serial, time, glob, sys, os
from multiprocessing import Process
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
import json
import requests
from requests.auth import HTTPBasicAuth
import base64
import pyperclip
from PyQt5.QtWidgets import QMessageBox
from datetime import datetime
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QStringListModel
import pygame


class usp_service(object):

    def __init__(self, url):
        self.url = url
        self.headers = { "Content-Type": "application/json" }
        
    def login(self, email, password):
        url = self.url + '/Users'
        payload = json.dumps({
            "email": email,
            "password": password,
            "ttl": "4838400"
        })
        response = requests.request("POST", url + "/login", headers=self.headers, data=payload)
        # print(response.text)
        if(response.status_code == 200):
            myResponse = json.loads(response.text)["id"]
        else:
            myResponse = ""
        return(myResponse)
    
    def poll(self, client, mac):
        return {'ClientId':client, "MAC":mac}
    
    def query(self, client, mac, cmd):
        return {'ClientId':client, "MAC":mac, "CMD":cmd, "Type":1}
    
    def response(self, client, mac, cmd, ref):
        return {'ClientId':client, "MAC":mac, "CMD":cmd, "Type":1, "RefId":ref}


class piPumps(object):

    def __init__(self):
        self.id = 0 
        self.HardwareId = 0 
        self.SoftwareId = 0 
        self.Status = 0 
        self.Enabled = False 
        self.PulsRate = 0 
        self.tank_id = 0 
        self.pumptype_id = 0 
        self.ComPort = 0 
        self.PumpTotal = 0 
        self.SiteId = 0 
        self.OldPulse = 0 
        self.Pulse = 0 
        self.OldStatus = 0 
        self.TagString = "" 
        self.FinCount = 0 
        self.Nozzle = 0 
        self.NozPrice = 0 
        self.Money = 0 
        self.Volume = 0 
        self.PresetPulse = 0 
        self.PresetVolume = 0 
        self.PulseTimeout = 0 
        self.Attendant = "" 
        self.Driver = "" 
        self.client_id = "" 
        self.ElectronicTotal = 0 
        self.TransactionId = 0 
        self.ProtocolTimer = 0 
        self.ProtocolTimeout = 0 
        self.ProtocolBaud = 0 
        self.StatusMessageId = 0 
        self.StatusMessage = "" 
        self.IsPrepay = False 
        self.SlowDownVal = 0 
        self.PinNo = "" 
        self.FleetNo = "" 
        self.Authorized = False 
        self.WebId = 0 
        self.Downloaded = True 
        self.DecimalPlaces = 0 
        self.PumpModel = 0 
        self.kbStatus = 0 
        self.kbData = ""
        self.GroupId = 0
        self.NoOfNoz = 0
        self.TankId2 = 0
        self.TankId3 = 0
        self.TankId4 = 0
        self.VitIP = ""
        self.VitHexId = 0
        self.VitEnabled = False
        self.VitPort = 0
        self.VitChannel = 0
        self.VitOdometer = 0.0
        self.VitPlate = ""
        self.VitEnginehours = 0.0
        self.VitBlocked = False
        self.VitBlockReason = ""
        self.TagEnabled = True
        self.TagPort = 0
        self.TagType = -1
        self.TagRemote = 0
        self.ClientCommand = 0
        self.ServerCommand = 0
        self.Description = ""
        self.InuseAsBypass = False
        self.DummyNoz = False
        self.AutoAuth = False
        self.VIUStatus = 0
        self.OverideType = 0
        self.OverideTag = ""
        self.DeviceId = 0
        self.TagReader = 0
        self.volume1 = 0
        self.volume2 = 0
        self.volume3 = 0
        self.tagstring1 = ""
        self.tagstring2 = ""
        self.tagstring3 = ""
        self.otp = ""
        self.priceDecimal = 1.0
        self.volumeDecimal = 100.0
        self.moneyDecimal = 100.0
        self.pplDecimal = 100.0
        self.totalsDecimal = 100.0


class MAX9097:
    """ Minimal DS2480B control and 1-wire data transfer.
    
    DS2480B control
        0xE3 : command-mode
        0xE1 : data-mode
        0xC1 : reset
        0x81/0x91 : sigle-bit-write-0/1
    """
    _MODE_CMD = 0xE3
    _MODE_DAT = 0xE1
    
    def __init__(self, port, timeout=3):
        """
        port : string, name of serial port (ex. 'COM3').
        timeout : float, [sec] timeout.
        """
        self.uart = serial.Serial(port=port, timeout=timeout)
        self.clear()
        self.mode = MAX9097._MODE_CMD
        self.cmd_reset()
        
    def clear(self):
        self.uart.send_break()
        self.uart.reset_input_buffer()
        self.uart.reset_output_buffer()
        
    def set_mode(self, mode):
        if mode != self.mode:
            self.uart.write([mode])
            self.mode = mode
            # r = self.uart.read(1)
        
    def close(self):
        self.uart.close()
        
    def cmd_reset(self):
        self.set_mode(MAX9097._MODE_CMD)
        self.uart.write([0xC1])  # reset-pulse
        r = self.uart.read()
        if r != b'\xCD':
            "ERROR"
        
    def cmd_write_bit(self, v):
        self.set_mode(MAX9097._MODE_CMD)
        if v != 0:
            self.uart.write([0x91])  # "on" bit
        else:
            self.uart.write([0x81])  # "off" bit
        val = self.uart.read(1)
        return int(val[0]) & 1
        
    def cmd_read_bit(self):
        return self.cmd_write_bit(1)
        
    def dat_write(self, buf):

        def _w(v):
            self.uart.write([v])
            return self.uart.read(1)

        self.set_mode(MAX9097._MODE_DAT)
        return [_w(a) for a in buf]
        
    def dat_read(self, n):
        return self.dat_write([0xFF] * n)

    def crc_check(self, rBytes):
        crc = 0
        for b in rBytes:
            if(b < 0):
                b += 256    
            for i in range(8):
                odd = ((b ^ crc) & 1) == 1
                crc >>= 1
                b >>= 1
                if(odd):
                    crc ^= 0x8C
        return crc


class max9097TagReader(object):

    def __init__(self):
        print("INFO - max9097TagReader started")
        self.tagString = "0000000000000000"

    # Define MAX9097 BUS
    def connect(self, COMport='/dev/ttyUSB0', timeout=0.03):
        self.bus = MAX9097(COMport, timeout)
        print("INFO - OneWire connected on port : %s" % COMport)

    def readTagReader(self):
        try:
            self.bus.mode = self.bus._MODE_CMD
            self.bus.dat_write([0x33])  # read-rom
            ans = self.bus.dat_read(8)  # little-endian (family + SN[6] + CRC)
            if(any(x == '' for x in ans)):
                print("WARNING - Invalid Rx : %s" % ans)
                time.sleep(1.0)
            else:
                barray = [int.from_bytes(x, byteorder='little') for x in ans]
                crc = self.bus.crc_check(barray)
                if((ans[0] == b'\x01' or ans[0] == b'\x08') and crc == 0):
                    rcv = ['%02X' % a for a in reversed(barray)]
                    self.tagString = rcv[7] + rcv[6] + rcv[5] + rcv[4] + rcv[3] + rcv[2] + rcv[1] + rcv[0]
                    print("TAG - %s" % self.tagString)
            self.bus.clear()
        except:
            print("ERROR- readTagReader : %s" % sys.exc_info()[1])

    def clearTagBuffer(self):
        self.tagString = "0000000000000000"

    def isTagData(self):
        isTag = False
        if(self.tagString != "0000000000000000"):
            isTag = True
        return isTag

    def getTagData(self, pData):
        sTag = self.tagString
        pData.TagString = sTag
        # print("INFO - Tag No - %s" % sTag)
        self.clearTagBuffer()
        return True


class Ui_MainWindow(object):
    open = 0
    
    def __init__(self):
        self.oPumps = piPumps() 
        self.oTagReader = max9097TagReader()
        self.timer = QtCore.QTimer(interval=30, timeout=self.tControl)
        self.t = time.time()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(488, 386)
        MainWindow.setMinimumSize(QtCore.QSize(600, 500))
        MainWindow.setMaximumSize(QtCore.QSize(600, 500))

        # Apply custom styles
        self.apply_styles(MainWindow)

        # Remove window frame and set rounded corners
        MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        MainWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        # Create the main layout
        mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        mainLayout.setContentsMargins(10, 10, 10, 10)
        mainLayout.setSpacing(10)

        # Logo label at the top center
        self.logoLbl = QtWidgets.QLabel(self.centralwidget)
        self.logoLbl.setFont(QtGui.QFont('Segoe UI', 28))
        self.logoLbl.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.logoLbl.setText("")
        self.logoLbl.setObjectName("logoLbl")
        self.logoLbl.setAlignment(QtCore.Qt.AlignCenter)
        mainLayout.addWidget(self.logoLbl)

        # Layout for the close button and empty space
        closeLayout = QtWidgets.QHBoxLayout()
        closeLayout.addStretch(1)
        self.closeButton = QtWidgets.QPushButton("X", self.centralwidget)
        self.closeButton.setObjectName("closeButton")
        self.closeButton.clicked.connect(MainWindow.close)
        closeLayout.addWidget(self.closeButton)
        mainLayout.addLayout(closeLayout)

        # Stacked widget container
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName("stackedWidget")

        # Page layout for the Tag Reader page
        self.page3 = QtWidgets.QWidget()
        self.page3.setObjectName("page3")
        pageLayout = QtWidgets.QVBoxLayout(self.page3)

        self.serialLbl = QtWidgets.QLabel(self.page3)
        self.serialLbl.setFont(QtGui.QFont('Segoe UI', 10))
        self.serialLbl.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.serialLbl.setObjectName("serialLbl")
        pageLayout.addWidget(self.serialLbl, alignment=QtCore.Qt.AlignLeft)

        comboLayout = QtWidgets.QHBoxLayout()
        comboLayout.addWidget(QtWidgets.QLabel("COM:", self.page3), alignment=QtCore.Qt.AlignLeft)
        self.comboBoxComs = QtWidgets.QComboBox(self.page3)
        self.comboBoxComs.setMinimumWidth(200)
        self.comboBoxComs.setObjectName("comboBoxComs")
        comboLayout.addWidget(self.comboBoxComs, alignment=QtCore.Qt.AlignLeft)
        self.connectButton = QtWidgets.QPushButton(self.page3)
        self.connectButton.setMinimumWidth(200)
        self.connectButton.setObjectName("connectButton")
        comboLayout.addWidget(self.connectButton, alignment=QtCore.Qt.AlignLeft)
        
        pageLayout.addLayout(comboLayout)

        self.tagLbl_2 = QtWidgets.QLabel(self.page3)
        self.tagLbl_2.setFont(QtGui.QFont('Segoe UI', 16, QtGui.QFont.Bold))
        self.tagLbl_2.setObjectName("tagLbl_2")
        pageLayout.addWidget(self.tagLbl_2, alignment=QtCore.Qt.AlignLeft)

        self.tagEdit_2 = QtWidgets.QLineEdit(self.page3)
        self.tagEdit_2.setFont(QtGui.QFont('Segoe UI', 12))
        self.tagEdit_2.setMinimumWidth(450)
        self.tagEdit_2.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        self.tagEdit_2.setReadOnly(True)
        self.tagEdit_2.setObjectName("tagEdit_2")
        pageLayout.addWidget(self.tagEdit_2, alignment=QtCore.Qt.AlignLeft)

        self.infoLbl_3 = QtWidgets.QLabel(self.page3)
        self.infoLbl_3.setFont(QtGui.QFont('Segoe UI', 10))
        self.infoLbl_3.setStyleSheet("color: red;")
        self.infoLbl_3.setObjectName("infoLbl_3")
        pageLayout.addWidget(self.infoLbl_3, alignment=QtCore.Qt.AlignLeft)

        # Horizontal layout for additional QLineEdit and QComboBox
        rangeLayout = QtWidgets.QHBoxLayout()
        
        self.rangeLbl = QtWidgets.QLabel("Tag Type:", self.page3)
        self.rangeLbl.setFont(QtGui.QFont('Segoe UI', 12))
        rangeLayout.addWidget(self.rangeLbl, alignment=QtCore.Qt.AlignLeft)
        
        self.newLineEdit = QtWidgets.QLineEdit(self.page3)
        self.newLineEdit.setFont(QtGui.QFont('Segoe UI', 12))
        self.newLineEdit.setObjectName("newLineEdit")
        self.newLineEdit.setMinimumWidth(200)  # Set minimum width for wider appearance
        rangeLayout.addWidget(self.newLineEdit, alignment=QtCore.Qt.AlignLeft)
        
        self.newLineEdit.hide()

        self.newComboBox = QtWidgets.QComboBox(self.page3)
        self.newComboBox.setFont(QtGui.QFont('Segoe UI', 12))
        self.newComboBox.setObjectName("newComboBox")
        self.newComboBox.addItems(["Dallas Tag", "RFID Tag", "Mix Tag"])  # Customize options as needed
        self.newComboBox.setMinimumWidth(500)  # Increased width
        
        rangeLayout.addWidget(self.newComboBox, alignment=QtCore.Qt.AlignLeft)

        pageLayout.addLayout(rangeLayout)

        self.stackedWidget.addWidget(self.page3)
        mainLayout.addWidget(self.stackedWidget)
        '''
        # Set the initial layout for the status bar
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        '''
        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentWidget(self.page3)  # Directly show the tag reader page
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.startButton = QtWidgets.QPushButton(self.page3)

        self.startButton.setMinimumWidth(200)
        self.startButton.setObjectName("startButton")
        self.startButton.setText("BULK SETUP")
        pageLayout.addWidget(self.startButton, alignment=QtCore.Qt.AlignCenter)
        self.startButton.clicked.connect(self.show_start_popup)

    def show_start_popup(self):

        '''range_value = self.newLineEdit.text()
        selected_tag = self.newComboBox.currentText()
    
        # Create and display the message box
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle("Start Button Clicked")
        msg_box.setText(f"Range: {range_value}\nSelected Tag: {selected_tag}")
        msg_box.setIcon(QtWidgets.QMessageBox.Information)
        msg_box.exec_() '''
        self.RangeLoopWindow = RangeLoopWindow()
        # self.RangeTagWindow.romCodeEdit.setText(self.oPumps.TagString)
        self.RangeLoopWindow.show()
        
    def apply_styles(self, MainWindow):
        style = """
            QWidget {
                background-color: #f0f0f0;
                border-radius: 15px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 14px;
            }
            QLabel {
                color: #333;
                font-weight: bold;
            }
            QLineEdit {
                font-size: 14px;
                border: 3px solid #cc5500;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
                color: #333;
            }
            QComboBox {
                font-size: 14px;
                border: 1px solid #cc5500;
                border: 3px solid #cc5500;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #cc5500;
                color: white;
                font-size: 14px;
                border-radius: 10px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff6600;
            }
            QStatusBar {
                background-color: #f0f0f0;
                border-radius: 10px;
                border-top: 1px solid #cc5500;
                border: 3px solid #cc5500;
            }
            QMenuBar {
                background-color: #f0f0f0;
            }
            QMainWindow {
                border: 3px solid #cc5500;
            }  
        """
        MainWindow.setStyleSheet(style)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "FMA Tag Reader"))
        self.serialLbl.setText(_translate("MainWindow", "Serial Settings"))
        self.tagLbl_2.setText(_translate("MainWindow", "Tag"))
        self.infoLbl_3.setText(_translate("MainWindow", ""))
        self.connectButton.setText(_translate("MainWindow", "Connect"))

        pixmap = QtGui.QPixmap(self.resource_path("logo.png"))
        pixmap = pixmap.scaled(self.logoLbl.width(), self.logoLbl.height(), QtCore.Qt.KeepAspectRatio)
        self.logoLbl.setPixmap(pixmap)
        self.logoLbl.setAlignment(QtCore.Qt.AlignCenter)

        self.attachUIcontrol()

    def attachUIcontrol(self):
        self.connectButton.clicked.connect(self.connect)
        self.closeButton.clicked.connect(QtWidgets.qApp.quit)
        self.comboBoxComs.addItems(self.getPortNames())

    def resource_path(self, relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def connect(self):
        self.connectButton.setEnabled(False)
        self.oTagReader.connect(self.getPortSelected())  
        self.timer.start()

        '''     def tControl(self):
    
        self.oTagReader.readTagReader()
        if self.oTagReader.isTagData():
            self.oTagReader.getTagData(self.oPumps)
            self.infoLbl_3.setText("New Tag Detected!!!")
            self.tagEdit_2.setText(self.oPumps.TagString)
            self.t = time.time() + 2
            # Clear the clipboard first
            pyperclip.copy('')
            
            # Copy the tag data to the clipboard
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(self.oPumps.TagString)

            # Show the Tag Action Window
            self.tagActionWindow = TagActionWindow()
            self.tagActionWindow.show()
        elif time.time() > self.t:
            self.infoLbl_3.setText("Present Next Tag")
            self.t = time.time() '''

    def tControl(self):
    
        # Get the value from the range field
        range_value = self.newLineEdit.text().strip()
        print("Range field value:", range_value)
    
        # Function to handle tag reader and populate/update the window
        def handle_tag_action():
            
            self.oTagReader.readTagReader()
            if self.oTagReader.isTagData():
                self.oTagReader.getTagData(self.oPumps)
                self.infoLbl_3.setText("New Tag Detected!!!")

                # Initialize pygame
                pygame.mixer.init()
                
                # Load the sound file
                pygame.mixer.music.load(r'beep.mp3')
                
                # Play the sound
                pygame.mixer.music.play()
                
                # Wait for 1 second (1000 milliseconds)
                pygame.time.wait(1000)
                
                # Stop the sound
                pygame.mixer.music.stop()
                tag_data = self.oPumps.TagString
                self.t = time.time() + 2
    
                # Clear the clipboard first
                pyperclip.copy('')
    
                # Copy the tag data to the clipboard
                clipboard = QtWidgets.QApplication.clipboard()
                clipboard.setText(tag_data)
    
                # Check if RangeLoopWindow is already open
                if hasattr(self, 'RangeLoopWindow') and self.RangeLoopWindow.isVisible():
                    # If the window is open, update the QListView with tag data
                    current_list = self.RangeLoopWindow.listModel.stringList()
                    current_list.append(tag_data)
                    self.RangeLoopWindow.listModel.setStringList(current_list)
                else:
                    # Show the RangeLoopWindow if it's not open
                    self.TagActionWindow = TagActionWindow()
                    
                    # Set up the RangeLoopWindow if not already done
                    self.TagActionWindow.show()
    
                    # Add the tag data to the QListView
                    # self.RangeLoopWindow.listModel.setStringList([tag_data])
    
            elif time.time() > self.t:
                self.infoLbl_3.setText("Present Next Tag")
                self.t = time.time()
        
        # Check if the range_value is empty
        if range_value == '':
            handle_tag_action()
        else:
            # Convert range_value to integer and check if it is greater than 0
            try:
                range_value_int = int(range_value)
                if range_value_int > 0:
                    handle_tag_action()
            except ValueError:
                print("Invalid value entered. Please enter a valid number.")
    
    def getPortNames(self):
        ports = [ port.portName() for port in QSerialPortInfo().availablePorts() ]
        return ports

    def getPortSelected(self):
        return self.comboBoxComs.currentText()


def getPortName():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class RangeLoopWindow(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Custom Window")
        self.setGeometry(100, 100, 600, 400)  # Adjust the window size as needed

        # Set rounded corners and background color
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-radius: 15px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QTextEdit {
                font-size: 14px;
                border: 3px solid #cc5500;  /* Border color */
                border-radius: 20px;         /* Rounded corners */
                padding: 20px;               /* Padding inside the text edit */
            }
            QPushButton {
                background-color: #cc5500;
                color: white;
                font-size: 14px;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #ff6600;
            }
            .header {
                font-size: 18px;
                font-weight: bold;
                color: #333;
                padding: 10px;
            }
        """)

        # Create main layout
        main_layout = QtWidgets.QVBoxLayout(self)

        # Create header label
        self.headerLabel = QtWidgets.QLabel("BULK TAG SETUP")
        self.headerLabel.setObjectName("header")
        self.headerLabel.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.headerLabel)

        # Create horizontal layout for Start Range and QTextEdit
        start_range_layout = QtWidgets.QHBoxLayout()
        self.startRangeEdit = QtWidgets.QTextEdit()
        self.startRangeEdit.setPlaceholderText("Start Range")
        start_range_layout.addWidget(self.startRangeEdit)
        main_layout.addLayout(start_range_layout)

        # Create horizontal layout for End Range and QTextEdit
        end_range_layout = QtWidgets.QHBoxLayout()
        self.endRangeEdit = QtWidgets.QTextEdit()
        self.endRangeEdit.setPlaceholderText("End Range")
        end_range_layout.addWidget(self.endRangeEdit)
        main_layout.addLayout(end_range_layout)

        # Create and add QListView
        self.listView = QtWidgets.QListView()
        self.listView.setMinimumHeight(150)  # Adjust the height as needed
        main_layout.addWidget(self.listView)

        # Create a model for the QListView
        self.listModel = QStringListModel()
        self.listView.setModel(self.listModel)

        # Create Start Button
        self.startButton = QtWidgets.QPushButton("Start")
        self.startButton.clicked.connect(self.startAction)
        main_layout.addWidget(self.startButton)

        # Create Push Button
        self.pushButton = QtWidgets.QPushButton("Push")
        self.pushButton.clicked.connect(self.pushAction)
        main_layout.addWidget(self.pushButton)

        # Initialize counter and end range
        self.counter = 0
        self.end_range = 0

    def startAction(self):
        # Get start and end range values
        try:
            start_range = int(self.startRangeEdit.toPlainText())
            end_range = int(self.endRangeEdit.toPlainText())
        except ValueError:
            QtWidgets.QMessageBox.warning(self, 'Input Error', 'Please enter valid numbers.')
            return

        # Set the counter to start at start_range and store the end_range
        self.counter = start_range
        self.end_range = end_range

        # Check if range is valid
        if self.counter <= self.end_range:
            self.listModel.setStringList([])  # Clear previous results
            QtWidgets.QMessageBox.information(self, 'Ready', f"Ready to accept tags from {self.counter} to {self.end_range}.")
            print(f"Ready to accept tags from {self.counter} to {self.end_range}.")
        else:
            QtWidgets.QMessageBox.warning(self, 'Error', 'End range must be greater than or equal to start range.')

    def pushAction(self):
        # Retrieve all items from the QListView's model
        items = self.listModel.stringList()
        
        # Prepare data for the popup
        start_tag_number = int(self.startRangeEdit.toPlainText())  # Get the start tag number
        popup_data = ""
        for index, item in enumerate(items):
            # Calculate the tag number based on the start_tag_number and index
            tag_number = start_tag_number + index
            if tag_number > self.end_range:
                QtWidgets.QMessageBox.warning(self, 'Error', 'Tag number exceeds end range.')
                return
            popup_data += f'ROM Code: {item}, Tag Number: {tag_number}\n'
        
        # Show the popup dialog with options to close or save
        self.showPopup(popup_data)

    def showPopup(self, data):
        # Create a QDialog for the popup
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Tag Data")

        # Layout for the dialog
        layout = QtWidgets.QVBoxLayout(dialog)

        # Add a QLabel to display the data
        label = QtWidgets.QLabel(data)
        label.setWordWrap(True)  # Allow text to wrap
        layout.addWidget(label)

        # Add Save and Close buttons
        button_layout = QtWidgets.QHBoxLayout()

        # Save button
        save_button = QtWidgets.QPushButton("Save")
        save_button.clicked.connect(self.saveData)
        button_layout.addWidget(save_button)

        # Close button
        close_button = QtWidgets.QPushButton("Close")
        close_button.clicked.connect(dialog.accept)  # Close the dialog
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        # Set dialog size and show
        dialog.setFixedSize(400, 300)  # Adjust size as needed
        dialog.exec_()

    def send_tag_data(self, tag_string, tag_number, datestamp):
        url = 'https://api.fmafrica.com:4615/TagSetup'
        
        headers = {
            'accept': '*/*',
            'Content-Type': 'application/json'
        }
        
        # Create the payload with the provided data
        payload = {
            "tagString": f"{tag_string}",
            "tagNumber": tag_number,
            "datestamp": f"{datestamp}"
        }
        
        # Send the POST request
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # Check the response
        if response.status_code == 200:
            print("Success:", response.json())
        else:
            print(f"Failed with status code {response.status_code}: {response.text}")

    def saveData(self):
        # Retrieve all items from the QListView's model
        items = self.listModel.stringList()
        
        # Get the start tag number from the Start Range input
        start_tag_number = int(self.startRangeEdit.toPlainText())
    
        # Loop through the items and send each one using the send_tag_data function
        for index, item in enumerate(items):
            tag_number = start_tag_number + index
            
            # Prepare the datestamp (example: you can replace this with the actual date if needed)
            datestamp = datetime.now().strftime('%Y-%m-%d')
            
            # Send each tag's data to the API
            self.send_tag_data(item, tag_number, datestamp)
        
        # Optionally close the RangeLoopWindow after saving
        QtWidgets.QMessageBox.information(
        self,
        'Upload Complete',
        'Tags uploaded successfully.'
        )
        self.close()

    def addTagToListView(self, romcode):
        # Append ROM code with counter as tag number to the QListView
        if self.counter <= self.end_range:
            current_items = self.listModel.stringList()
            new_item = f"{romcode}, {self.counter}"
            current_items.append(new_item)
            self.listModel.setStringList(current_items)
            self.counter += 1  # Increment the counter after each tag
        else:
            QtWidgets.QMessageBox.information(self, 'Range Complete', 'Tagging for the specified range is complete.')

    def beep(self):
        
        pygame.mixer.init()    
        # Load the sound file
        pygame.mixer.music.load(r'beep.mp3')
        # Play the sound
        pygame.mixer.music.play()
        # Wait for 1 second (1000 milliseconds)
        pygame.time.wait(1000)
        # Stop the sound
        pygame.mixer.music.stop()


class SetupNewTagWindow(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("SETUP NEW TAG")
        self.setGeometry(100, 100, 400, 300)
        
        # Set rounded corners and background color
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-radius: 15px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                font-size: 14px;
                border: 1px solid #cc5500;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox {
                font-size: 14px;
                border: 1px solid #cc5500;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #cc5500;
                color: white;
                font-size: 14px;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #ff6600;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)

        self.header = QtWidgets.QLabel("SETUP NEW TAG")
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.header)

        # Tag Number
        self.tagNumberLabel = QtWidgets.QLabel("Tag Number:")
        self.tagNumberEdit = QtWidgets.QLineEdit()
        layout.addWidget(self.tagNumberLabel)
        layout.addWidget(self.tagNumberEdit)

        # Client ID
        self.clientIdLabel = QtWidgets.QLabel("Client ID:")
        self.clientIdEdit = QtWidgets.QLineEdit()
        layout.addWidget(self.clientIdLabel)
        layout.addWidget(self.clientIdEdit)

        # ROM Code
        self.romCodeLabel = QtWidgets.QLabel("ROM Code:")
        self.romCodeEdit = QtWidgets.QLineEdit()
        layout.addWidget(self.romCodeLabel)
        layout.addWidget(self.romCodeEdit)

        # Tag Type
        self.tagTypeLabel = QtWidgets.QLabel("Tag Type:")
        self.tagTypeCombo = QtWidgets.QComboBox()
        self.tagTypeCombo.addItem("Dallas", 1)
        self.tagTypeCombo.addItem("BodyMount", 2)
        self.tagTypeCombo.addItem("RFID", 3)
        layout.addWidget(self.tagTypeLabel)
        layout.addWidget(self.tagTypeCombo)

        # Setup Now Button
        self.setupButton = QtWidgets.QPushButton("Setup Now")
        self.setupButton.clicked.connect(self.setupNow)
        layout.addWidget(self.setupButton)
        
        self.searchNowButton = QtWidgets.QPushButton("Search Now")
        self.searchNowButton.clicked.connect(self.searchNow)
        layout.addWidget(self.searchNowButton)

        # Result Display
        self.resultDisplay = QtWidgets.QTextEdit()
        self.resultDisplay.setReadOnly(True)
        layout.addWidget(self.resultDisplay)

    def setupNow(self):
        tag_number = self.tagNumberEdit.text()
        client_id = self.clientIdEdit.text()
        rom_code = self.romCodeEdit.text()
        tag_type = self.tagTypeCombo.currentData()  # Get the data associated with the selected item
        
        # Prepare the API endpoint and headers
        url = "https://api.fmafrica.com:4615/create-tag"
        headers = {
            'accept': '*/*',
            'Authorization': 'Bearer YOUR_ACCESS_TOKEN',  # Replace with your token
            'Content-Type': 'application/json'
        }
        payload = {
            "clientId": client_id,
            "tagType": tag_type,
            "tagNo": tag_number,
            "romCode": rom_code,
            "action": 1  # Assuming action is 1 for setting up a new tag
        }

        # Make the API call
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            api_response = response.json()  # Assuming the response is in JSON format

            # Display the API response in the text edit
            result_text = (f"Tag Number: {tag_number}\n"
                           f"Client ID: {client_id}\n"
                           f"ROM Code: {rom_code}\n"
                           f"Selected Tag Type: {self.tagTypeCombo.currentText()}\n\n"
                           f"API Response:\n{api_response}")
        except requests.RequestException as e:
            result_text = f"An error occurred: {e}"

        self.resultDisplay.setText(result_text)

    def searchNow(self):
        # Create an instance of TagUi
        self.tag_ui = TagUi()
        self.tag_ui.show()


class UpdateTagWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()       
        self.setWindowTitle("Update Tag")
        self.setGeometry(100, 100, 400, 300)       
        # Set rounded corners and background color
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-radius: 15px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                font-size: 14px;
                border: 1px solid #cc5500;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox {
                font-size: 14px;
                border: 1px solid #cc5500;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #cc5500;
                color: white;
                font-size: 14px;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #ff6600;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)

        self.header = QtWidgets.QLabel("Update Tag")
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.header)

        # Tag Number
        self.tagNumberLabel = QtWidgets.QLabel("Tag Number:")
        self.tagNumberEdit = QtWidgets.QLineEdit()
        layout.addWidget(self.tagNumberLabel)
        layout.addWidget(self.tagNumberEdit)

        # Client ID
        self.clientIdLabel = QtWidgets.QLabel("Client ID:")
        self.clientIdEdit = QtWidgets.QLineEdit()
        layout.addWidget(self.clientIdLabel)
        layout.addWidget(self.clientIdEdit)

        # ROM Code
        self.romCodeLabel = QtWidgets.QLabel("ROM Code:")
        self.romCodeEdit = QtWidgets.QLineEdit()
        layout.addWidget(self.romCodeLabel)
        layout.addWidget(self.romCodeEdit)

        # Tag Type
        self.tagTypeLabel = QtWidgets.QLabel("Tag Type:")
        self.tagTypeCombo = QtWidgets.QComboBox()
        self.tagTypeCombo.addItem("Dallas", 1)
        self.tagTypeCombo.addItem("BodyMount", 2)
        self.tagTypeCombo.addItem("RFID", 3)
        layout.addWidget(self.tagTypeLabel)
        layout.addWidget(self.tagTypeCombo)

        # Update Now Button
        self.updateButton = QtWidgets.QPushButton("Update Now")
        self.updateButton.clicked.connect(self.updateNow)
        layout.addWidget(self.updateButton)
        self.searchNowButton = QtWidgets.QPushButton("Search Now")
        self.searchNowButton.clicked.connect(self.searchNow)
        layout.addWidget(self.searchNowButton)
        # Result Display
        self.resultDisplay = QtWidgets.QTextEdit()
        self.resultDisplay.setReadOnly(True)
        layout.addWidget(self.resultDisplay)

    def updateNow(self):
        tag_number = self.tagNumberEdit.text()
        client_id = self.clientIdEdit.text()
        rom_code = self.romCodeEdit.text()
        tag_type = self.tagTypeCombo.currentData()  # Get the data associated with the selected item       
        # Prepare the API endpoint and headers
        url = "https://api.fmafrica.com:4615/update-tag"
        headers = {
            'accept': '*/*',
            'Authorization': 'Bearer YOUR_ACCESS_TOKEN',  # Replace with your token
            'Content-Type': 'application/json'
        }
        payload = {
            "clientId": client_id,
            "tagType": tag_type,
            "tagNo": tag_number,
            "romCode": rom_code,
            "action": 2  # Assuming action is 2 for updating a tag
        }

        # Make the API call
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            api_response = response.json()  # Assuming the response is in JSON format

            # Display the API response in the text edit
            result_text = (f"Tag Number: {tag_number}\n"
               f"Client ID: {client_id}\n"
               f"ROM Code: {rom_code}\n"
               f"Selected Tag Type: {self.tagTypeCombo.currentText()}\n\n"
               f"API Response:\n{api_response}")
        except requests.RequestException as e:
            result_text = f"An error occurred: {e}"

        self.resultDisplay.setText(result_text)

    def searchNow(self):
        # Create an instance of TagUi
        self.tag_ui = TagUi()
        self.tag_ui.show()


class QueryWindow(QtWidgets.QWidget):

    def __init__(self):
        
        super().__init__()
        
        # self.romCodeEdit.setText(clipboard_data)
        self.setWindowTitle("Query Existing  Tag")
        self.setGeometry(100, 100, 400, 300)

        # Set rounded corners and background color
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-radius: 15px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                font-size: 14px;
                border: 1px solid #cc5500;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox {
                font-size: 14px;
                border: 1px solid #cc5500;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #cc5500;
                color: white;
                font-size: 14px;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #ff6600;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)

        self.header = QtWidgets.QLabel("QUERY TAG")
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.header)

        # Tag Number
        self.tagNumberLabel = QtWidgets.QLabel("Tag Number:")
        self.tagNumberEdit = QtWidgets.QLineEdit()
        layout.addWidget(self.tagNumberLabel)
        layout.addWidget(self.tagNumberEdit)

        # Client ID
        self.clientIdLabel = QtWidgets.QLabel("Client ID:")
        self.clientIdEdit = QtWidgets.QLineEdit()
        layout.addWidget(self.clientIdLabel)
        layout.addWidget(self.clientIdEdit)

        # ROM Code
        self.romCodeLabel = QtWidgets.QLabel("ROM Code:")
        self.romCodeEdit = QtWidgets.QLineEdit()
        layout.addWidget(self.romCodeLabel)
        layout.addWidget(self.romCodeEdit)
        
        print()
        self.romCodeEdit.setText("014344B51E000049")

        # Tag Type
        self.tagTypeLabel = QtWidgets.QLabel("Tag Type:")
        self.tagTypeCombo = QtWidgets.QComboBox()
        self.tagTypeCombo.addItem("Dallas", 1)
        self.tagTypeCombo.addItem("BodyMount", 2)
        self.tagTypeCombo.addItem("RFID", 3)
        layout.addWidget(self.tagTypeLabel)
        layout.addWidget(self.tagTypeCombo)

        # Query Now Button
        self.queryButton = QtWidgets.QPushButton("Query Now")
        self.queryButton.clicked.connect(self.queryNow)
        layout.addWidget(self.queryButton)

        # Search Now Button
        # self.searchNowButton = QtWidgets.QPushButton("Search Now")    
        # self.searchNowButton.clicked.connect(self.searchNow)
        # layout.addWidget(self.searchNowButton)
        
        # Result Display
        self.resultDisplay = QtWidgets.QTextEdit()
        self.resultDisplay.setReadOnly(True)
        layout.addWidget(self.resultDisplay)

    def queryNow(self):
        
        token = 'test'
        
        # Login URL and headers
        loginUrl = "https://api.fmafrica.com:4615/api/Users/login"
        headers = {
            "accept": "*/*",
            "Content-Type": "application/json"
        }
        data = {
            "email": "Naledi@nano.com",
            "password": "P@ssword"
        }
        
        # Perform login request
        response = requests.post(loginUrl, headers=headers, json=data)
        
        if response.status_code == 200:
            # Parse the JSON response to get the token
            response_data = json.loads(response.text)
            token = response_data.get('token')  # Adjust 'token' based on the actual key in the response
            print(token)
        else:
            print(f"Login failed, status code: {response.status_code}")
            return

        # Retrieve form values
        tag_number = self.tagNumberEdit.text()
        client_id = self.clientIdEdit.text()
        rom_code = self.romCodeEdit.text()
        tag_type = self.tagTypeCombo.currentData()  # Get the data associated with the selected item
    
        # Create tag URL and headers
        url = "https://api.fmafrica.com:4615/create-tag"
        headers = {
            "accept": "*/*",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {
            "clientId": f"{client_id}",
            "tagType": tag_type,
            "tagNo": f"{tag_number}",
            "romCode": f"{rom_code}",
            "action": 0
        }
        
        # Perform create tag request
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            # Parse and display the response JSON
            response_data = json.loads(response.text)
            print(f"Query tag response: {response_data}")
            
            # Prepare the message
            message = (
                f"Tag Information:\n\n"
                f"Tag ID: {response_data[0].get('RomCode', 'N/A')}\n"
                f"Client ID: {response_data[0].get('ClientId', 'N/A')}\n"
                f"RomCode Status: {response_data[0].get('RomCodeStatus', 'N/A')}\n"
                f"Client ID Status: {response_data[0].get('ClientIdStatus', 'N/A')}"
            )
            
            # Create a QMessageBox to show the message
            msg_box = QtWidgets.QMessageBox()
            msg_box.setIcon(QtWidgets.QMessageBox.Information)
            msg_box.setWindowTitle("Tag Information")
            msg_box.setText(message)
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
            
            # Show the message box
            msg_box.exec_()
        else:
            # Handle the error
            print(f"Failed to create tag, status code: {response.text}")
            msg_box = QtWidgets.QMessageBox()
            msg_box.setIcon(QtWidgets.QMessageBox.Critical)
            msg_box.setWindowTitle("Error")
            msg_box.setText(f"Failed to create tag. Status code: {response.status_code}")
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg_box.exec_()

    def searchNow(self):
        # Create an instance of TagUi
        self.tag_ui = TagUi()
        self.tag_ui.show


class TagActionWindow(QtWidgets.QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tag Actions")
        self.setGeometry(100, 100, 300, 150)
        
        # Initialize the tag reader
        self.tag_reader = max9097TagReader()
        # Set up the layout
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Create buttons
        self.queryButton = QtWidgets.QPushButton("Query and Existing Tag")
        self.createButton = QtWidgets.QPushButton("Setup A New Tag")
        self.deleteButton = QtWidgets.QPushButton("Update Existing Tag")
        self.rangeButton = QtWidgets.QPushButton("Range Tag Setup")
        
        # Add buttons to the layout
        layout.addWidget(self.queryButton)
        layout.addWidget(self.createButton)
        layout.addWidget(self.deleteButton)
        layout.addWidget(self.rangeButton)
        
        self.setLayout(layout)
        
        # Apply modern styling
        self.apply_styles()

        # Connect buttons to their respective functions
        self.queryButton.clicked.connect(self.query_tag)
        self.createButton.clicked.connect(self.setup_tag)
        self.deleteButton.clicked.connect(self.update_tag)
        self.rangeButton.clicked.connect(self.rang_Tag)

    def apply_styles(self):
        style = """
            QWidget {
                background-color: #f0f0f0;
                border-radius: 15px;
                padding: 10px;
            }
            QPushButton {
                background-color: #cc5500;
                color: white;
                font-size: 14px;
                border-radius: 10px; /* Rounded corners for buttons */
                padding: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #ff6600;
            }
            QPushButton:pressed {
                background-color: #cc5500;
                border-style: inset;
            }
        """
        self.setStyleSheet(style)

    def query_tag(self):
        try:
            clipboard_data = pyperclip.paste()
            print(f"Clipboard data    {clipboard_data}")
            self.query_window = QueryWindow()
            self.query_window.show()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def rang_Tag(self):
        
        self.RangeTagWindow = RangeTagWindow()
        self.RangeTagWindow.show()

    def setup_tag(self):
        self.SetupNewTagWindow = SetupNewTagWindow()
        self.SetupNewTagWindow.show()
    
    def update_tag(self):
        self.UpdateTagWindow = UpdateTagWindow()
        self.UpdateTagWindow.show()
    
    def login_and_get_token(self, email, password):
        url = "https://api.fmafrica.com:4615/api/Users/login"
        headers = {
            "accept": "*/*",
            "Content-Type": "application/json"
        }
        data = {
            "email": email,
            "password": password
        }
    
        response = requests.post(url, headers=headers, json=data)
    
        if response.status_code == 200:
            # Parse the JSON response to get the token
            response_data = json.loads(response.text)
            token = response_data.get('token')  # Adjust 'token' based on the actual key in the response
            return token
        else:
            # Handle the error
            print(f"Failed to login, status code: {response.status_code}")
            return None
    
    def create_tag(self, token, client_id, tag_type, tag_no, rom_code, action):
        
        url = "https://api.fmafrica.com:4615/create-tag"
        headers = {
            "accept": "*/*",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {
            "clientId": client_id,
            "tagType": tag_type,
            "tagNo": tag_no,
            "romCode": rom_code,
            "action": action
        }
    
        response = requests.post(url, headers=headers, json=data)
    
        if response.status_code == 200:
            # Return the response JSON if the request is successful
            return response.json()
        else:
            # Handle the error
            print(f"Failed to create tag, status code: {response.status_code}")
            return None

        
if __name__ == "__main__":
    # ports = getPortName()
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

