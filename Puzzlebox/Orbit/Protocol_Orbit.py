#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Puzzlebox - Jigsaw - Protocol - Orbit
#
# Copyright Puzzlebox Productions, LLC (2013-2014)

__changelog__ = """\
Last Update: 2014.02.23
"""

__todo__ = """
"""

import string, time
import serial

import Configuration as configuration

if configuration.ENABLE_PYSIDE:
	try:
		import PySide as PyQt4
		from PySide import QtCore
	except Exception, e:
		print "ERROR: Exception importing PySide:",
		print e
		configuration.ENABLE_PYSIDE = False
	else:
		print "INFO: [Protocol:Orbit] Using PySide module"

if not configuration.ENABLE_PYSIDE:
	print "INFO: [Protocol:Orbit] Using PyQt4 module"
	from PyQt4 import QtCore

import Puzzlebox.Jigsaw.Configuration as configuration
#import puzzlebox_logger


#####################################################################
# Globals
#####################################################################

DEBUG = 1

DEFAULT_COMMAND = 'neutral'
DEFAULT_SERIAL_DEVICE = '/dev/ttyACM0'

DEFAULT_MODE = "pyramid"

DEFAULT_ARDUINO_BAUD_RATE = 9600
DEFAULT_PYRAMID_BAUD_RATE = 115200
DEFAULT_BLOOM_BAUD_RATE = 57600

ARDUINO_INITIALIZATION_TIME = 2
#ARDUINO_INITIALIZATION_TIME = 12

#THROTTLE_POWER_MODIFIER = 0.25
#STEERING_POWER_MODIFIER = 0.75

LOOP_TIMER = 80 # 80 ms

FLIGHT_COMMANDS = ['O', 'P']


#####################################################################
# Classes
#####################################################################

