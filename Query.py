'''
I BEGIN BY IMPORTING ALL THE PACKAGES I WILL NEED
'''
import requests
import json
import serial
import time
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QClipboard

class TagUi(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle("Tag Reader")
        MainWindow.resize(300, 300)
        
        # Set rounded corners and background color
        MainWindow.setStyleSheet("""
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
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #ff6600;
            }
        """)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        # Layouts
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        self.mainLayout.setSpacing(20)

        self.infoLabel = QtWidgets.QLabel("ROM Code will appear here")
        self.portLabel = QtWidgets.QLabel("Port:")
        self.portComboBox = QtWidgets.QComboBox()
        self.connectButton = QtWidgets.QPushButton("Connect")
        self.timerLabel = QtWidgets.QLabel("Timer Control:")
        self.timerControlButton = QtWidgets.QPushButton("Start Timer")

        # Create a form layout for the serial port controls
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.addRow(self.portLabel, self.portComboBox)
        self.formLayout.addRow(self.timerLabel, self.timerControlButton)
        
        # Create a layout for the buttons
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.addWidget(self.connectButton)
        
        # Create a vertical layout for the page
        self.pageLayout = QtWidgets.QVBoxLayout()
        self.pageLayout.addWidget(self.infoLabel)
        self.pageLayout.addLayout(self.formLayout)
        self.pageLayout.addLayout(self.buttonLayout)
        
        self.mainLayout.addLayout(self.pageLayout)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Hide timer label and button
        self.timerLabel.setVisible(False)
        self.timerControlButton.setVisible(False)

        # Populate ports and set up connections
        self.populate_ports()
        self.connectButton.clicked.connect(self.connect_to_port)
        self.timerControlButton.clicked.connect(self.toggle_timer)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.read_tag)
        self.tag_reader = None

        # Apply custom style
        self.apply_styles()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Tag Reader"))
        self.infoLabel.setText(_translate("MainWindow", "Tag Information will appear here"))
        self.portLabel.setText(_translate("MainWindow", "Port:"))
        self.connectButton.setText(_translate("MainWindow", "Connect"))
        self.timerLabel.setText(_translate("MainWindow", "Timer Control:"))
        self.timerControlButton.setText(_translate("MainWindow", "Start Timer"))
    def populate_ports(self):
        ports = [port.portName() for port in QSerialPortInfo.availablePorts()]
        self.portComboBox.addItems(ports)

    def connect_to_port(self):
        port = self.portComboBox.currentText()
        if port:
            self.tag_reader = max9097TagReader()
            self.tag_reader.connect(COMport=port)
            self.infoLabel.setText(f"Connected to {port}")
            self.timer.start(1000)  # Start timer with 1-second interval

    def toggle_timer(self):
        if self.timer.isActive():
            self.timer.stop()
            self.timerControlButton.setText("Start Timer")
        else:
            self.timer.start(1000)
            self.timerControlButton.setText("Stop Timer")

    def read_tag(self):
        if self.tag_reader:
            self.tag_reader.readTagReader()
            if self.tag_reader.isTagData():
                tag_data = self.tag_reader.getTagData(pData=self.tag_reader)
                self.infoLabel.setText(f"Tag Data: {self.tag_reader.tagString}")
                # Show tag message box
                if self.tag_reader.tagString != '0000000000000000':

                    self.tag_reader.show_tag_message(self.tag_reader.tagString)

    def apply_styles(self):
        style = """
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
        QWidget {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 14px;
            background-color: #F5F5F5;
            border-radius: 10px;
        }
        QLabel {
            color: #333;
            font-weight: bold;
        }
        QPushButton {
            background-color: #cc5500; /* Microsoft blue */
            color: white;
            border: none;
            border-radius: 12px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #0056A0; /* Darker blue */
        }
        QComboBox {
            font-size: 14px;
            border: 1px solid #cc5500;
            border-radius: 5px;
            padding: 5px;
        }
        QComboBox::drop-down {
            border-left: 1px solid #0078D4;
        }
        QWidget#centralwidget {
            background-color: #FFFFFF; /* White background */
            border-radius: 15px;
            padding: 10px;
        }
        """
        self.setStyleSheet(style)
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
        
    def close(self):
        self.uart.close()
        
    def cmd_reset(self):
        self.set_mode(MAX9097._MODE_CMD)
        self.uart.write([0xC1]) # reset-pulse
        r = self.uart.read()
        if r != b'\xCD':
            print("ERROR")
        
    def cmd_write_bit(self, v):
        self.set_mode(MAX9097._MODE_CMD)
        if v != 0:
            self.uart.write([0x91]) # "on" bit
        else:
            self.uart.write([0x81]) # "off" bit
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
        return self.dat_write([0xFF]*n)

    def crc_check(self, rBytes):
        crc = 0
        for b in rBytes:
            if(b < 0):
                b += 256    
            for i in range(8):
                odd = ((b^crc) & 1) == 1
                crc >>= 1
                b >>= 1
                if(odd):
                    crc ^= 0x8C
        return crc        
