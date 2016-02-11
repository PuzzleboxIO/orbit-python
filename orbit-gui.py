#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Puzzlebox - Orbit - Interface - GUI
#
# Copyright Puzzlebox Productions, LLC (2013-2014)

__changelog__ = """\
Last Update: 2014.02.23
"""

__doc__ = """|
Linux Examples:
#hcitool scan # Find devices
#sdptool search sp D0:DF:9A:69:5D:42 # Examine serial services on device
#hciconfig hci0 sspmode 0 # ignore this step as device seems to work with sspmode enabled
rfcomm bind rfcomm0 D0:DF:9A:69:5D:42 1 # bind /dev/rfcomm0 to channel 1 on device
rfcomm release D0:DF:9A:69:5D:42 # disconnect device
"""

import os, sys
import signal

if ('_MEIPASS2' in os.environ.keys()):
	sys.path.insert(0, os.environ['_MEIPASS2'])
	os.chdir(os.environ['_MEIPASS2'])

if (sys.platform == 'darwin'):
	pass

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
		print "INFO: [Orbit:orbit-gui] Using PySide module"

if not configuration.ENABLE_PYSIDE:
	print "INFO: [Orbit:orbit-gui] Using PyQt4 module"
	from PyQt4 import QtCore, QtGui, QtNetwork


import Puzzlebox.Orbit.Interface as interface
#import puzzlebox_logger


#####################################################################
# Globals
#####################################################################

DEBUG = 1

#####################################################################
# Classes
#####################################################################

#####################################################################
# Functions
#####################################################################

#####################################################################
# Main
#####################################################################

if __name__ == '__main__':
	
	# Perform correct KeyboardInterrupt handling
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	
	#log = puzzlebox_logger.puzzlebox_logger(logfile='client_interface')
	log = None
	
	# Collect default settings and command line parameters
	#server_interface = SERVER_INTERFACE
	#server_host = SERVER_HOST
	#server_port = SERVER_PORT
	
	for each in sys.argv:
		
		if each.startswith("--interface="):
			server_interface = each[ len("--interface="): ]
		if each.startswith("--host="):
			server_host = each[ len("--host="): ]
		if each.startswith("--port="):
			server_port = each[ len("--port="): ]
	
	app = QtGui.QApplication(sys.argv)
	
	QtGui.QApplication.setApplicationName('puzzlebox-orbit')
	
	window = interface.puzzlebox_orbit_interface(log, \
	                                             #server=server, \
	                                              DEBUG=DEBUG)
	
	window.show()
	
	sys.exit(app.exec_())