class puzzlebox_jigsaw_protocol_orbit(QtCore.QThread):
	
	def __init__(self, log, \
	             serial_port=DEFAULT_SERIAL_DEVICE, \
	             mode=DEFAULT_MODE, \
	             command=DEFAULT_COMMAND, \
	             DEBUG=DEBUG, parent=None):
		
		QtCore.QThread.__init__(self,parent)
		
		self.log = log
		self.DEBUG = DEBUG
		self.parent = parent
		self.serial_port = serial_port
		self.mode = mode
		
		self.command = command
		self.last_flight_command = None
		self.last_color_command = None
		self.last_throttle = None
		self.last_yaw = None
		self.last_pitch = None
		
		self.device = None
		
		self.configuration = configuration
		
		self.name = "Jigsaw-Protocol-Orbit"
		
		self.command_queue = []
		
		
		self.bloomServoPercentage = 0
		self.bloomColorRed = 0
		self.bloomColorBlue = 0
		self.bloomColorGreen = 0
		
		
		try:
			self.initializeSerial()
		except Exception, e:
			if self.DEBUG:
				print "<-- [Protocol:Orbit] Connection failed to Orbit control device [%s]" % self.device
				print "ERROR [Protocol:Orbit]:",
				print e
		
		self.connection = self.device
		
		
		self.keep_running = True
	
	
	##################################################################
	
	def initializeSerial(self):
		
		if self.mode == 'pyramid':
			baudrate = DEFAULT_PYRAMID_BAUD_RATE
			rts_cts_flow_control = 'f'
		elif self.mode == 'bloom':
			baudrate = DEFAULT_BLOOM_BAUD_RATE
			rts_cts_flow_control = 'f'
		else:
			baudrate = DEFAULT_ARDUINO_BAUD_RATE
			rts_cts_flow_control = 't'
			
		if self.DEBUG:
			print "INFO [Protocol:Orbit]: Serial device:",
			print self.serial_port
			print "INFO [Protocol:Orbit]: Connecting at baud rate",
			print baudrate
			
		bytesize = 8
		parity = 'NONE'
		stopbits = 1
		software_flow_control = 'f'
		#timeout = 15
		timeout = 5
		
		# convert bytesize
		if (bytesize == 5):
			init_byte_size = serial.FIVEBITS
		elif (bytesize == 6):
			init_byte_size = serial.SIXBITS
		elif (bytesize == 7):
			init_byte_size = serial.SEVENBITS
		elif (bytesize == 8):
			init_byte_size = serial.EIGHTBITS
		else:
			#self.log.perror("Invalid value for %s modem byte size! Using default (8)" % modem_type)
			init_byte_size = serial.EIGHTBITS
		
		# convert parity
		if (parity == 'NONE'):
			init_parity = serial.PARITY_NONE
		elif (parity == 'EVEN'):
			init_parity = serial.PARITY_EVEN
		elif (parity == 'ODD'):
			init_parity = serial.PARITY_ODD
		else:
			#self.log.perror("Invalid value for %s modem parity! Using default (NONE)" % modem_type)
			init_parity = serial.PARITY_NONE
		
		# convert stopbits
		if (stopbits == 1):
			init_stopbits = serial.STOPBITS_ONE
		elif (stopbits == 2):
			init_stopbits = serial.STOPBITS_TWO
		else:
			#self.log.perror("Invalid value for %s modem stopbits! Using default (8)" % modem_type)
			init_byte_size = serial.STOPBITS_ONE
		
		# convert software flow control
		if (software_flow_control == 't'):
			init_software_flow_control = 1
		else:
			init_software_flow_control = 0
		
		# convert rts cts flow control
		if (rts_cts_flow_control == 't'):
			init_rts_cts_flow_control = 1
		else:
			init_rts_cts_flow_control = 0
		
		self.device = serial.Serial(port = self.serial_port, \
		                            baudrate = baudrate, \
		                            bytesize = init_byte_size, \
		                            parity = init_parity, \
		                            stopbits = init_stopbits, \
		                            xonxoff = init_software_flow_control, \
		                            rtscts = init_rts_cts_flow_control, \
		                            timeout = timeout)
		
		
		if self.mode != 'bloom':
			self.land()
		
		time.sleep(ARDUINO_INITIALIZATION_TIME)
	
	
	##################################################################
	
	def get_status(self, connection):
		
		status = 'Connected'
		
		return(status)
	
	
	##################################################################
	
	def hover(self):
		
		"Set throttle to hover"
		
		# Issue command
		if self.DEBUG:
			print '--> [Protocol:Orbit] Hover ("P")'
		
		#self.device.write("P")
		#self.command_queue.append(command)
		self.command_queue.append("P")
	
	
	##################################################################
	
	def land(self):
		
		"Set throttle to zero"
		
		# Issue command
		if self.DEBUG:
			print '--> [Protocol:Orbit] Land ("O")'
		
		self.command_queue.append("O")
		#self.device.write("O")
	
	
	##################################################################
	
	def padValue(self, value):
		
		while len(value) < 3:
			value = '0%s' % value
		
		return value
	
	
	##################################################################
	
	def setThrottle(self, throttle):
		
		value = self.padValue( str(throttle) )
		
		command = 't%s' % value
		
		if (command == self.last_throttle):
			if self.DEBUG > 1:
				print "Skipping sending of duplicate throttle command:",
				print command
			return
		else:
			self.last_throttle = command
		
		if self.DEBUG:
			print "--> [Protocol:Orbit] Sending Orbit Command:",
			print command
		
		#self.device.write(command)
		self.command_queue.append(command)
	
	
	##################################################################
	
	def setYaw(self, yaw):
		
		value = self.padValue( str(yaw) )
		
		command = 'y%s' % value
		
		if (command == self.last_yaw):
			if self.DEBUG > 1:
				print "Skipping sending of duplicate yaw command:",
				print command
			return
		else:
			self.last_yaw = command
		
		if self.DEBUG:
			print "--> [Protocol:Orbit] Sending Orbit Command:",
			print command
		
		#self.device.write(command)
		self.command_queue.append(command)
	
	
	##################################################################
	
	def setPitch(self, pitch):
		
		value = self.padValue( str(pitch) )
		
		command = 'p%s' % value
		
		if (command == self.last_pitch):
			if self.DEBUG > 1:
				print "Skipping sending of duplicate pitch command:",
				print command
			return
		else:
			self.last_pitch = command
		
		
		if self.DEBUG:
			print "--> [Protocol:Orbit] Sending Orbit Command:",
			print command
		
		#self.device.write(command)
		self.command_queue.append(command)
	
	
	##################################################################
	
	def sendCommand(self, command, power=None):
		
		if self.DEBUG:
			print "INFO: [Protocol:Orbit] Sending Orbit Command:",
			print command
		
		self.command_queue.append(command)
	
	
	##################################################################
	
	def convertColorToString(self, color):
		
		if len("%s" % color) == 1:
			output = "00%i" % color
		elif len("%s" % color) == 2:
			output = "0%i" % color
		elif len("%s" % color) == 3:
			output = "%i" % color
		else:
			output = "%i" % color
			output = output[:3]
		
		
		return(output)
	
	
	##################################################################
	
	def setColorWheel(self, red, green, blue):
		
		red = self.convertColorToString(red)
		green = self.convertColorToString(green)
		blue = self.convertColorToString(blue)
		
		command = "w%s%s%s" % (red, green, blue)
		
		if (command == self.last_color_command):
			if self.DEBUG > 1:
				print "Skipping sending of duplicate color wheel command:",
				print command
			return
		else:
			self.last_color_command = command
		
		if self.DEBUG:
			print "INFO: [Protocol:Orbit] Sending Orbit Command:",
			print command
		
		self.command_queue.append(command)
		#self.device.write(command)
	
	
	##################################################################
	
	def setColor(self, position, red, green, blue):
		
		position = position - 1 # convert from counting number
		
		if len("%s" % position) == 1:
			position = "0%s" % position
		else:
			position = "%s" % position
		
		red = convertColorToString(red)
		green = convertColorToString(green)
		blue = convertColorToString(blue)
		
		command = "c%s%s%s%s" % (position, red, green, blue)
		
		if self.DEBUG:
			print "INFO: [Protocol:Orbit] Sending Orbit Command:",
			print command
		
		self.command_queue.append(command)
		#self.device.write(command)
	
	
	##################################################################
	
	def updateBloomServoPercentage(self, eegPower):
		
		if (eegPower > 0):
			#self.bloomServoPercentage = self.bloomServoPercentage + 3
			self.bloomServoPercentage = self.bloomServoPercentage + self.configuration.BLOOM_SERVO_STEP_POSITIVE
		else:
			#self.bloomServoPercentage = self.bloomServoPercentage - 1
			self.bloomServoPercentage = self.bloomServoPercentage - self.configuration.BLOOM_SERVO_STEP_NEGATIVE
		
		if (self.bloomServoPercentage > 100):
			self.bloomServoPercentage = 100
		
		if (self.bloomServoPercentage < 0):
			self.bloomServoPercentage = 0
		
	
	##################################################################
	
	def updateBloomRGB(self, eegPower, concentration, relaxation):
		
		#sendRed = False
		#sendBlue = False

		#attentionSeekValue = seekBarAttention.getProgress();
		#meditationSeekValue = seekBarMeditation.getProgress();

		if (eegPower > 0):

			if (concentration > 0):
				#self.bloomColorRed = self.bloomColorRed + 8
				self.bloomColorRed = self.bloomColorRed + 8
			else:
				#self.bloomColorRed = self.bloomColorRed - 6
				self.bloomColorRed = self.bloomColorRed - 6
				#sendRed = True
			
			if (relaxation > 0):
				self.bloomColorBlue = self.bloomColorBlue + 8
			else:
				self.bloomColorBlue = self.bloomColorBlue - 6
				#sendBlue = True
			

		else:

			#if (concentration > 0):
			self.bloomColorRed = self.bloomColorRed - 6
				#sendRed = True
			
			#if (relaxation > 0):
			self.bloomColorBlue = self.bloomColorBlue - 6
				#sendBlue = True
			

		
		if (self.bloomColorRed > 255):
			self.bloomColorRed = 255
		if (self.bloomColorBlue > 255):
			self.bloomColorBlue = 255
		if (self.bloomColorGreen > 255):
			self.bloomColorGreen = 255

		if (self.bloomColorRed < 0):
			self.bloomColorRed = 0
		if (self.bloomColorBlue < 0):
			self.bloomColorBlue = 0
		if (self.bloomColorGreen < 0):
			self.bloomColorGreen = 0


		red = self.padValue( str( int(self.bloomColorRed)) )
		green = self.padValue( str( int(self.bloomColorGreen)) )
		blue = self.padValue( str( int(self.bloomColorBlue)) )
		
		command = 'R%s%s%s' % (red, green, blue)
			
			
		#if (sendRed) or (sendBlue):
			
		if self.DEBUG:
			print "--> [Protocol:Orbit] Sending Bloom Command:",
			print command
		
		self.command_queue.append(command)
	
	
	##################################################################
	
	def updateBloom(self, eegPower, concentration, relaxation):
		
		
		self.updateBloomServoPercentage(eegPower)
		self.updateBloomRGB(eegPower, concentration, relaxation)
		
		
		value = self.padValue( str( int(self.bloomServoPercentage) ) )
		
		command = 'S%s' % value
		
		if self.DEBUG:
			print "--> [Protocol:Orbit] Sending Bloom Command:",
			print command
		
		self.command_queue.append(command)
	
	
	##################################################################
	
	def processCommand(self, command):
		
		if (command == 'hover'):
			self.hover()
		
		elif (command == 'land'):
			self.land()
		
		else:
			
			#if (command in FLIGHT_COMMANDS):
				
				#if (command == self.last_flight_command):
					#if self.DEBUG:
						#print "Skipping sending of duplicate flight command:",
						#print command
						#return
				#else:
					#self.last_flight_command = command
			
			
			#if (command.startswith('w')):
				
				#if (command == self.last_color_command):
					#if self.DEBUG:
						#print "Skipping sending of duplicate Pyramid color command:",
						#print command
						#return
				#else:
					#self.last_color_command = command
			
			
			self.device.write(command)
	
	
	##################################################################
	
	def run(self):
		
		while self.keep_running:
			
			#if self.command_queue != []:
			while self.command_queue != []:
				
				command = self.command_queue[0]
				self.command_queue = self.command_queue[1:]
				
				try:
					self.processCommand(command)
					pass
				except Exception, e:
					print "ERROR: [Protocol:Orbit] Exception sending Orbit commands:",
					print e
			
			
			# Sleep 80 ms
			QtCore.QThread.msleep(LOOP_TIMER)
	
	
	##################################################################
	
	def stop(self):
		
		self.land()
		
		self.keep_running = False
		
		self.command_queue = []
		
		try:
			self.device.close()
		except Exception, e:
			if self.DEBUG:
				print "ERROR: [Protocol:Orbit] failed to close device in stop():",
				print e
	
	
	##################################################################
	
	def exitThread(self, callThreadQuit=True):
		
		self.stop()
		
		if callThreadQuit:
			try:
				QtCore.QThread.quit(self)
			except Exception, e:
				if self.DEBUG:
					print "ERROR: [Protocol:Orbit] failed to call QtCore.QThread.quit(self) in exitThread():",
					print e


#####################################################################
# Functions
#####################################################################

#####################################################################
# Main
#####################################################################

if __name__ == '__main__':
	
	# Perform correct KeyboardInterrupt handling
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	
	# Collect default settings and command line parameters
	device = DEFAULT_SERIAL_DEVICE
	mode = DEFAULT_MODE
	command = DEFAULT_COMMAND
	
	for each in sys.argv:
		
		if each.startswith("--device="):
			device = each[ len("--device="): ]
		elif each.startswith("--mode="):
			mode = each[ len("--mode="): ]
		elif each.startswith("--command="):
			command = each[ len("--command="): ]
	
	
	app = QtCore.QCoreApplication(sys.argv)
	
	orbit = puzzlebox_jigsaw_protocol_orbit( \
	                None, \
	                serial_port=device, \
	                mode=mode, \
	                command=command, \
	                DEBUG=DEBUG)
	
	orbit.start()
	
	sys.exit(app.exec_())