class max9097TagReader:
    def __init__(self):
        print("INFO - max9097TagReader started")
        self.tagString = "0000000000000000"

    def connect(self, COMport='/dev/ttyUSB0', timeout=0.03):
        self.bus = MAX9097(COMport, timeout)
        print("INFO - OneWire connected on port : %s" % COMport)

    def readTagReader(self):
        try:
            self.bus.mode = MAX9097._MODE_CMD
            # initiate an initial read
            self.bus.dat_write([0xCC, 0x33])
            self.tagString = self._crc_check()
            return self.tagString
        except Exception as e:
            print(f"Error reading tag: {e}")
            return None

    def isTagData(self):
        # Check if valid tag data exists
        return len(self.tagString) == 16 and self.tagString.isalnum()

    def getTagData(self, pData):
        if pData.isTagData():
            return pData.tagString
        else:
            return "No valid tag data"

    def _crc_check(self):
        self.bus.set_mode(MAX9097._MODE_CMD)
        self.bus.dat_write([0xCC, 0x33])
        r = self.bus.dat_read(16)
        c = self.bus.crc_check(r)
        if c != 0:
            raise Exception(f"CRC check failed: {c}")
        tag_data = ''.join([format(b[0], '02X') for b in r])
        return tag_data
class max9097TagReader:

    def __init__(self):
        print("INFO - max9097TagReader started")
        self.tagString = "0000000000000000"
        self.app = QtWidgets.QApplication.instance()  # Get the existing QApplication instance

    def connect(self, COMport='/dev/ttyUSB0', timeout=0.03):
        self.bus = MAX9097(COMport, timeout)
        print("INFO - OneWire connected on port : %s" % COMport)

    def readTagReader(self):
        try:
            self.bus.mode = self.bus._MODE_CMD
            self.bus.dat_write([0x33])           # read-rom
            ans = self.bus.dat_read(8)           # little-endian (family + SN[6] + CRC)
            if any(x == '' for x in ans):
                print("WARNING - Invalid Rx : %s" % ans)
                time.sleep(1.0)
            else:
                barray = [int.from_bytes(x, byteorder='little') for x in ans]
                crc = self.bus.crc_check(barray)
                if (ans[0] == b'\x01' or ans[0] == b'\x08') and crc == 0:
                    rcv = ['%02X'%a for a in reversed(barray)]
                    self.tagString = rcv[7] + rcv[6] + rcv[5] + rcv[4] + rcv[3] + rcv[2] + rcv[1] + rcv[0]
                    
                    # Print to console
                    print("TAG - %s" % self.tagString)

                    # Show the tag in a message box
                    self.show_tag_message(self.tagString)
                    
            self.bus.clear()
        except:
            print("ERROR- readTagReader : %s" % sys.exc_info()[1])

    def show_tag_message(self, tag_string):
        # Show the tag in a custom dialog
        dialog = TagMessageBox(tag_string, self.app.activeWindow())
        dialog.exec_()

    def clearTagBuffer(self):
        self.tagString = "0000000000000000"

    def isTagData(self):
        return self.tagString != "0000000000000000"

    def getTagData(self, pData):
        sTag = self.tagString
        pData.TagString = sTag
        self.clearTagBuffer()
        return True
