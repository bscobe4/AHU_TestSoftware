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
RHC_PIN = 13 #Refrigerant Heater Control
AHC_PIN = 15 #Air Heater Control
DIR_PIN = 11
STEP_PIN = 12

#GLOBAL VARIABLES
valInpReg = []
valOutReg = [] #desired value of the output register, not necessarily actual value
valPolReg = [REG_POL0,REG_POL1]
valConReg = [REG_CON0,REG_CON1]

InputPins = {"Fan Current Fault 1": bool,
            "Fan Current Fault 2": bool,
            "Fan Voltage Monitor": bool,
            "Air Heater Voltage Monitor": bool,
            "Air Heater Current Fault 1": bool,
            "Air Heater Current Fault 2": bool,
            "Refrigerant Heater Voltage Monitor": bool,
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
    GPIO.setup(DIR_PIN, GPIO.OUT) #Stepper Motor Direction
    GPIO.setup(STEP_PIN, GPIO.OUT) #Stepper Motor step pin
    

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
            print("Exception: read input registers failed in PCA9535 module\n")
            noError = False
            
        #Print status (or refresh status display?
        InputPins["Fan Current Fault 1"] = "HIGH" if (valInpReg[0] & 0x02) else "LOW"
        InputPins["Fan Current Fault 2"] = "HIGH" if (valInpReg[0] & 0x01) else "LOW"
        InputPins["Fan Voltage Monitor"] = "HIGH" if (valInpReg[0] & 0x04) else "LOW"

        InputPins["Air Heater Voltage Monitor"] = "HIGH" if (valInpReg[1] & 0x01) else "LOW"
        InputPins["Air Heater Current Fault 1"] = "HIGH" if (valInpReg[1] & 0x02) else "LOW"
        InputPins["Air Heater Current Fault 2"] = "HIGH" if (valInpReg[1] & 0x04) else "LOW"
        InputPins["Refrigerant Heater Voltage Monitor"] = "HIGH" if (valInpReg[1] & 0x08) else "LOW"
        InputPins["Refrigerant Heater Current Fault 1"] = "HIGH" if (valInpReg[1] & 0x10) else "LOW"
        InputPins["Refrigerant Heater Current Fault 2"] = "HIGH" if (valInpReg[1] & 0x20) else "LOW"
        InputPins["nFAULT"] = "HIGH" if (valInpReg[1] & 0x80) else "LOW"
        
        #for pin in InputPins:
        #    print(pin + " " + InputPins[pin]) #DEBUG Does this only print
        FanI1_val['text'] = InputPins['Fan Current Fault 1']
        FanI2_val['text'] = InputPins['Fan Current Fault 2']
        FanV_val['text'] = InputPins['Fan Voltage Monitor']
        AHV_val['text'] = InputPins['Air Heater Voltage Monitor']
        AHI1_val['text'] = InputPins['Air Heater Current Fault 1']
        AHI2_val['text'] = InputPins['Air Heater Current Fault 2']
        RHV_val['text'] = InputPins['Refrigerant Heater Voltage Monitor']
        RHI1_val['text'] = InputPins['Refrigerant Heater Current Fault 1']
        RHI2_val['text'] = InputPins['Refrigerant Heater Current Fault 2']
        nFAULT_val['text'] = InputPins['nFAULT']

def writeOutputs():
    try:
    #if pinOption == "RVCtrl":
        if (RVCtrlState.get() == "RVCtrlLOW"): valOutReg[0] = valOutReg[0] & PIN_RVCtrl  #set RVCtrl bit to 0 if state is LOW
        if (RVCtrlState.get() == "RVCtrlHIGH"): valOutReg[0] = valOutReg[0] | PIN_RVCtrl #set RVCtrl bit to 1 if state is HIGH
    #if pinOption == "nSleep":
        if (nSleepState.get() == "nSleepLOW"): valOutReg[0] = valOutReg[0] & PIN_nSleep  #set nSleep bit to 0 if state is LOW
        if (nSleepState.get() == "nSleepHIGH"): valOutReg[0] = valOutReg[0] | PIN_nSleep #set nSleep bit to 1 if state is HIGH
    #if pinOption == "ENABLE":
        if (ENABLEState.get() == "ENABLELOW"): valOutReg[0] = valOutReg[0] & PIN_ENABLE  #set ENABLE bit to 0 if state is LOW
        if (ENABLEState.get() == "ENABLEHIGH"): valOutReg[0] = valOutReg[0] | PIN_ENABLE #set ENABLE bit to 1 if state is HIGH
    #if pinOption == "ADCRST":
        if (ADCRSTState.get() == "ADCRSTLOW"): valOutReg[0] = valOutReg[0] & PIN_ADCRST  #set ADCRST bit to 0 if state is LOW
        if (ADCRSTState.get() == "ADCRSTHIGH"): valOutReg[0] = valOutReg[0] | PIN_ADCRST #set ADCRST bit to 1 if state is HIGH
        
        #Write to Refrigerator Valve
        WriteReg(i2cbus, ADDRESS, CMD_OUT0, valOutReg[0])
            
    except:
        print("Exception: PCA9535- Could not write output register.\n")
        #Read output register afterwards?

#Callback function for setting motor direction
def setDir():
    try:
        if (DIRState.get() == "DIRLOW"): GPIO.output(DIR_PIN, GPIO.LOW)
        if (DIRState.get() == "DIRHIGH"): GPIO.output(DIR_PIN, GPIO.HIGH)
    except:
        print("Exception: could not change stepper motor direction")
        
def runSTEP():
    #stepToggle = True
    stepDur = STEPduration.get()
    startTime = time.time_ns()
    STEPState = False
    while not StepStop.get() == 'STOP':
        nowTime= time.time_ns() - startTime
        print(str(nowTime))
        if nowTime > int(stepDur):
            startTime = time.time_ns()
            if not STEPState:
                GPIO.output(STEP_PIN, GPIO.HIGH)
                STEPState = True
                STEPState_val['text'] = "HIGH"
                print("HIGH")
            if STEPState:
                GPIO.output(STEP_PIN, GPIO.LOW)
                STEPState = False
                STEPState_val['text'] = "LOW"
                print("LOW")

def STEPThread():
    #Call runSTEP function
    t2=Thread(target=runSTEP)
    t2.start()

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

root.geometry("800x500") #Configure GUI geometry

root.title('AHU Test GUI') #Create title of GUI

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N,W,E,S))
root.grid_columnconfigure(0,weight=1)
root.grid_rowconfigure(0, weight=1)

