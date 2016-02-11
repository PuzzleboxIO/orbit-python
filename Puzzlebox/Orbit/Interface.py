#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Puzzlebox - Orbit - Interface
#
# Copyright Puzzlebox Productions, LLC (2011-2014)

__changelog__ = """\
Last Update: 2014.02.23
"""

__todo__ = """
"""

import os, sys, time
import urllib


import Puzzlebox.Orbit.Configuration as configuration

if configuration.ENABLE_PYSIDE:
	try:
		#import PySide as PyQt4
		from PySide import QtCore, QtGui, QtNetwork
	except Exception, e:
		print "ERROR: Exception importing PySide:",
		print e
		configuration.ENABLE_PYSIDE = False
	else:
		print "INFO: [Orbit:Interface] Using PySide module"

if not configuration.ENABLE_PYSIDE:
	print "INFO: [Orbit:Interface] Using PyQt4 module"
	from PyQt4 import QtCore, QtGui, QtNetwork


if (sys.platform == 'win32'):
	DEFAULT_IMAGE_PATH = 'images'
	import _winreg as winreg
	import itertools
	import re
	import serial
elif (sys.platform == 'darwin'):
	DEFAULT_IMAGE_PATH = 'images'
else:
	DEFAULT_IMAGE_PATH = '/usr/share/puzzlebox_orbit/images'
	import bluetooth


from Puzzlebox.Jigsaw.Design_Interface import Ui_Form as Design

import simplejson as json

import Puzzlebox.Jigsaw.Interface as jigsaw_interface

##import puzzlebox_logger
import Puzzlebox.Jigsaw.Plugin_Help as Plugin_Help
if configuration.ENABLE_PLUGIN_SESSION:
	import Puzzlebox.Jigsaw.Plugin_Session as Plugin_Session
if configuration.ENABLE_PLUGIN_EEG:
	import Puzzlebox.Jigsaw.Plugin_Eeg as Plugin_Eeg
if configuration.ENABLE_PLUGIN_ORBIT:
	import Puzzlebox.Orbit.Plugin_Orbit as Plugin_Orbit


#####################################################################
# Globals
#####################################################################

DEBUG = 1

#####################################################################
# Classes
#####################################################################

class puzzlebox_orbit_interface(jigsaw_interface.puzzlebox_jigsaw_interface):
	
	def __init__(self, log, server=None, DEBUG=DEBUG, parent=None):
		
		self.log = log
		self.DEBUG = DEBUG
		
		QtGui.QWidget.__init__(self, parent)
		self.setupUi(self)
		self.icon = None
		
		self.configuration = configuration
		
		self.configureSettings()
		self.connectWidgets()
		
		self.name = "Orbit:Interface"
		
		self.activePlugins = []
		self.configurePlugins()
		
		self.customDataHeaders = []


	##################################################################
	
	def closeEvent(self, event):
		
		quit_message = "Are you sure you want to exit the program?"
		
		reply = QtGui.QMessageBox.question( \
		           self, \
		          'Quit Puzzlebox Orbit', \
		           quit_message, \
		           QtGui.QMessageBox.Yes, \
		           QtGui.QMessageBox.No)
		
		if reply == QtGui.QMessageBox.Yes:
			
			self.stop()
			
			event.accept()
		
		else:
			event.ignore()


#####################################################################
# Functions
#####################################################################

#####################################################################
# Main
#####################################################################

if __name__ == '__main__':
	
	#log = puzzlebox_logger.puzzlebox_logger(logfile='client_interface')
	log = None
	
	app = QtGui.QApplication(sys.argv)
	
	window = puzzlebox_orbit_interface(log, DEBUG)
	window.show()
	
	sys.exit(app.exec_())

