#!/usr/bin/python
# -*- coding:utf-8 -*-

import RPi.GPIO as GPIO
#import cffi
import time
from smbus import SMBus
from tkinter import *
from tkinter import ttk
from threading import *
#import spidev
#import re
import sys
import select
import tty
import termios
import configparser

#REGISTER VALUES

REG_CON0 = 0xC7 #config register 0 (pins 0-7)
REG_CON1 = 0xBF #config register 1 (pins 10-17)
REG_POL0 = 0x10 #polarity inversion register 0
REG_POL1 = 0x80 #polarity inversion register 1

#COMMAND BYTE VALUES
CMD_INP0 = 0x00 #Input 0
CMD_INP1 = 0x01 #Input 1
CMD_OUT0 = 0x02 #Output 0
CMD_OUT1 = 0x03 #Output 1
CMD_POL0 = 0x04 #Polarity 0
CMD_POL1 = 0x05 #Polarity 1
CMD_CON0 = 0x06 #Config 0
CMD_CON1 = 0x07 #Config 1

#Output Pin Bits
PIN_RVCtrl = 0x08 #P03
PIN_nSleep = 0x10 #P04
PIN_ENABLE = 0x20 #P05
PIN_ADCRST = 0x40 #P16

#I2C address format is b00100[A2][A1][A0] (Address pins are tied to GND on circuit)
ADDRESS= 0x20

#CONSTANTS
channel = 1
RHC_PIN = 37 #Refrigerant Heater Control
AHC_PIN = 35 #Air Heater Control

#GLOBAL VARIABLES
valInpReg = []
valOutReg = [] #desired value of the output register, not necessarily actual value
valPolReg = [REG_POL0,REG_POL1]
valConReg = [REG_CON0,REG_CON1]

InputPins = {"Fan Current Fault 1": bool,
            "Fan Current Fault 2": bool,
            "Fan Voltage Monitor": bool,
            "Air Heater Voltage Fault": bool,
            "Air Heater Current Fault 1": bool,
            "Air Heater Current Fault 2": bool,
            "Refrigerant Heater Voltage Fault": bool,
            "Refrigerant Heater Current Fault 1": bool,
            "Refrigerant Heater Current Fault 2": bool,
            "nFAULT": bool}

OutputPins = {"RVCtrl": PIN_RVCtrl,
              "nSleep": PIN_nSleep,
              "ENABLE": PIN_ENABLE,
              "ADCRST": PIN_ADCRST}




        

#**FUNCTION DEFINITIONS**

def isData(): #keypress-function to know if there is input available
  return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []) #keypress

def GPIOsetup():
    GPIO.setwarnings(False) #DEBUG 
    GPIO.setmode(GPIO.BOARD) #use the board pin numbering
    GPIO.setup(RHC_PIN, GPIO.OUT) #Refrigerant Heater Control
    GPIO.setup(AHC_PIN, GPIO.OUT) #Air Heater Control

def ReadReg(bus, address, command):
    readData = bus.read_byte_data(address, command)
    return readData

def ReadRegPair(bus, address, command):
    readData = bus.read_i2c_block_data(address, command, 2)
    return readData

def WriteReg(bus, address, command, data):
    writeData = bus.write_byte_data(address, command, data)
    return writeData

def WriteRegPair(bus, address, command, data0, data1):
    data = [data0, data1]
    bus.write_i2c_block_data(address, command, data)
    return data

def threading():
    #Call readInputs function
    t1=Thread(target=readInputs)
    t1.start()

def readInputs():
    noError = True
    while(noError):
    
        try:
            #Read both input registers (TODO add delay buffer for i2c bus to execute?) (TODO check needed baudrate?)
            valInpReg = ReadRegPair(i2cbus, ADDRESS, CMD_INP0)
            #TODO store expected output register value and confirm
            
        except:
            valInpReg = [0xFF,0xFF]
            noError = False
            print("Exception: read input registers failed in PCA9535 module\n")
            
        #Print status (or refresh status display?
        InputPins["Fan Current Fault 1"] = "HIGH" if (valInpReg[0] & 0x02) else "LOW"
        InputPins["Fan Current Fault 2"] = "HIGH" if (valInpReg[0] & 0x01) else "LOW"
        InputPins["Fan Voltage Monitor"] = "HIGH" if (valInpReg[0] & 0x04) else "LOW"

        InputPins["Air Heater Voltage Fault"] = "HIGH" if (valInpReg[1] & 0x01) else "LOW"
        InputPins["Air Heater Current Fault 1"] = "HIGH" if (valInpReg[1] & 0x02) else "LOW"
        InputPins["Air Heater Current Fault 2"] = "HIGH" if (valInpReg[1] & 0x04) else "LOW"
        InputPins["Refrigerant Heater Voltage Fault"] = "HIGH" if (valInpReg[1] & 0x08) else "LOW"
        InputPins["Refrigerant Heater Current Fault 1"] = "HIGH" if (valInpReg[1] & 0x10) else "LOW"
        InputPins["Refrigerant Heater Current Fault 2"] = "HIGH" if (valInpReg[1] & 0x20) else "LOW"
        InputPins["nFAULT"] = "HIGH" if (valInpReg[1] & 0x80) else "LOW"
        
        for pin in InputPins:
            print(pin) #DEBUG Does this only print