Read_button = ttk.Button(mainframe, text="Start Input Registers Read", command=threading)

FanI1_lbl = ttk.Label(mainframe, text="Fan Current Fault 1 :")
FanI2_lbl = ttk.Label(mainframe, text="Fan Current Fault 2 :")
FanV_lbl = ttk.Label(mainframe, text="Fan Voltage Monitor :")
AHV_lbl = ttk.Label(mainframe, text="Air Heater Voltage Monitor :")
AHI1_lbl = ttk.Label(mainframe, text="Air Heater Current Fault 1 :")
AHI2_lbl = ttk.Label(mainframe, text="Air Heater Current Fault 2 :")
RHV_lbl = ttk.Label(mainframe, text="Refrigerant Heater Voltage Monitor :")
RHI1_lbl = ttk.Label(mainframe, text="Refrigerant Heater Current Fault 1 :")
RHI2_lbl = ttk.Label(mainframe, text="Refrigerant Heater Current Fault 2 :")
nFAULT_lbl = ttk.Label(mainframe, text="nFault :")

FanI1_val = ttk.Label(mainframe, text="NO DATA")
FanI2_val = ttk.Label(mainframe, text="NO DATA")
FanV_val = ttk.Label(mainframe, text="NO DATA")
AHV_val = ttk.Label(mainframe, text="NO DATA")
AHI1_val = ttk.Label(mainframe, text="NO DATA")
AHI2_val = ttk.Label(mainframe, text="NO DATA")
RHV_val = ttk.Label(mainframe, text="NO DATA")
RHI1_val = ttk.Label(mainframe, text="NO DATA")
RHI2_val = ttk.Label(mainframe, text="NO DATA")
nFAULT_val = ttk.Label(mainframe, text="NO DATA")

RVCtrl_lbl = ttk.Label(mainframe, text="Refrigerator Valve Control (P3)")
RVCtrlState = StringVar()
RVCtrl_lo = ttk.Radiobutton(mainframe, text="LOW", command=writeOutputs, variable=RVCtrlState, value='RVCtrlLOW')
RVCtrl_hi = ttk.Radiobutton(mainframe, text="HIGH", command=writeOutputs, variable=RVCtrlState, value='RVCtrlHIGH')

nSleep_lbl = ttk.Label(mainframe, text="nSleep (P4)")
nSleepState = StringVar()
nSleep_lo = ttk.Radiobutton(mainframe, text="LOW", command=writeOutputs, variable=nSleepState, value='nSleepLOW')
nSleep_hi = ttk.Radiobutton(mainframe, text="HIGH", command=writeOutputs, variable=nSleepState, value='nSleepHIGH')

ENABLE_lbl = ttk.Label(mainframe, text="ENABLE (P5)")
ENABLEState = StringVar()
ENABLE_lo = ttk.Radiobutton(mainframe, text="LOW", command=writeOutputs, variable=ENABLEState, value='ENABLELOW')
ENABLE_hi = ttk.Radiobutton(mainframe, text="HIGH", command=writeOutputs, variable=ENABLEState, value='ENABLEHIGH')

