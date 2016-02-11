#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Puzzlebox - Jigsaw - Plug-in - Orbit
#
# Copyright Puzzlebox Productions, LLC (2013-2015)

__changelog__ = """\
Last Update: 2015.01.17
"""

__todo__ = """
"""

import os, string, sys, time

import Puzzlebox.Orbit.Configuration as configuration

if configuration.ENABLE_PYSIDE:
	try:
		from PySide import QtCore, QtGui, QtNetwork
		if configuration.DEFAULT_ORBIT_AUDIO_FRAMEWORK == 'Phonon':
			try:
				from PySide.phonon import Phonon
			except Exception, e:
				print "ERROR: [Plugin:Orbit] Exception importing Phonon:",
				print e
				configuration.DEFAULT_ORBIT_AUDIO_FRAMEWORK = 'QSound'
	except Exception, e:
		print "ERROR: [Plugin:Orbit] Exception importing PySide:",
		print e
		configuration.ENABLE_PYSIDE = False
	else:
		print "INFO: [Plugin:Orbit] Using PySide module"

if not configuration.ENABLE_PYSIDE:
	print "INFO: [Plugin:Orbit] Using PyQt4 module"
	from PyQt4 import QtCore, QtGui, QtNetwork
	if configuration.DEFAULT_ORBIT_AUDIO_FRAMEWORK == 'Phonon':
			try:
				from PyQt4.phonon import Phonon
			except Exception, e:
				print "ERROR: [Plugin:Orbit] Exception importing Phonon:",
				print e
				configuration.DEFAULT_ORBIT_AUDIO_FRAMEWORK = 'QSound'


try:
	from Puzzlebox.Jigsaw.Interface_Plot import *
	MATPLOTLIB_AVAILABLE = True
except Exception, e:
	print "ERROR: Exception importing Puzzlebox.Jigsaw.Interface_Plot:",
	print e
	MATPLOTLIB_AVAILABLE = False

#MATPLOTLIB_AVAILABLE = False

if (sys.platform == 'win32'):
	DEFAULT_IMAGE_PATH = 'images'
elif (sys.platform == 'darwin'):
	DEFAULT_IMAGE_PATH = 'images'
else:
	DEFAULT_IMAGE_PATH = '/usr/share/puzzlebox_orbit/images'


try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	_fromUtf8 = lambda s: s


from Puzzlebox.Orbit.Design_Plugin_Orbit import Ui_Form as Design

import Puzzlebox.Orbit.Protocol_Orbit as protocol_orbit
#import puzzlebox_logger


#####################################################################
# Globals
#####################################################################

DEBUG = 1

THINKGEAR_POWER_THRESHOLDS = { \
	
	'concentration': { \
		0: 0, \
		10: 0, \
		20: 0, \
		30: 0, \
		40: 0, \
		50: 0, \
		60: 0, \
		70: 0, \
		71: 0, \
		72: 60, \
		73: 62, \
		74: 64, \
		75: 66, \
		76: 68, \
		77: 70, \
		78: 72, \
		79: 74, \
		80: 76, \
		81: 78, \
		82: 80, \
		83: 82, \
		84: 84, \
		85: 86, \
		86: 88, \
		87: 90, \
		88: 90, \
		89: 90, \
		90: 100, \
		100: 100, \
		}, \
	
	'relaxation': { \
		0: 0, \
		10: 0, \
		20: 0, \
		30: 0, \
		40: 0, \
		50: 0, \
		60: 0, \
		70: 0, \
		80: 0, \
		90: 0, \
		100: 0, \
		}, \
	
} # THINKGEAR_POWER_THRESHOLDS

ORBIT_LABEL_TITLE = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'Sans'; font-size:10pt; font-weight:400; font-style:normal;">
<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><a href="http://orbit.puzzlebox.info"><span style=" font-size:11pt; font-weight:600; text-decoration: none; color:#000000;">Puzzlebox<br />Orbit</span></a></p></body></html>
'''

ORBIT_LABEL_HELP_WEB_ADDRESS = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'Sans'; font-size:10pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><a href="http://orbit.puzzlebox.info"><span style="text-decoration: none; color:#000000;; color:#0000ff;">http://orbit.puzzlebox.info</span></a></p></body></html>
'''

#####################################################################
# Classes
#####################################################################