class TagMessageBox(QtWidgets.QDialog):

    def __init__(self, tag_string, parent=None):
        super(TagMessageBox, self).__init__(parent)
        self.setWindowTitle("Tag Detected")
        self.tag_string = tag_string
        self.init_ui()
        
    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        # Tag information label
        self.tag_label = QtWidgets.QLabel(f"TAG - {self.tag_string}")
        layout.addWidget(self.tag_label)

        # Copy button
        self.copy_button = QtWidgets.QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(self.copy_button)

        # Close button
        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

    def copy_to_clipboard(self):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.tag_string)
class Menu(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 400)
        
        # Set rounded corners and background color
        MainWindow.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
                border-radius: 15px;
            }
            QLabel#header {
                font-size: 20px;
                font-weight: bold;
                color: #cc5500;
            }
            QLabel#footer {
                font-size: 10px;
                color: #808080;
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

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.header = QtWidgets.QLabel(self.centralwidget)
        self.header.setObjectName("header")
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.header)

        self.button_setup_new_tag = QtWidgets.QPushButton(self.centralwidget)
        self.button_setup_new_tag.setText("Setup New Tag")
        self.verticalLayout.addWidget(self.button_setup_new_tag)
        self.button_setup_new_tag.clicked.connect(self.showNewTagScreen)

        self.button_query_tag = QtWidgets.QPushButton(self.centralwidget)
        self.button_query_tag.setText("Query an Existing Tag")
        self.verticalLayout.addWidget(self.button_query_tag)
        self.button_query_tag.clicked.connect(self.showQueryWindow)  # Connect to the method
        '''
        self.button_delete_tag = QtWidgets.QPushButton(self.centralwidget)
        self.button_delete_tag.setText("Delete an Existing Tag")
        self.verticalLayout.addWidget(self.button_delete_tag)
        '''
        self.button_update_tag = QtWidgets.QPushButton(self.centralwidget)
        self.button_update_tag.setText("Update an Existing Tag")
        self.verticalLayout.addWidget(self.button_update_tag)
        self.button_update_tag.clicked.connect(self.showUpdateTagScreen)  # Connect to the method

        self.footer = QtWidgets.QLabel(self.centralwidget)
        self.footer.setObjectName("footer")
        self.footer.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.footer)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.queryWindow = None  # Initialize the QueryWindow variable
        self.SetupNewTagWindow = None  # Initialize the QueryWindow variable
        self.UpdateTagWindow = None  # Initialize the QueryWindow variable

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Dashboard"))
        self.header.setText(_translate("MainWindow", "FUEL MANAGEMENT AFRICA"))
        self.footer.setText(_translate("MainWindow", "Fuelmanagement Africa PtyLtd 2024 All rights reserved."))

    def showQueryWindow(self):
        self.queryWindow = QueryWindow()
        self.queryWindow.show()
    def showNewTagScreen(self):
        self.SetupNewTagWindow = SetupNewTagWindow()
        self.SetupNewTagWindow.show()
        print('Set up new tag function')
    def showUpdateTagScreen(self):
        self.UpdateTagWindow = UpdateTagWindow()
        self.UpdateTagWindow.show()
        print('Set up new tag function')