ADCRST_lbl = ttk.Label(mainframe, text="ADCRST (P16)")
ADCRSTState = StringVar()
ADCRST_lo = ttk.Radiobutton(mainframe, text="LOW", command=writeOutputs, variable=ADCRSTState, value='ADCRSTLOW')
ADCRST_hi = ttk.Radiobutton(mainframe, text="HIGH", command=writeOutputs, variable=ADCRSTState, value='ADCRSTHIGH')

DIR_lbl = ttk.Label(mainframe, text="Stepper Direction (DIR)")
DIRState = StringVar()
DIR_lo = ttk.Radiobutton(mainframe, text="LOW", command=setDir, variable=DIRState, value='DIRLOW')
DIR_hi = ttk.Radiobutton(mainframe, text="HIGH", command=setDir, variable=DIRState, value='DIRHIGH')

STEPstart_button = ttk.Button(mainframe, text="Start STEP input", command=STEPThread)
StepStop = StringVar()
STEPstop_button = ttk.Checkbutton(mainframe, text="Stop STEP input", variable=StepStop, onvalue='STOP', offvalue='notSTOP')
STEPdur_lbl = ttk.Label(mainframe, text="Step Duration (ns)")
STEPduration = StringVar()
STEPrate = ttk.Entry(mainframe, textvariable=STEPduration)
STEPduration.set("1")
STEPState_val = ttk.Label(mainframe, text="NO DATA")


#Grid Widgets
Read_button.grid(column=0, columnspan=2, row=3, pady=20)

inLblCol = 0
inLblCspan = 1
inLblPady = 5

FanI1_lbl.grid(column=inLblCol, row=4, columnspan=inLblCspan, pady=5)
FanI2_lbl.grid(column=inLblCol, row=5, columnspan=inLblCspan, pady=5)
FanV_lbl.grid(column=inLblCol, row=6, columnspan=inLblCspan, pady=5)
AHV_lbl.grid(column=inLblCol, row=7, columnspan=inLblCspan, pady=5)
AHI1_lbl.grid(column=inLblCol, row=8, columnspan=inLblCspan, pady=5)
AHI2_lbl.grid(column=inLblCol, row=9, columnspan=inLblCspan, pady=5)
RHV_lbl.grid(column=inLblCol, row=10, columnspan=inLblCspan, pady=5)
RHI1_lbl.grid(column=inLblCol, row=11, columnspan=inLblCspan, pady=5)
RHI2_lbl.grid(column=inLblCol, row=12, columnspan=inLblCspan, pady=5)
nFAULT_lbl.grid(column=inLblCol, row=13, columnspan=inLblCspan, pady=5)

inValCol = 1
inValPady = 5

FanI1_val.grid(column=inValCol, row=4, pady=inValPady)
FanI2_val.grid(column=inValCol, row=5, pady=inValPady)
FanV_val.grid(column=inValCol, row=6, pady=inValPady)
AHV_val.grid(column=inValCol, row=7, pady=inValPady)
AHI1_val.grid(column=inValCol, row=8, pady=inValPady)
AHI2_val.grid(column=inValCol, row=9, pady=inValPady)
RHV_val.grid(column=inValCol, row=10, pady=inValPady)
RHI1_val.grid(column=inValCol, row=11, pady=inValPady)
RHI2_val.grid(column=inValCol, row=12, pady=inValPady)
nFAULT_val.grid(column=inValCol, row=13, pady=inValPady)

RVCtrl_lbl.grid(column=0,row=0,padx=10,pady=5)
RVCtrl_lo.grid(column=0,row=2,pady=10)
RVCtrl_hi.grid(column=0,row=1,pady=10)

nSleep_lbl.grid(column=1,row=0,padx=10,pady=5)
nSleep_lo.grid(column=1,row=2,pady=10)
nSleep_hi.grid(column=1,row=1,pady=10)

ENABLE_lbl.grid(column=2,row=0,padx=10,pady=5)
ENABLE_lo.grid(column=2,row=2,pady=10)
ENABLE_hi.grid(column=2,row=1,pady=10)

ADCRST_lbl.grid(column=3,row=0,padx=10,pady=5)
ADCRST_lo.grid(column=3,row=2,pady=10)
ADCRST_hi.grid(column=3,row=1,pady=10)

DIR_lbl.grid(column=4,row=0,padx=10,pady=5)
DIR_lo.grid(column=4,row=2,pady=10)
DIR_hi.grid(column=4,row=1,pady=10)

STEPstart_button.grid(column=2, row=4, pady=5)
STEPstop_button.grid(column=3, row=4, pady=5)
STEPdur_lbl.grid(column=2, row=5, pady=5)
STEPrate.grid(column=3, row=5, pady=5)
STEPState_val.grid(column=3, row=6, pady=5)

#Start main loop of GUI
root.mainloop()

#State machine to read input registers and write to output registers (maybe read from output register to check its value,
#                                                                     or ask Frank to check if the output state is measured by
#                                                                     the input registers too (ie pin value vs output flipflop)



    

