#!/usr/bin/python
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855
import Adafruit_CharLCD as LCD
import MySQLdb
import os
import socket

lcd = LCD.Adafruit_CharLCDPlate()
db = MySQLdb.connect("localhost","nate","kootek","temperature")
cursor=db.cursor()

CLK = 25
CS  = 24
DO  = 18
sensor = MAX31855.MAX31855(CLK, CS, DO)


count = 0
count2 = 0
times = 10
product = 0
sets = 0
lcd.clear()
lcd.message("  Raspberry pi\n  Thermometer")
time.sleep(2)
lcd.clear()	
mL = ["Filet","Nuggets","Spicy"]
sL = ["Shutdown","Restart","IP address","Current\n      Temp"]
		
# Function to display currently selected product
def currentProduct(x):
	global product
	if x == 0:
		product = mL[0]
	elif x == 1:
		product = mL[1]
	elif x == 2:
		product = mL[2]
	elif x > 2:
		currentProduct(0)
		loopM(0) 
	elif x < 0:
		currentProduct(2)
		loopM(2)	
	lcd.message("   < " + product + " >")
	time.sleep(0.1)
	lcd.clear()
	
def	settings(y):
	if y == 0:
		sets = sL[0]
		if lcd.is_pressed(LCD.SELECT):
			lcd.message("Shutting down...")
			time.sleep(3)
			lcd.clear()
			lcd.set_color(0, 0, 0)
			os.system("shutdown -h now")		
	elif y == 1:
		sets = sL[1]
		if lcd.is_pressed(LCD.SELECT):
			lcd.message("Restarting.........")
			os.system("shutdown -r now")
	elif y == 2:
		sets = sL[2]
		if lcd.is_pressed(LCD.SELECT):
			try:
				lcd.message("My IP address is :\n" + str([(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]))
				time.sleep(5)
				lcd.clear()
				settings(y)
			except:
				lcd.message("Unable to locate\nIP address")
				time.sleep(5)
				lcd.clear()
				settings(y)
	elif y == 3:
		sets = sL[3]
		if lcd.is_pressed(LCD.SELECT):
			def displayCurrentTemp():
				lcd.message("Press UP\nTo Exit...")
				time.sleep(3)
				lcd.clear()
				while True:
					tempC = sensor.readTempC()
					tempF = c_to_f(tempC)
					lcd.message(str(tempF) + "F")
					time.sleep(0.1)
					lcd.clear()
					if lcd.is_pressed(LCD.UP):
						time.sleep(0.5)
						settings(0)
						loopS(0)
			displayCurrentTemp()
	elif y > 3:
		settings(0)
		loopS(0)
	elif y < 0:
		settings(3)
		loopS(3)
	lcd.message("    "+sets)
	time.sleep(0.1)
	lcd.clear()
		
		
def loopM(c):
	while True:
		if lcd.is_pressed(LCD.RIGHT):
			c = c + 1
		elif lcd.is_pressed(LCD.LEFT):
			c = c - 1
		elif lcd.is_pressed(LCD.UP):
			loopS(0)
		elif lcd.is_pressed(LCD.DOWN):
			loopS(0)
		elif lcd.is_pressed(LCD.SELECT):
			lcd.clear()
			tempCheck(times)
			
		currentProduct(c)

def loopS(b):
	while True:
		if lcd.is_pressed(LCD.UP):
			b = b + 1
		elif lcd.is_pressed(LCD.DOWN):
			b = b - 1
		elif lcd.is_pressed(LCD.RIGHT):
			loopM(0)
		elif lcd.is_pressed(LCD.LEFT):
			loopM(0)
		settings(b)
	
def c_to_f(c):
	return c * 9.0 / 5.0 + 32
def tempCheck(t):					
	tempc = sensor.readTempC()
	tempf = c_to_f(tempc)
	date = time.strftime("%m-%d-%Y")
	timeClock = time.strftime("%I:%M:%S %p")
	lcd.message(str(tempf) + "F\nPlease Wait " + str(t))
	#Starts count down to allow product to reach maximum temperature
	while (t > 0):	
		t = t - 1
		time.sleep(1)
		lcd.clear()
		tempCheck(t)
	#Checks if product is at correct temperature of 140	
	# if product == mL[0] or mL[1] or mL[2]:
		# if tempf < 140:
			# lcd.clear()
			
			# lcd.set_color(0, 0, 0)
			# while True:
				# lcd.set_color(1, 1, 1)
				# lcd.message("   *Discard*\n   *Product*")
				# time.sleep(0.5)
				# lcd.clear()
				# lcd.set_color(0, 0, 0)
				# time.sleep(0.5)
				# lcd.set_color(1, 1, 1)
				# lcd.message("    *"+str(tempf)+"F*")
				# time.sleep(0.5)
				# lcd.clear()
				# lcd.set_color(0, 0, 0)
				# time.sleep(0.5)
				# if lcd.is_pressed(LCD.SELECT):
					# lcd.clear()
					# lcd.set_color(1, 1, 1)
					# time.sleep(1)
					# currentProduct(0)
					# loopM(0)
					
			
	try:
		cursor.execute("INSERT INTO temperaturedata (Date,Time,Product,Temperature) VALUES (%s,%s,%s,%s)", (date,timeClock,product,tempf))
		db.commit()
		lcd.clear()
		lcd.message(str(tempf) + "\n" + "Success")
		time.sleep(3)
	except:
		lcd.message("Fail")
		time.sleep(3)
	times = 0
	lcd.clear()
	loopM(0)

	
loopM(count)