class puzzlebox_jigsaw_plugin_orbit(QtGui.QWidget, Design):
	
	def __init__(self, log, tabIndex=None, DEBUG=DEBUG, parent=None):
		
		self.log = log
		self.DEBUG = DEBUG
		self.parent = parent
		self.tabIndex = tabIndex
		
		QtGui.QWidget.__init__(self, parent)
		self.setupUi(self)
		
		self.configuration = configuration
		self.thresholds = THINKGEAR_POWER_THRESHOLDS
		
		self.configureSettings()
		self.connectWidgets()
		
		self.mediaState = None
		
		if self.configuration.DEFAULT_ORBIT_AUDIO_FRAMEWORK == 'Phonon':
			self.initializeAudioPhonon()
		else:
			self.initializeAudio()
		
		self.name = "Jigsaw-Plugin-Orbit"
		self.baseWidget = self.horizontalLayoutWidget
		self.tabTitle = _fromUtf8("Orbit")
		
		if self.tabIndex == None:
			self.parent.tabWidget.addTab(self.baseWidget, self.tabTitle)
		else:
			self.parent.tabWidget.insertTab(self.tabIndex, self.baseWidget, self.tabTitle)
		
		self.warnings = []
		
		self.customDataHeaders = []
		self.protocolSupport = ['EEG']
		
		self.current_power = 0
		
		self.pitch = 0
		self.throttle = 0
		self.yaw = 0
		self.updateFlightCharateristics()
		
		self.protocol = None
	
	
	##################################################################
	
	def configureSettings(self):
		
		self.parent.setProgressBarColor( \
			self.progressBarOrbitConcentration, 'FF0000') # Red
		self.parent.setProgressBarColor( \
			self.progressBarOrbitRelaxation, '0000FF') # Blue
		self.parent.setProgressBarColor( \
			self.progressBarOrbitConnectionLevel, '00FF00') # Green
		self.parent.setProgressBarColor( \
			self.progressBarOrbitPower, 'FCFF00') # Yellow
		
		
		self.progressBarOrbitConcentration.setValue(0)
		self.progressBarOrbitRelaxation.setValue(0)
		self.progressBarOrbitConnectionLevel.setValue(0)
		self.progressBarOrbitPower.setValue(0)
		#self.dialOrbitPower.setValue(0)
		
		#self.pushButtonOrbitOn.setChecked(False)
		#self.pushButtonOrbitOff.setChecked(True)
		
		# Tweak UI Elements
		#self.pushButtonOrbitOn.setVisible(False)
		#self.pushButtonOrbitOff.setVisible(False)
		# Following command removed due to causing a segfault
		#self.verticalLayout_5.removeItem(self.horizontalLayout_3)
		
		
		#self.dialOrbitPower.setEnabled(False)
		
		
		self.pushButtonOrbitConcentrationEnable.setVisible(False)
		self.pushButtonOrbitRelaxationEnable.setVisible(False)
		
		self.comboBoxInfraredPortSelect.setVisible(False)
		#self.pushButtonInfraredSearch.setEnabled(False)
		
		self.pushButtonInfraredConnect.setVisible(False)
		self.pushButtonInfraredSearch.setVisible(False)
		
		#self.textLabelInfraredStatus.setText('Status: Unknown')
		self.textLabelInfraredStatus.setVisible(False)
		
		
		#self.searchInfraredDevices()
		self.updateOrbitDeviceList()
		
		#index = string.uppercase.index(configuration.DEFAULT_ORBIT_HOUSE_CODE)
		#self.comboBoxInfraredHouseCode.setCurrentIndex(index)
		#self.comboBoxInfraredDeviceNumber.setCurrentIndex(configuration.DEFAULT_ORBIT_DEVICE - 1)
		
		
		if MATPLOTLIB_AVAILABLE:
			
			windowBackgroundRGB =  (self.palette().window().color().red() / 255.0, \
			                        self.palette().window().color().green() / 255.0, \
			                        self.palette().window().color().blue() / 255.0)
			
			self.rawEEGMatplot = rawEEGMatplotlibCanvas( \
			                        parent=self.widgetPlotRawEEG, \
			                        width=self.widgetPlotRawEEG.width(), \
			                        height=self.widgetPlotRawEEG.height(), \
			                        title=None, \
			                        axes_top_text='1.0s', \
			                        axes_bottom_text='0.5s', \
			                        facecolor=windowBackgroundRGB)
			
			
			self.historyEEGMatplot = historyEEGMatplotlibCanvas( \
			                            parent=self.widgetPlotHistory, \
			                            width=self.widgetPlotHistory.width(), \
			                            height=self.widgetPlotHistory.height(), \
			                            title=None, \
			                            axes_right_text='percent', \
			                            facecolor=windowBackgroundRGB)
		
		
		# Help
		url = self.configuration.DEFAULT_ORBIT_HELP_URL
		if (url.startswith('path://')):
			url = "file://" + os.path.join( os.getcwd(), url.split('path://')[1] )
		if (sys.platform == 'win32'):
			url = url.replace('file://', '')
		
		if self.DEBUG:
			print "[Jigsaw:Plugin_Orbit] loadWebURL:",
			print url
		
		self.webViewOrbit.load( QtCore.QUrl(url) )
	
	
	##################################################################

	def connectWidgets(self):
		
		self.connect(self.comboBoxInfraredModelName, \
		             QtCore.SIGNAL("activated(int)"), \
		             self.updateOrbitDeviceList)
		
		self.connect(self.pushButtonInfraredSearch, \
		             QtCore.SIGNAL("clicked()"), \
		             self.searchInfraredDevices)
		
		self.connect(self.pushButtonInfraredConnect, \
		             QtCore.SIGNAL("clicked()"), \
		             self.connectInfraredDevice)
		
		self.connect(self.horizontalSliderOrbitConcentration, \
		             QtCore.SIGNAL("valueChanged(int)"), \
		             self.updateSliderConcentration)
		
		self.connect(self.horizontalSliderOrbitRelaxation, \
		             QtCore.SIGNAL("valueChanged(int)"), \
		             self.updateSliderRelaxation)
		
		
		self.connect(self.pushButtonHelicopterHover, \
		             QtCore.SIGNAL("clicked()"), \
		             self.enableHelicopterHover)
		
		self.connect(self.pushButtonHelicopterForward, \
		             QtCore.SIGNAL("clicked()"), \
		             self.enableHelicopterForward)
		
		self.connect(self.pushButtonHelicopterSpinLeft, \
		             QtCore.SIGNAL("clicked()"), \
		             self.enableHelicopterSpinLeft)
		
		self.connect(self.pushButtonHelicopterSpinRight, \
		             QtCore.SIGNAL("clicked()"), \
		             self.enableHelicopterSpinRight)
		
		self.connect(self.pushButtonHelicopterTestFly, \
		             QtCore.SIGNAL("clicked()"), \
		             self.helicopterTestFly)
		
		self.connect(self.pushButtonHelicopterLand, \
		             QtCore.SIGNAL("clicked()"), \
		             self.helicopterLand)
		
		
		self.connect(self.horizontalSliderOrbitPitch, \
		             QtCore.SIGNAL("valueChanged(int)"), \
		             self.updateSliderPitch)
		
		self.connect(self.horizontalSliderOrbitThrottle, \
		             QtCore.SIGNAL("valueChanged(int)"), \
		             self.updateSliderThrottle)
		
		self.connect(self.horizontalSliderOrbitYaw, \
		             QtCore.SIGNAL("valueChanged(int)"), \
		             self.updateSliderYaw)
	
	
	##################################################################
	
	def updateOrbitInterface(self):
		
		# Interface
		self.parent.setWindowTitle("Puzzlebox Orbit")
		self.parent.tabWidget.setTabText(0, "Puzzlebox")
		
		# Session
		self.parent.plugin_session.textLabelTitlePuzzleboxJigsaw.setText(ORBIT_LABEL_TITLE)
		
		self.parent.plugin_session.labelSessionPluginAPI.hide()
		self.parent.plugin_session.checkBoxServiceEnableJSON.setCheckable(False)
		self.parent.plugin_session.checkBoxServiceEnableJSON.hide()
		self.parent.plugin_session.lineSessionPluginAPI.hide()
		
		sessionGraphicFile = os.path.join( \
			os.getcwd(), \
			'images', \
			self.configuration.DEFAULT_ORBIT_SESSION_GRAPHIC)
		
		try:
			self.parent.plugin_session.labelSessionGraphic.setPixmap(QtGui.QPixmap(sessionGraphicFile))
		except Exception, e:
			if self.DEBUG:
				print "ERROR [Plugin:Orbit] Exception:",
				print e

		# EEG
		self.parent.plugin_eeg.checkBoxControlEmulateThinkGear.setVisible(False)
		
		# Help
		self.parent.plugin_help.textLabelTitlePuzzleboxJigsaw.setText(ORBIT_LABEL_TITLE)
		self.parent.plugin_help.labelWebsiteAddress.setText(ORBIT_LABEL_HELP_WEB_ADDRESS)
		self.parent.plugin_help.loadWebURL(self.parent.configuration.DEFAULT_HELP_URL)
	
	
	##################################################################
	
	def connectInfraredDevice(self):
		
		self.comboBoxInfraredModelName.setEnabled(False)
		self.comboBoxInfraredPortSelect.setEnabled(False)
		self.pushButtonInfraredSearch.setEnabled(False)
		
		self.disconnect(self.pushButtonInfraredConnect, \
		                QtCore.SIGNAL("clicked()"), \
		                self.connectInfraredDevice)
		
		self.connect(self.pushButtonInfraredConnect, \
		             QtCore.SIGNAL("clicked()"), \
		             self.disconnectInfraredDevice)
		
		self.pushButtonInfraredConnect.setText('Disconnect')
		
		infraredDevice = str(self.comboBoxInfraredModelName.currentText())
		serial_device = str(self.comboBoxInfraredPortSelect.currentText())
		
		if infraredDevice == 'Puzzlebox Pyramid':
			mode = 'pyramid'
		elif infraredDevice == 'Arduino Infrared Circuit':
			mode = 'arduino'
		#if infraredDevice == 'Mindfulness, Inc. Lotus':
			#mode = 'pyramid'
		if infraredDevice == 'Puzzlebox Bloom':
			mode = 'bloom'
		
		self.protocol = protocol_orbit.puzzlebox_jigsaw_protocol_orbit( \
		                   log=self.log, \
		                   serial_port=serial_device, \
		                   mode=mode, \
		                   command='land', \
		                   DEBUG=self.DEBUG, \
		                   parent=self)
		
		self.protocol.start()
	
	
	##################################################################
	
	def disconnectInfraredDevice(self):
		
		self.comboBoxInfraredModelName.setEnabled(True)
		self.comboBoxInfraredPortSelect.setEnabled(True)
		self.pushButtonInfraredSearch.setEnabled(True)
		
		self.disconnect(self.pushButtonInfraredConnect, \
		                QtCore.SIGNAL("clicked()"), \
		                self.disconnectInfraredDevice)
		
		self.connect(self.pushButtonInfraredConnect, \
		             QtCore.SIGNAL("clicked()"), \
		             self.connectInfraredDevice)
		
		self.pushButtonInfraredConnect.setText('Connect')
		
		
		if self.protocol != None:
			self.protocol.stop()
		
		self.protocol = None
	
	
	##################################################################
	
	def updateOrbitDeviceList(self, index=None):
		
		selection = str(self.comboBoxInfraredModelName.currentText())
		
		if selection == 'Puzzlebox Pyramid':
			
			self.comboBoxInfraredPortSelect.setVisible(True)
			self.pushButtonInfraredConnect.setVisible(True)
			#self.pushButtonInfraredSearch.setEnabled(True)
			self.pushButtonInfraredSearch.setVisible(True)
		
		
		elif selection == 'Puzzlebox Bloom':
			
			self.comboBoxInfraredPortSelect.setVisible(True)
			self.pushButtonInfraredConnect.setVisible(True)
			#self.pushButtonInfraredSearch.setEnabled(True)
			self.pushButtonInfraredSearch.setVisible(True)
		
		
		elif selection == 'Audio Infrared Dongle':
			
			self.comboBoxInfraredPortSelect.setVisible(False)
			self.pushButtonInfraredConnect.setVisible(False)
			#self.pushButtonInfraredSearch.setEnabled(False)
			self.pushButtonInfraredSearch.setVisible(False)
			
			error_message = 'Warning: Differences between audio hardware produce variations in signal output. Audio IR control for the Orbit does not work on all computers.'
			
			if ('audio_infrared_dongle' not in self.warnings):
				QtGui.QMessageBox.information(self, \
				                             'Warning', \
				                              error_message)
			self.warnings.append('audio_infrared_dongle')
		
		
		elif selection == 'Arduino Infrared Circuit':
			
			self.comboBoxInfraredPortSelect.setVisible(True)
			self.pushButtonInfraredConnect.setVisible(True)
			#self.pushButtonInfraredSearch.setEnabled(True)
			self.pushButtonInfraredSearch.setVisible(True)
		
		
		self.searchInfraredDevices()
	
	
	##################################################################
	
	def searchInfraredDevices(self):
		
		self.comboBoxInfraredPortSelect.clear() # doesn't seem to work under OS X
		
		devices = self.searchForSerialDevices()
		
		if devices == []:
			devices = ['No Devices Found']
			self.comboBoxInfraredPortSelect.setEnabled(False)
			self.pushButtonInfraredConnect.setEnabled(False)
		else:
			self.comboBoxInfraredPortSelect.setEnabled(True)
			self.pushButtonInfraredConnect.setEnabled(True)
		
		for device in devices:
			self.comboBoxInfraredPortSelect.addItem(device)
	
	
	##################################################################
	
	def searchForSerialDevices(self, devices=[]):
		
		if (sys.platform == 'win32'):
			
			for portname in self.parent.plugin_eeg.enumerateSerialPorts():
				
				if portname not in devices:
					#portname = self.fullPortName(portname)
					devices.append(portname)
		
		else:
			
			if os.path.exists('/dev/ttyUSB0'):
				devices.append('/dev/ttyUSB0')
			if os.path.exists('/dev/ttyUSB1'):
				devices.append('/dev/ttyUSB1')
			if os.path.exists('/dev/ttyUSB2'):
				devices.append('/dev/ttyUSB2')
			if os.path.exists('/dev/ttyUSB3'):
				devices.append('/dev/ttyUSB3')
			if os.path.exists('/dev/ttyUSB4'):
				devices.append('/dev/ttyUSB4')
			if os.path.exists('/dev/ttyUSB5'):
				devices.append('/dev/ttyUSB5')
			if os.path.exists('/dev/ttyUSB6'):
				devices.append('/dev/ttyUSB6')
			if os.path.exists('/dev/ttyUSB7'):
				devices.append('/dev/ttyUSB7')
			if os.path.exists('/dev/ttyUSB8'):
				devices.append('/dev/ttyUSB8')
			if os.path.exists('/dev/ttyUSB9'):
				devices.append('/dev/ttyUSB9')
			
			if os.path.exists('/dev/ttyACM0'):
				devices.append('/dev/ttyACM0')
			if os.path.exists('/dev/ttyACM1'):
				devices.append('/dev/ttyACM1')
			if os.path.exists('/dev/ttyACM2'):
				devices.append('/dev/ttyACM2')
			if os.path.exists('/dev/ttyACM3'):
				devices.append('/dev/ttyACM3')
			if os.path.exists('/dev/ttyACM4'):
				devices.append('/dev/ttyACM4')
			
			if os.path.exists('/dev/tty.usbmodemfd1221'):
				devices.append('/dev/tty.usbmodemfd1221')
			if os.path.exists('/dev/tty.usbmodemfd1222'):
				devices.append('/dev/tty.usbmodemfd1222')
			if os.path.exists('/dev/tty.usbmodem1411'):
				devices.append('/dev/tty.usbmodem1411')
			if os.path.exists('/dev/tty.usbmodem14231'):
				devices.append('/dev/tty.usbmodem14231')
				
			
			#if os.path.exists('/dev/tty.usbserial-A602050J'):
				#devices.append('/dev/tty.usbserial-A602050J')
			#if os.path.exists('/dev/tty.usbserial-A100MZB6'):
				#devices.append('/dev/tty.usbserial-A100MZB6')
		
		
		if (sys.platform == 'darwin'):
			for device in os.listdir('/dev'):
				if device.startswith('tty.usbserial'):
					devices.append( os.path.join('/dev', device))
				if device.startswith('tty.usbmodem'):
					devices.append( os.path.join('/dev', device))
		
		
		return(devices)
	
	
	##################################################################
	
	def updateSliderConcentration(self):
		
		self.updatePowerThresholds()
	
	
	##################################################################
	
	def updateSliderRelaxation(self):
		
		self.updatePowerThresholds()
	
	
	##################################################################
	
	def updatePowerThresholds(self):
		
		minimum_power = self.configuration.DEFAULT_ORBIT_POWER_MINIMUM
		maximum_power = self.configuration.DEFAULT_ORBIT_POWER_MAXIMUM
		
		# Reset all values to zero
		for index in range(101):
			self.thresholds['concentration'][index] = 0
			self.thresholds['relaxation'][index] = 0
		
		
		concentration_value = self.horizontalSliderOrbitConcentration.value()
		
		if concentration_value != 0:
			
			concentration_range = 101 - concentration_value
			
			for x in range(concentration_range):
				
				current_index = x + concentration_value
				if (concentration_value == 100):
					percent_of_max_power = x # don't divide by zero
				else:
					percent_of_max_power = x / (100.0 - concentration_value)
				new_power = minimum_power + ((maximum_power - minimum_power) * percent_of_max_power)
				self.thresholds['concentration'][current_index] = int(new_power)
		
		
		relaxation_value = self.horizontalSliderOrbitRelaxation.value()
		
		if relaxation_value != 0:
			relaxation_range = 101 - relaxation_value
			
			for x in range(relaxation_range):
				
				current_index = x + relaxation_value
				if (relaxation_value == 100):
					percent_of_max_power = x # don't divide by zero
				else:
					percent_of_max_power = x / (100.0 - relaxation_value)
				new_power = minimum_power + ((maximum_power - minimum_power) * percent_of_max_power)
				self.thresholds['relaxation'][current_index] = int(new_power)
		
		
		#if self.DEBUG > 2:
			#concentration_keys = self.thresholds['concentration'].keys()
			#concentration_keys.sort()
			#for key in concentration_keys:
				#print "%i: %i" % (key, self.thresholds['concentration'][key])
			
			#print
			#print
			
			#concentration_keys = self.thresholds['relaxation'].keys()
			#concentration_keys.sort()
			#for key in concentration_keys:
				#print "%i: %i" % (key, self.thresholds['relaxation'][key])
	
	
	##################################################################
	
	def processCustomData(self, packet):
		
		return(packet)
	
	
	##################################################################
	
	#def connectToThinkGearHost(self):
		
		#pass
	
	
	##################################################################
	
	#def disconnectFromThinkGearHost(self):
		
		#self.progressBarOrbitConcentration.setValue(0)
		#self.progressBarOrbitRelaxation.setValue(0)
		#self.progressBarOrbitConnectionLevel.setValue(0)
	
	
	##################################################################
	
	def updateEEGProcessingGUI(self):
		
		self.progressBarOrbitConcentration.setValue(0)
		self.progressBarOrbitRelaxation.setValue(0)
		self.progressBarOrbitConnectionLevel.setValue(0)
		
		self.stopControl()
	
	
	##################################################################
	
	def processPacketEEG(self, packet):
		
		self.processPacketThinkGear(packet)
		#self.processPacketEmotiv(packet)
	
	
	##################################################################
	
	def processPacketThinkGear(self, packet):
		
		if (self.parent.tabWidget.currentIndex() == \
		    self.tabIndex):
		    #self.parent.tabWidget.indexOf(self.parent.tabOrbit))
			
			#if ('rawEeg' in packet.keys()):
				##self.parent.packets['rawEeg'].append(packet['rawEeg'])
				##value = packet['rawEeg']
				##if MATPLOTLIB_AVAILABLE and \
				##(self.parent.tabWidget.currentIndex() == self.tabIndex):
					##self.rawEEGMatplot.update_figure(value)
				#return
			
			
			if ('rawEeg' in packet.keys()):
				self.rawEEGMatplot.updateValues(packet['rawEeg'])
				return
			
			
			if ('eSense' in packet.keys()):
				
				#self.processEyeBlinks()
				
				if ('attention' in packet['eSense'].keys()):
					if self.pushButtonOrbitConcentrationEnable.isChecked():
						self.progressBarOrbitConcentration.setValue(packet['eSense']['attention'])
						
						# Perform custom function for packet data
						#packet = self.processCustomData(packet)
				
				
				if ('meditation' in packet['eSense'].keys()):
					if self.pushButtonOrbitRelaxationEnable.isChecked():
						self.progressBarOrbitRelaxation.setValue(packet['eSense']['meditation'])
				
				
				self.updateOrbitPower()
				#self.updateProgressBarColors()
				
				if MATPLOTLIB_AVAILABLE:
					self.historyEEGMatplot.updateValues('eSense', packet['eSense'])
					if (self.parent.tabWidget.currentIndex() == self.tabIndex):
						self.historyEEGMatplot.updateFigure('eSense', packet['eSense'])
			
			
			if ('poorSignalLevel' in packet.keys()):
				
				if packet['poorSignalLevel'] == 200:
					value = 0
					self.textLabelOrbitConnectionLevel.setText('No Contact')
				elif packet['poorSignalLevel'] == 0:
					value = 100
					self.textLabelOrbitConnectionLevel.setText('Connected')
				else:
					value = int(100 - ((packet['poorSignalLevel'] / 200.0) * 100))
				#self.textLabelOrbitConnectionLevel.setText('Connection Level')
				self.progressBarOrbitConnectionLevel.setValue(value)
	
	
	##################################################################
	
	#def processPacketEmotiv(self, packet):
		
		#pass
	
	
	##################################################################
	
	def updateOrbitPower(self, new_speed=None):
		
		if new_speed == None:
			
			concentration=self.progressBarOrbitConcentration.value()
			relaxation=self.progressBarOrbitRelaxation.value()
			
			new_speed = self.calculateSpeed(concentration, relaxation)
		
		
		self.current_power = new_speed
		
		# Update GUI
		#if self.pushButtonControlPowerEnable.isChecked():
			#self.progressBarControlPower.setValue(new_speed)
		
		self.progressBarOrbitPower.setValue(new_speed)
		#self.dialOrbitPower.setValue(new_speed)
		
		
		self.triggerActions(power=self.current_power)
		
		
	##################################################################
	
	def triggerActions(self, power):
		
		infraredDevice = str(self.comboBoxInfraredModelName.currentText())
		
		if power == 0:
			
			#self.pushButtonOrbitOn.setChecked(False)
			#self.pushButtonOrbitOff.setChecked(True)
			
			if infraredDevice == 'Puzzlebox Pyramid':
				
				if self.protocol != None:
					#self.protocol.sendCommand('land')
					self.protocol.land()
					self.protocol.setColorWheel(255, 255, 0) # yellow
			
			elif infraredDevice == 'Audio Infrared Dongle':
				self.stopControl()
			
			elif infraredDevice == 'Arduino Infrared Circuit':
				
				if self.protocol != None:
					#self.protocol.sendCommand('land')
					self.protocol.land()
		
			#elif infraredDevice == 'Mindfulness, Inc. Lotus':
				
				#if self.protocol != None:
					#self.protocol.setLotus(power)
			
			elif infraredDevice == 'Puzzlebox Bloom':
				
				if self.protocol != None:
					
					concentration = 0
					relaxation = 0
					
					if (self.horizontalSliderOrbitConcentration.value() > 0):
						concentration = self.progressBarOrbitConcentration.value()
						
					if (self.horizontalSliderOrbitRelaxation.value() > 0):
						relaxation = self.progressBarOrbitRelaxation.value()
					
					self.protocol.updateBloom(power, concentration, relaxation)
		
		else:
			
			#self.pushButtonOrbitOn.setChecked(True)
			#self.pushButtonOrbitOff.setChecked(False)
			
			if infraredDevice == 'Puzzlebox Pyramid':
				
				if self.protocol != None:
					
					#self.protocol.sendCommand('hover')
					
					self.protocol.setThrottle(self.throttle)
					self.protocol.setYaw(self.yaw)
					self.protocol.setPitch(self.pitch)
					self.protocol.setColorWheel(255, 255, 255) # white
			
			elif infraredDevice == 'Audio Infrared Dongle':
				self.playControl()
			
			elif infraredDevice == 'Arduino Infrared Circuit':
				
				if self.protocol != None:
					
					#self.protocol.sendCommand('hover')
					
					self.protocol.setThrottle(self.throttle)
					self.protocol.setYaw(self.yaw)
					self.protocol.setPitch(self.pitch)
			
			#elif infraredDevice == 'Mindfulness, Inc. Lotus':
				
				#if self.protocol != None:
					
					#self.protocol.setLotus(power)
			
			elif infraredDevice == 'Puzzlebox Bloom':
				
				if self.protocol != None:
					
					concentration = 0
					relaxation = 0
					
					if (self.horizontalSliderOrbitConcentration.value() > 0):
						concentration = self.progressBarOrbitConcentration.value()
						
					if (self.horizontalSliderOrbitRelaxation.value() > 0):
						relaxation = self.progressBarOrbitRelaxation.value()
					
					self.protocol.updateBloom(power, concentration, relaxation)

	
	##################################################################
	
	def calculateSpeed(self, concentration, relaxation):
		
		speed = 0
		
		#thresholds = self.configuration.THINKGEAR_POWER_THRESHOLDS
		#thresholds = THINKGEAR_POWER_THRESHOLDS
		
		match = int(concentration)
		
		while ((match not in self.thresholds['concentration'].keys()) and \
			    (match >= 0)):
			match -= 1
		
		
		if match in self.thresholds['concentration'].keys():
			speed = self.thresholds['concentration'][match]
		
		
		match = int(relaxation)
		
		while ((match not in self.thresholds['relaxation'].keys()) and \
			    (match >= 0)):
			match -= 1
		
		if match in self.thresholds['relaxation'].keys():
			speed = speed + self.thresholds['relaxation'][match]
		
		
		# Power settings cannot exceed 100
		# and must be higher than 50
		if (speed > 100):
			speed = 100
		elif (speed < 50):
			speed = 0
		
		
		return(speed)
	
	
	##################################################################
	
	def initializeAudioFilePath(self):
		
		self.audio_file = os.path.join( \
			os.getcwd(), \
			'audio', \
			self.configuration.DEFAULT_ORBIT_AUDIO_FILE)
	
	
	##################################################################
	
	def initializeAudio(self):
		
		if self.DEBUG:
			print "INFO: [Plugin:Orbit] Using QSound Audio Framework"
		
		self.initializeAudioFilePath()
		
		self.media = QtGui.QSound(self.audio_file)
		
		self.media.setLoops(-1) # loop indefinitely
		
		#print dir(self.media)
		
		#self.media.play()
	
	
	##################################################################
	
	def initializeAudioPhonon(self):
		
		if self.DEBUG:
			print "INFO: [Plugin:Orbit] Using Phonon Audio Framework"
		
		self.initializeAudioFilePath()
		
		self.media = Phonon.MediaObject()
		
		#print dir(self.media)
		
		audio = Phonon.AudioOutput(Phonon.MusicCategory)
		Phonon.createPath(self.media, audio)
		f = QtCore.QFile(self.audio_file)
		if f.exists():
			source = Phonon.MediaSource(self.audio_file)
			if source.type() != -1:                 # -1 stands for invalid file
				self.media.setCurrentSource(source)
				
				self.media.play()
				
			else:
				if self.DEBUG:
					print "ERROR: [Plugin:Orbit] Audio control file invalid:",
					print self.audio_file
		else:
			if self.DEBUG:
				print "ERROR: [Plugin:Orbit] Audio control file does not exist:,"
				print self.audio_file
	
	
	##################################################################
	
	def audioFilePlaying(self):
		
		if (self.configuration.DEFAULT_ORBIT_AUDIO_FRAMEWORK == 'Phonon'):
			
			if (self.media.state() == Phonon.State.PlayingState):
				
				return True
			
			else:
				
				return False
				
		
		else:
			
			if self.mediaState == 'Playing':
				
				return True
				
			else:
				
				return False
	
	
	##################################################################
	
	def playControl(self):
		
		if (not self.audioFilePlaying()):
			
			if self.DEBUG:
				print "INFO: [Plugin:Orbit] Playing:",
				print self.audio_file
			
			self.media.play()
			self.mediaState = 'Playing'
	
	
	##################################################################
	
	def stopControl(self):
		
		if (self.audioFilePlaying()):
			
			if self.DEBUG:
				print "INFO: [Plugin:Orbit] Stopping:",
				print self.audio_file
			
			self.media.stop()
			self.mediaState = 'Stopped'
	
	
	##################################################################
	
	def updateSliderPitch(self):
		
		self.updateFlightCharateristics()
	
	
	##################################################################
	
	def updateSliderThrottle(self):
		
		self.updateFlightCharateristics()
	
	
	##################################################################
	
	def updateSliderYaw(self):
		
		self.updateFlightCharateristics()
	
	
	##################################################################
	
	def updateFlightCharateristics(self):
		
		self.pitch = self.horizontalSliderOrbitPitch.value()
		self.throttle = self.horizontalSliderOrbitThrottle.value()
		self.yaw = self.horizontalSliderOrbitYaw.value()
		
		matchFound = False
		
		for mode in self.configuration.ORBIT_CONTROL_SETTINGS.keys():
			
			settings = self.configuration.ORBIT_CONTROL_SETTINGS[mode]
			
			if ((self.throttle == settings['throttle']) and \
			    (self.yaw == settings['yaw']) and \
			    (self.pitch == settings['pitch'])):
				
				matchFound = True
				
				if mode == 'hover':
					if not self.pushButtonHelicopterHover.isChecked():
						self.enableHelicopterHover()
				
				elif mode == 'forward':
					if not self.pushButtonHelicopterForward.isChecked():
						self.enableHelicopterForward()
				
				elif mode == 'spinleft':
					if not self.pushButtonHelicopterSpinLeft.isChecked():
						self.enableHelicopterSpinLeft()
				
				elif mode == 'spinright':
					if not self.pushButtonHelicopterSpinRight.isChecked():
						self.enableHelicopterSpinRight()
		
		
		if not matchFound:
			if self.pushButtonHelicopterHover.isChecked():
				self.disableHelicopterHover()
			elif self.pushButtonHelicopterForward.isChecked():
				self.disableHelicopterForward()
			elif self.pushButtonHelicopterSpinLeft.isChecked():
				self.disableHelicopterSpinLeft()
			elif self.pushButtonHelicopterSpinRight.isChecked():
				self.disableHelicopterSpinRight()
	
	
	##################################################################
	
	def setFlightPlan(self, mode):
		
		if mode in self.configuration.ORBIT_CONTROL_SETTINGS.keys():
			
			settings = self.configuration.ORBIT_CONTROL_SETTINGS[mode]
			
			self.horizontalSliderOrbitThrottle.setSliderPosition(settings['throttle'])
			self.horizontalSliderOrbitYaw.setSliderPosition(settings['yaw'])
			self.horizontalSliderOrbitPitch.setSliderPosition(settings['pitch'])
	
	
	##################################################################
	
	def enableHelicopterHover(self):
		
		if not self.pushButtonHelicopterHover.isChecked():
			self.pushButtonHelicopterHover.setChecked(True)
		
		if self.pushButtonHelicopterForward.isChecked():
			self.pushButtonHelicopterForward.setChecked(False)
			self.disableHelicopterForward()
		
		if self.pushButtonHelicopterSpinLeft.isChecked():
			self.pushButtonHelicopterSpinLeft.setChecked(False)
			self.disableHelicopterSpinLeft()
			
		if self.pushButtonHelicopterSpinRight.isChecked():
			self.pushButtonHelicopterSpinRight.setChecked(False)
			self.disableHelicopterSpinRight()
		
		
		self.setFlightPlan('hover')
		
		
		self.disconnect(self.pushButtonHelicopterHover, \
		                QtCore.SIGNAL("clicked()"), \
		                self.enableHelicopterHover)
		
		self.connect(self.pushButtonHelicopterHover, \
		             QtCore.SIGNAL("clicked()"), \
		             self.disableHelicopterHover)
	
	
	##################################################################
	
	def disableHelicopterHover(self):
		
		if self.pushButtonHelicopterHover.isChecked():
			self.pushButtonHelicopterHover.setChecked(False)
		
		self.disconnect(self.pushButtonHelicopterHover, \
		                QtCore.SIGNAL("clicked()"), \
		                self.disableHelicopterHover)
		
		self.connect(self.pushButtonHelicopterHover, \
		             QtCore.SIGNAL("clicked()"), \
		             self.enableHelicopterHover)
	
	
	##################################################################
	
	def enableHelicopterForward(self):
		
		if not self.pushButtonHelicopterForward.isChecked():
			self.pushButtonHelicopterForward.setChecked(True)
		
		if self.pushButtonHelicopterHover.isChecked():
			self.pushButtonHelicopterHover.setChecked(False)
			self.disableHelicopterHover()
		
		if self.pushButtonHelicopterSpinLeft.isChecked():
			self.pushButtonHelicopterSpinLeft.setChecked(False)
			self.disableHelicopterSpinLeft()
			
		if self.pushButtonHelicopterSpinRight.isChecked():
			self.pushButtonHelicopterSpinRight.setChecked(False)
			self.disableHelicopterSpinRight()
		
		
		self.setFlightPlan('forward')
		
		
		self.disconnect(self.pushButtonHelicopterForward, \
		                QtCore.SIGNAL("clicked()"), \
		                self.enableHelicopterForward)
		
		self.connect(self.pushButtonHelicopterForward, \
		             QtCore.SIGNAL("clicked()"), \
		             self.disableHelicopterForward)
	
	
	##################################################################
	
	def disableHelicopterForward(self):
		
		if self.pushButtonHelicopterForward.isChecked():
			self.pushButtonHelicopterForward.setChecked(False)
		
		self.disconnect(self.pushButtonHelicopterForward, \
		                QtCore.SIGNAL("clicked()"), \
		                self.disableHelicopterForward)
		
		self.connect(self.pushButtonHelicopterForward, \
		             QtCore.SIGNAL("clicked()"), \
		             self.enableHelicopterForward)
	
	
	##################################################################
	
	def enableHelicopterSpinLeft(self):
		
		if not self.pushButtonHelicopterSpinLeft.isChecked():
			self.pushButtonHelicopterSpinLeft.setChecked(True)
		
		if self.pushButtonHelicopterHover.isChecked():
			self.pushButtonHelicopterHover.setChecked(False)
			self.disableHelicopterHover()
		
		if self.pushButtonHelicopterForward.isChecked():
			self.pushButtonHelicopterForward.setChecked(False)
			self.disableHelicopterForward()
			
		if self.pushButtonHelicopterSpinRight.isChecked():
			self.pushButtonHelicopterSpinRight.setChecked(False)
			self.disableHelicopterSpinRight()
		
		
		self.setFlightPlan('spinleft')
		
		
		self.disconnect(self.pushButtonHelicopterSpinLeft, \
		                QtCore.SIGNAL("clicked()"), \
		                self.enableHelicopterSpinLeft)
		
		self.connect(self.pushButtonHelicopterSpinLeft, \
		             QtCore.SIGNAL("clicked()"), \
		             self.disableHelicopterSpinLeft)
	
	
	##################################################################
	
	def disableHelicopterSpinLeft(self):
		
		if self.pushButtonHelicopterSpinLeft.isChecked():
			self.pushButtonHelicopterSpinLeft.setChecked(False)
		
		self.disconnect(self.pushButtonHelicopterSpinLeft, \
		                QtCore.SIGNAL("clicked()"), \
		                self.disableHelicopterSpinLeft)
		
		self.connect(self.pushButtonHelicopterSpinLeft, \
		             QtCore.SIGNAL("clicked()"), \
		             self.enableHelicopterSpinLeft)
	
	
	##################################################################
	
	def enableHelicopterSpinRight(self):
		
		if not self.pushButtonHelicopterSpinRight.isChecked():
			self.pushButtonHelicopterSpinRight.setChecked(True)
		
		if self.pushButtonHelicopterHover.isChecked():
			self.pushButtonHelicopterHover.setChecked(False)
			self.disableHelicopterHover()
		
		if self.pushButtonHelicopterForward.isChecked():
			self.pushButtonHelicopterForward.setChecked(False)
			self.disableHelicopterForward()
			
		if self.pushButtonHelicopterSpinLeft.isChecked():
			self.pushButtonHelicopterSpinLeft.setChecked(False)
			self.disableHelicopterSpinLeft()
		
		
		self.setFlightPlan('spinright')
		
		
		self.disconnect(self.pushButtonHelicopterSpinRight, \
		                QtCore.SIGNAL("clicked()"), \
		                self.enableHelicopterSpinRight)
		
		self.connect(self.pushButtonHelicopterSpinRight, \
		             QtCore.SIGNAL("clicked()"), \
		             self.disableHelicopterSpinRight)
	
	
	##################################################################
	
	def disableHelicopterSpinRight(self):
		
		if self.pushButtonHelicopterSpinRight.isChecked():
			self.pushButtonHelicopterSpinRight.setChecked(False)
		
		self.disconnect(self.pushButtonHelicopterSpinRight, \
		                QtCore.SIGNAL("clicked()"), \
		                self.disableHelicopterSpinRight)
		
		self.connect(self.pushButtonHelicopterSpinRight, \
		             QtCore.SIGNAL("clicked()"), \
		             self.enableHelicopterSpinRight)
	
	
	##################################################################
	
	def helicopterLand(self):
		
		self.horizontalSliderOrbitConcentration.setSliderPosition(0)
		self.updateSliderConcentration()
		self.triggerActions(power=0)
	
	
	##################################################################
	
	def helicopterTestFly(self):
		
		self.triggerActions(power=100)
	
	
	##################################################################
	
	def stop(self):
		
		self.triggerActions(power=0)
		
		self.disconnectInfraredDevice()


#####################################################################
# Functions
#####################################################################

#####################################################################
# Main
#####################################################################

#if __name__ == '__main__':
	
	#pass