def writeOutputs(state,pinOption):
    try:
        if pinOption == "RVCtrl":
            if (state == "LOW"): valOutReg[0] = valOutReg[0] & PIN_RVCtrl  #set RVCtrl bit to 0 if state is LOW
            if (state == "HIGH"): valOutReg[0] = valOutReg[0] | PIN_RVCtrl #set RVCtrl bit to 1 if state is HIGH
        if pinOption == "nSleep":
            if (state == "LOW"): valOutReg[0] = valOutReg[0] & PIN_nSleep  #set nSleep bit to 0 if state is LOW
            if (state == "HIGH"): valOutReg[0] = valOutReg[0] | PIN_nSleep #set nSleep bit to 1 if state is HIGH
        if pinOption == "ENABLE":
            if (state == "LOW"): valOutReg[0] = valOutReg[0] & PIN_ENABLE  #set ENABLE bit to 0 if state is LOW
            if (state == "HIGH"): valOutReg[0] = valOutReg[0] | PIN_ENABLE #set ENABLE bit to 1 if state is HIGH
        if pinOption == "ADCRST":
            if (state == "LOW"): valOutReg[0] = valOutReg[0] & PIN_ADCRST  #set ADCRST bit to 0 if state is LOW
            if (state == "HIGH"): valOutReg[0] = valOutReg[0] | PIN_ADCRST #set ADCRST bit to 1 if state is HIGH
        
        #Write to Refrigerator Valve
        WriteReg(i2cbus, ADDRESS, CMD_OUT0, valOutReg[0])
            
    except:
        print("Exception: PCA9535- Could not write output register.\n" + str(pinOption))
        

#**MAIN**





#SETUP GPIO
GPIOsetup()

#SETUP I2C Bus
i2cbus = SMBus(channel)

#initial write to config and polarity inversion register
try:
    WriteRegPair(i2cbus, ADDRESS, CMD_POL0, REG_POL0, REG_POL1) #starting with the polarity 0 register, write 2 bytes containing the polarity register bytes
except:
    print("Exception: PCA9535- Could not write polarity register.\n")
try:
    WriteRegPair(i2cbus, ADDRESS, CMD_CON0, REG_CON0, REG_CON1) #starting with the config 0 register, write 2 bytes containing the config register bytes
except:
    print("Exception: PCA9535- Could not write configuration register.\n")
try:
    valOutReg = ReadRegPair(i2cbus, ADDRESS, CMD_OUT0)
except:
    valOutReg = [0x00,0x00]
    print("Exception: PCA0535- Could not read initial value of output register. Set to 0x00,0x00.\n")
#Construct and initialize GUI
    
root = Tk() #Create TKinter object for GUI

root.geometry("500x500") #Configure GUI geometry

root.title('AHU Test GUI') #Create title of GUI

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N,W,E,S))
root.grid_columnconfigure(0,weight=1)
root.grid_rowconfigure(0, weight=1)

RVCtrl_lbl = ttk.Label(mainframe, text="Refrigerator Valve Control (P3)")
RVCtrlvar = StringVar()
RVCtrl = ttk.Combobox(mainframe, textvariable=RVCtrlvar)
RVCtrl.bind("<<CombboxSelected>>", writeOutputs)
RVCtrl['values'] = ('HIGH', 'LOW')


#Grid Widgets
RVCtrl_lbl.grid(column=0,row=0,padx=10,pady=5)
RVCtrl.grid(column=0,row=1,pady=20)

#Start main loop of GUI
root.mainloop()

#State machine to read input registers and write to output registers (maybe read from output register to check its value,
#                                                                     or ask Frank to check if the output state is measured by
#                                                                     the input registers too (ie pin value vs output flipflop)



    