class Ui_BeLogin(object):
    def setupUi(self, BeLogin):
        BeLogin.setObjectName("BeLogin")
        BeLogin.resize(700, 700)  # Set the initial size

        # Set the fixed size
        BeLogin.setFixedSize(700, 700)

        # Set the window icon
        BeLogin.setWindowIcon(QtGui.QIcon("rfid.png"))

        # Set rounded corners and background color
        BeLogin.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
                border-radius: 15px;
            }
            QLabel#header {
                font-size: 20px;
                font-weight: bold;
                color: #cc5500;
            }
            QLabel#footer {
                font-size: 10px;
                color: #808080;
            }
            QLineEdit {
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
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
            QLabel#errorLabel {
                color: red;
                font-size: 12px;
                margin-top: 10px;
            }
        """)

        self.centralwidget = QtWidgets.QWidget(BeLogin)
        self.centralwidget.setObjectName("centralwidget")
        
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        # Create a QLabel for the image
        self.imageLabel = QtWidgets.QLabel(self.centralwidget)
        self.imageLabel.setObjectName("imageLabel")
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        # Load the image
        self.imageLabel.setPixmap(QtGui.QPixmap("FMA.png"))
        # Add the image label to the layout
        self.verticalLayout.addWidget(self.imageLabel)

        self.header = QtWidgets.QLabel(self.centralwidget)
        self.header.setObjectName("header")
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.header)

        self.username = QtWidgets.QLineEdit(self.centralwidget)
        self.username.setFixedHeight(30)
        self.username.setPlaceholderText("Username")
        self.verticalLayout.addWidget(self.username)

        self.password = QtWidgets.QLineEdit(self.centralwidget)
        self.password.setFixedHeight(30)
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.verticalLayout.addWidget(self.password)

        self.loginButton = QtWidgets.QPushButton(self.centralwidget)
        self.loginButton.setObjectName("loginButton")
        self.loginButton.clicked.connect(self.login)  # Connect the button to the login method
        self.verticalLayout.addWidget(self.loginButton)

        self.errorLabel = QtWidgets.QLabel(self.centralwidget)
        self.errorLabel.setObjectName("errorLabel")
        self.errorLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.errorLabel)

        self.footer = QtWidgets.QLabel(self.centralwidget)
        self.footer.setObjectName("footer")
        self.footer.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.footer)

        BeLogin.setCentralWidget(self.centralwidget)

        self.retranslateUi(BeLogin)
        QtCore.QMetaObject.connectSlotsByName(BeLogin)

        self.queryWindow = None  # Initialize the QueryWindow variable

    def retranslateUi(self, BeLogin):
        _translate = QtCore.QCoreApplication.translate
        BeLogin.setWindowTitle(_translate("BeLogin", "Login"))
        self.header.setText(_translate("BeLogin", ""))
        self.loginButton.setText(_translate("BeLogin", "LOGIN"))
        self.footer.setText(_translate("Footer", "Fuelmanagement Africa PtyLtd 2024 © All rights reserved."))

    def login(self):
        email = self.username.text()
        password = self.password.text()

        url = "https://api.fmafrica.com:4801/api/Users/login"
        payload = json.dumps({
            "email": f"{email}",
            "password": f"{password}"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors
            response_text = response.text

            if response.status_code == 200:
                result_text = "Login successful!"
                self.errorLabel.setStyleSheet("color: green;")
                self.showMenuWindow()  # Show the QueryWindow upon successful login
                BeLogin.close()  
            else:
                result_text = "Incorrect Username or Password."
                self.errorLabel.setStyleSheet("color: red;")
        except requests.RequestException as e:
            result_text = "Incorrect Username or Password."
            self.errorLabel.setStyleSheet("color: red;")

        self.errorLabel.setText(result_text)

    def showQueryWindow(self):
        self.queryWindow = QueryWindow()
        self.queryWindow.show()
    def showMenuWindow(self):
        self.menuWindow = QtWidgets.QMainWindow()
        self.ui = Menu()
        self.ui.setupUi(self.menuWindow)
        self.menuWindow.show()
        QtWidgets.QWidget().close()  # Close the login window
class QueryWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Query Tag")
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
        self.searchNowButton = QtWidgets.QPushButton("Search Now")
        self.searchNowButton.clicked.connect(self.searchNow)
        layout.addWidget(self.searchNowButton)

        # Result Display
        self.resultDisplay = QtWidgets.QTextEdit()
        self.resultDisplay.setReadOnly(True)
        layout.addWidget(self.resultDisplay)

    def queryNow(self):
        tag_number = self.tagNumberEdit.text()
        client_id = self.clientIdEdit.text()
        rom_code = self.romCodeEdit.text()
        tag_type = self.tagTypeCombo.currentData()  # Get the data associated with the selected item
        
        # Prepare the API endpoint and headers
        url = "https://api.fmafrica.com:4615/create-tag"  # Updated endpoint
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
            "action": 0  # Assuming action is always 0 for this example
        }

        # Make the API call
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            api_response = response.json()  # Parse JSON response

            # Update the result display with the response
            self.resultDisplay.setPlainText(json.dumps(api_response, indent=4))
        except requests.RequestException as e:
            self.resultDisplay.setPlainText(str(e))
    
    def searchNow(self):
        # Create an instance of TagUi
        self.tag_ui = TagUi()
        self.tag_ui.show()
class SetupNewTagWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Setup New Tag")
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

        self.header = QtWidgets.QLabel("UPDATE TAG")
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





class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 400)
        
        # Set rounded corners and background color
        MainWindow.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
                border-radius: 15px;
            }
            QLabel#header {
                font-size: 20px;
                font-weight: bold;
                color: #cc5500;
            }
            QLabel#footer {
                font-size: 10px;
                color: #808080;
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

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.header = QtWidgets.QLabel(self.centralwidget)
        self.header.setObjectName("header")
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.header)

        self.button_setup_new_tag = QtWidgets.QPushButton(self.centralwidget)
        self.button_setup_new_tag.setText("Setup New Tag")
        self.button_setup_new_tag.clicked.connect(self.openSetupNewTagWindow)  # Connect to open the setup window
        self.verticalLayout.addWidget(self.button_setup_new_tag)

        self.button_query_tag = QtWidgets.QPushButton(self.centralwidget)
        self.button_query_tag.setText("Query an Existing Tag")
        self.button_query_tag.clicked.connect(self.openQueryWindow)  # Connect to open the query window
        self.verticalLayout.addWidget(self.button_query_tag)

        #self.button_delete_tag = QtWidgets.QPushButton(self.centralwidget)
        #self.button_delete_tag.setText("Delete an Existing Tag")
        #self.verticalLayout.addWidget(self.button_delete_tag)

        self.button_update_tag = QtWidgets.QPushButton(self.centralwidget)
        self.button_update_tag.setText("Update an Existing Tag")
        self.button_update_tag.clicked.connect(self.openUpdateTagWindow)  # Connect to open the update window
        self.verticalLayout.addWidget(self.button_update_tag)

        self.footer = QtWidgets.QLabel(self.centralwidget)
        self.footer.setObjectName("footer")
        self.footer.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.footer)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Dashboard"))
        self.header.setText(_translate("MainWindow", "FUEL MANAGEMENT AFRICA"))
        self.footer.setText(_translate("MainWindow", "Fuelmanagement Africa PtyLtd 2024 © All rights reserved."))

    def openQueryWindow(self):
        self.query_window = QueryWindow()
        self.query_window.show()

    def openSetupNewTagWindow(self):
        self.setup_new_tag_window = SetupNewTagWindow()
        self.setup_new_tag_window.show()

    def openUpdateTagWindow(self):
        self.update_tag_window = UpdateTagWindow()
        self.update_tag_window.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Create a splash screen for rounded corners effect
    splash_pix = QtGui.QPixmap(600, 400)
    splash_pix.fill(QtCore.Qt.transparent)
    splash = QtWidgets.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    BeLogin = QtWidgets.QMainWindow()
    ui = Ui_BeLogin()
    ui.setupUi(BeLogin)
    BeLogin.show()
    sys.exit(app.exec_())