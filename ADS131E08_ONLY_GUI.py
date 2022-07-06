#!/usr/bin/python
# -*- coding:utf-8 -*-

import RPi.GPIO as GPIO
#import cffi
import time
from smbus import SMBus
from tkinter import *
from tkinter import ttk
from threading import *
import spidev
#import re
import sys
import select
import tty
import termios
import configparser

#SPI Addresses
spiaddr_ADS131E08 = 1
spiaddr_KX132 = 0

#CONSTANTS

#GLOBAL VARIABLES

CMD_ADC = {"WAKEUP": 0x02,
                 "STANDBY": 0x04,
                 "RESET": 0x06,
                 "START": 0x08,
                 "STOP": 0x0A,
                 "OFFSETCAL": 0x1A,
                 "RDATAC": 0x10,
                 "SDATAC": 0x11,
                 "RDATA": 0x12,
                 "RREG": 0x20,
                 "WREG": 0x40}

REGADDR_ADC = {'ID':0x00,
                     'CONFIG1':0x01,
                     'CONFIG2':0x02,
                     'CONFIG3':0x03,
                     'FAULT':0x04,
                     'CH1SET':0x05,
                     'CH2SET':0x06,
                     'CH3SET':0x07,
                     'CH4SET':0x08,
                     'CH5SET':0x09,
                     'CH6SET':0x0A,
                     'CH7SET':0x0B,
                     'CH8SET':0x0C,
                     'FAULT_STATP':0x12,
                     'FAULT_STATN':0x13,
                     'GPIO':0x14}

REGVAL_ADC = {'ID':bytes,
                     'CONFIG1':bytes,
                     'CONFIG2':bytes,
                     'CONFIG3':bytes,
                     'FAULT':bytes,
                     'CH1SET':bytes,
                     'CH2SET':bytes,
                     'CH3SET':bytes,
                     'CH4SET':bytes,
                     'CH5SET':bytes,
                     'CH6SET':bytes,
                     'CH7SET':bytes,
                     'CH8SET':bytes,
                     'FAULT_STATP':bytes,
                     'FAULT_STATN':bytes,
                     'GPIO':bytes}

#ID 0x00
IDREG = {'REV_ID': bytes, 'NU': bytes} 
#CONFIG1 0x01
CONFIG1REG = {'DAISY_IN': bytes, 'CLK_EN': bytes, 'DR[2:0]': bytes}
#CONFIG2 0x02
CONFIG2REG = {'INT_TEST': bytes, 'TEST_AMP0': bytes, 'TEST_FREQ[1:0]': bytes}
#CONFIG3 0x03
CONFIG3REG = {'PDB_REFBUF': bytes, 'VREF_4V': bytes, 'OPAMP_REF': bytes, 'PDB_OPAMP':bytes}
#FAULT 0x04
FAULTREG = {'COMP_TH[2:0]': bytes}
#CH1SET 0x05
CH1SETREG = {'PD1': bytes, 'GAIN1[2:0]': bytes, 'MUX1[2:0]': bytes}
#CH2SET 0x06
CH2SETREG = {'PD2': bytes, 'GAIN2[2:0]': bytes, 'MUX2[2:0]': bytes}
#CH3SET 0x07
CH3SETREG = {'PD3': bytes, 'GAIN3[2:0]': bytes, 'MUX3[2:0]': bytes}
#CH4SET 0x08
CH4SETREG = {'PD4': bytes, 'GAIN4[2:0]': bytes, 'MUX4[2:0]': bytes}
#CH5SET 0x09
CH5SETREG = {'PD5': bytes, 'GAIN5[2:0]': bytes, 'MUX5[2:0]': bytes}
#CH6SET 0x0A
CH6SETREG = {'PD6': bytes, 'GAIN6[2:0]': bytes, 'MUX6[2:0]': bytes}
#CH7SET 0x0B
CH7SETREG = {'PD7': bytes, 'GAIN7[2:0]': bytes, 'MUX7[2:0]': bytes}
#CH8SET 0x0C
CH8SETREG = {'PD8': bytes, 'GAIN8[2:0]': bytes, 'MUX8[2:0]': bytes}
#FAULT_STATP 0x12
FAULT_STATPREG = {'IN8P_FAULT': bytes,'IN7P_FAULT': bytes,'IN6P_FAULT': bytes,'IN5P_FAULT': bytes,'IN4P_FAULT': bytes,'IN3P_FAULT': bytes,'IN2P_FAULT': bytes,'IN1P_FAULT': bytes}
#FAULT_STATN 0x13
FAULT_STATNREG = {'IN8N_FAULT': bytes,'IN7N_FAULT': bytes,'IN6N_FAULT': bytes,'IN5N_FAULT': bytes,'IN4N_FAULT': bytes,'IN3N_FAULT': bytes,'IN2N_FAULT': bytes,'IN1N_FAULT': bytes}
#GPIO 0x14
GPIOREG = {'GPIOD4': bytes, 'GPIOD3': bytes, 'GPIOD2': bytes, 'GPIOD1': bytes, 'GPIOC4': bytes, 'GPIOC3': bytes, 'GPIOC2': bytes, 'GPIOC1': bytes}


#**FUNCTION DEFINITIONS**
def sendADCcmd():
    try:
        spi.writebytes([CMD_ADC[CMDvar.get()]])
        if CMDvar.get() == 'RDATA':
            data = spi.readbytes(1)
            print(data)
            DATAval_lbl['text'] = "Data Value: " + str(data)
    except:
        print("Could not send command" + CMDvar.get())
    return 0

def readregs_ADS131E08(): #Check if byte pairs need to be split in half
    #spi.writebytes([CMD_ADC['RREG'],REGADDR_ADC[REGvar.get()]])
    #print(hex(CMD_ADC['RREG'] + REGADDR_ADC[REGvar.get()]))
    try:    
        spi.writebytes([CMD_ADC['RREG'] + REGADDR_ADC[REGvar.get()], 0x00])
        regs = spi.readbytes(1)
        print(regs)
        print(hex(CMD_ADC['RREG'] + REGADDR_ADC[REGvar.get()]))
        REGval_lbl['text'] = "Register Value: " + str(regs)
    
    except:
        print("Could not read register " + REGvar.get())
    
    return 0

def writeregs_ADS131E08(): #NO NO can't do this, RREG and WREG need to be composed first, then the value of the command integrates the register valu
    #try:    
    spi.writebytes([CMD_ADC['WREG'] + REGADDR_ADC[REGvar.get()], 0x00, int(DATAvar.get(), 16)])
    print(hex(CMD_ADC['WREG'] + REGADDR_ADC[REGvar.get()]))
    REGval_lbl['text'] = "Register Value: " + hex(int(DATAvar.get(), 16))

    #except:
    #    print("Could not write" + DATAvar.get() + "to register " + REGvar.get())
    #return 0

def ADCThreadCMD():
    #Call runSTEP function
    t3=Thread(target=sendADCcmd)
    t3.start()
    
def ADCThreadRREG():
    #Call runSTEP function
    t4=Thread(target=readregs_ADS131E08)
    t4.start()
def ADCThreadWREG():
    #Call runSTEP function
    t5=Thread(target=writeregs_ADS131E08)
    t5.start()
#**MAIN**


#Setup SPI Bus
spi = spidev.SpiDev()
spi.open(0,spiaddr_ADS131E08)
spi.max_speed_hz = 500000
spi.mode = 0

#Construct and initialize GUI

adcgui = Tk() #Create TKinter object for GUI

adcgui.geometry("800x500") #Configure GUI geometry

adcgui.title('ADS131E08 Test GUI') #Create title of GUI

adcframe = ttk.Frame(adcgui, padding="3 3 12 12")
adcframe.grid(column=0, row=0, sticky=(N,W,E,S))
adcgui.grid_columnconfigure(0,weight=1)
adcgui.grid_rowconfigure(0, weight=1)

DATAval_lbl = ttk.Label(adcframe, text="Data Value: no data")

CMDvar = StringVar()
ADCcmd_box = ttk.Combobox(adcframe, textvariable=CMDvar)
ADCcmd_box.state(["readonly"])
ADCcmd_box['values'] = ("WAKEUP", "STANDBY", "RESET", "START", "STOP", "OFFSETCAL", "RDATAC", "SDATAC","RDATA")#, "RREG", "WREG")

REGval_lbl = ttk.Label(adcframe, text="Register Value: no data")

REGvar = StringVar()
ADCreg_box = ttk.Combobox(adcframe, textvariable=REGvar)
ADCreg_box.state(["readonly"])
ADCreg_box['values'] = ('ID' ,'CONFIG1','CONFIG2','CONFIG3','FAULT','CH1SET','CH2SET','CH3SET','CH4SET','CH5SET','CH6SET','CH7SET','CH8SET','FAULT_STATP','FAULT_STATN','GPIO')



DATAvar = StringVar()
ADCdata_box = ttk.Entry(adcframe, textvariable=DATAvar)

ADCcmd_button = ttk.Button(adcframe, text="Send ADC Command", command=ADCThreadCMD)
ADCrreg_button = ttk.Button(adcframe, text="Read Register", command=ADCThreadRREG)
ADCwreg_button = ttk.Button(adcframe, text="Write Register", command=ADCThreadWREG)



#Grid Widgets

DATAval_lbl.grid(column=3, row=0, pady=10)

ADCcmd_box.grid(column=0, row=0, pady=10)
ADCreg_box.grid(column=0, row=1, pady=10)
ADCdata_box.grid(column=0, row=2, pady=10)

REGval_lbl.grid(column=3, row = 1, pady=10)

ADCcmd_button.grid(column=1, row=0, pady=10)
ADCrreg_button.grid(column=1, row=1, pady=10)
ADCwreg_button.grid(column=1, row=2, pady=10)

#Start main loop of GUI
adcgui.mainloop()