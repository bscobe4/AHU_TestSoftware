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


#ACC Register Definitions:
REGADDR_ACC = {'MAN_ID': 0x00,'PART_ID': 0x01,'XADP_L': 0x02,'XADP_H': 0x03,'YADP_L': 0x04,'YADP_H': 0x05,'ZADP_L': 0x06,'ZADP_H': 0x07,'XOUT_L': 0x08,'XOUT_H': 0x09,'YOUT_L': 0x0A,'YOUT_H': 0x0B,'ZOUT_L': 0x0C,'ZOUT_H': 0x0D,
                        'COTR': 0x12,'WHO_AM_I': 0x13,'TSCP': 0x14,'TSPP': 0x15,'INS1': 0x16,'INS2': 0x17,'INS3': 0x18,'STATUS_REG': 0x19,'INT_REL': 0x1A,'CNTL1': 0x1B,'CNTL2': 0x1C,'CNTL3': 0x1D,'CNTL4': 0x1E,'CNTL5': 0x1F,'CNTL6': 0x20,'ODCNTL': 0x21,'INC1': 0x22,'INC2': 0x23,'INC3': 0x24,'INC4': 0x25,'INC5': 0x26,'INC6': 0x27,
                        'TILT_TIMER': 0x29,'TDTRC': 0x2A,'TDTC': 0x2B,'TTH': 0x2C,'TTL': 0x2D,'FTD': 0x2E,'STD': 0x2F,'TLT': 0x30,'TWS': 0x31,'FFTH': 0x32,'FFC': 0x33,'FFCNTL': 0x34,
                        'TILT_ANGLE_LL': 0x37,'TILT_ANGLE_HL': 0x38,'HYST_SET': 0x39,'LP_CNTL1': 0x3A,'LP_CNTL2': 0x3B,
                        'WUFTH': 0x49,'BTSWUFTH': 0x4A,'BTSTH': 0x4B,'BTSC': 0x4C,'WUFC': 0x4D,
                        'SELF_TEST': 0x5D,'BUF_CNTL1': 0x5E,'BUF_CNTL2': 0x5F,'BUF_STATUS_1': 0x60,'BUF_STATUS_2': 0x61,'BUF_CLEAR': 0x62,'BUF_READ': 0x63,
                        'ADP_CNTL1': 0x64,'ADP_CNTL2': 0x65,'ADP_CNTL3': 0x66,'ADP_CNTL4': 0x67,'ADP_CNTL5': 0x68,'ADP_CNTL6': 0x69,'ADP_CNTL7': 0x6A,'ADP_CNTL8': 0x6B,'ADP_CNTL9': 0x6C,'ADP_CNTL10': 0x6D,
                        'ADP_CNTL11': 0x6E,'ADP_CNTL12': 0x6F,'ADP_CNTL13': 0x70,'ADP_CNTL14': 0x71,'ADP_CNTL15': 0x72,'ADP_CNTL16': 0x73,'ADP_CNTL17': 0x74,'ADP_CNTL18': 0x75,'ADP_CNTL19': 0x76}

#**FUNCTION DEFINITIONS**
def sendADCcmd():
    try:
        spi.open(0,spiaddr_ADS131E08)
        spi.writebytes([CMD_ADC[CMDvar.get()]])
        if CMDvar.get() == 'RDATA':
            data = spi.readbytes(1)
            #print(data)
            DATAval_lbl['text'] = "ADC Data Value: " + str(data)
        spi.close()
    except:
        print("Could not send ADC command" + CMDvar.get())
    #return 0
        
def ADCReadAllReg():
    try:
        REGvar.set('ID')
        spi.open(0,spiaddr_ADS131E08)
        spi.writebytes([CMD_ADC['RREG'] + REGADDR_ADC[REGvar.get()], 0x0F]) #Read ll 16 registers starting with "ID"
        regs = spi.readbytes(16)
        #print(regs)
        #print(hex(CMD_ADC['RREG'] + REGADDR_ADC[REGvar.get()]))
        #REGval_lbl['text'] = "ADC Register Values: " + str(regs)
        spi.close()
        
        ID_lblv['text'] = str(regs[0])
        CONFIG1_lblv['text'] = str(regs[1])
        CONFIG2_lblv['text'] = str(regs[2])
        CONFIG3_lblv['text'] = str(regs[3])
        FAULT_lblv['text'] = str(regs[4])
        CH1SET_lblv['text'] = str(regs[5])
        CH2SET_lblv['text'] = str(regs[6])
        CH3SET_lblv['text'] = str(regs[7])
        CH4SET_lblv['text'] = str(regs[8])
        CH5SET_lblv['text'] = str(regs[9])
        CH6SET_lblv['text'] = str(regs[10])
        CH7SET_lblv['text'] = str(regs[11])
        CH8SET_lblv['text'] = str(regs[12])
        FAULT_STATP_lblv['text'] = str(regs[13])
        FAULT_STATN_lblv['text'] = str(regs[14])
        GPIO_lblv['text'] = str(regs[15])
    except:
        print("Could not read ADC register " + REGvar.get())
        
def ADCInit():
    try:
        CMDvar.set("RESET")
        sendADCcmd()
    except:
        print("Could not initial reset ADC")
    try:
        CMDvar.set("SDATAC")
        sendADCcmd()
    except:
        print("Could not stop ADC continuous read")
    ADCReadAllReg()

def readregs_ADS131E08(): #Check if byte pairs need to be split in half
    #spi.writebytes([CMD_ADC['RREG'],REGADDR_ADC[REGvar.get()]])
    #print(hex(CMD_ADC['RREG'] + REGADDR_ADC[REGvar.get()]))
    try:
        spi.open(0,spiaddr_ADS131E08)
        spi.writebytes([CMD_ADC['RREG'] + REGADDR_ADC[REGvar.get()], 0x00])
        regs = spi.readbytes(1)
        #print(regs)
        print(hex(CMD_ADC['RREG'] + REGADDR_ADC[REGvar.get()]))
        REGval_lbl['text'] = "ADC Register Value: " + str(regs)
        spi.close()
    except:
        print("Could not read ADC register " + REGvar.get())
    
    #return 0

def writeregs_ADS131E08(): #NO NO can't do this, RREG and WREG need to be composed first, then the value of the command integrates the register valu
    try:    
        spi.open(0,spiaddr_ADS131E08)
        spi.writebytes([CMD_ADC['WREG'] + REGADDR_ADC[REGvar.get()], 0x00, int(DATAvar.get(), 16)])
        print(hex(CMD_ADC['WREG'] + REGADDR_ADC[REGvar.get()]))
        REGval_lbl['text'] = "ADC Register Value: " + hex(int(DATAvar.get(), 16))
        spi.close()
    except:
        print("Could not write " + DATAvar.get() + "to ADC register " + REGvar.get())
    #return 0

def readregs_KX132(): #Check if byte pairs need to be split in half
    #try:
    spi.open(0,spiaddr_KX132)
    spi.writebytes([0x80 + REGADDR_ACC[REGadd.get()]])
    regs = spi.readbytes(1)
    print(regs)
    print(hex(0x80 + REGADDR_ACC[REGadd.get()]))
    REGvalAcc_lbl['text'] = "ACC Register Value: " + str(regs)
    spi.close()
    #except:
    #    print("Could not read ACC register " + REGadd.get())
        
def writeregs_KX132():
    #try:    
    spi.open(0,spiaddr_KX132)
    #spi.writebytes([CMD_ADC['WREG'] + REGADDR_ADC[REGvar.get()], 0x00, int(DATAvar.get(), 16)])
    spi.writebytes([REGADDR_ACC[REGadd.get()],int(REGvalAcc.get(), 16)])
    print(hex(REGADDR_ACC[REGadd.get()]))
    REGvalAcc_lbl['text'] = " ACC Register Value: " + hex(int(REGvalAcc.get(), 16))
    spi.close()
    #except:
    #    print("Could not write " + DATAvar.get() + "to ACC register " + REGvar.get())

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
    
def ACCThreadRREG():
    t6=Thread(target=readregs_KX132)
    t6.start()
    
def ACCThreadWREG():
    t7=Thread(target=writeregs_KX132)
    t7.start()
    
 
    
#**MAIN**


#Setup SPI Bus
spi = spidev.SpiDev()
#spi.max_speed_hz = 500000
#spi.mode = 0

#Construct and initialize GUI

adcgui = Tk() #Create TKinter object for GUI

adcgui.geometry("590x390") #Configure GUI geometry

adcgui.title('ADS131E08 Test GUI') #Create title of GUI

adcframe = ttk.Frame(adcgui, padding="3 3 12 12")
adcframe.grid(column=0, row=0, sticky=(N,W,E,S))
regframe = ttk.Frame(adcgui, padding=" 3 3 12 12")
regframe.grid(column=0, row=1, sticky=(N,W,E,S))
adcgui.grid_columnconfigure(0,weight=1)
adcgui.grid_rowconfigure(0, weight=1)

DATAval_lbl = ttk.Label(adcframe, text="ADC Data Value: no data")

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
ADCrreg_button = ttk.Button(adcframe, text="Read ADC Register", command=ADCThreadRREG)
ADCwreg_button = ttk.Button(adcframe, text="Write ADC Register", command=ADCThreadWREG)


REGadd = StringVar()
ACCreg_box = ttk.Combobox(adcframe, textvariable=REGadd)
ACCreg_box.state(["readonly"])
ACCreg_box['values'] = ('MAN_ID','PART_ID','XADP_L','XADP_H','YADP_L','YADP_H','ZADP_L','ZADP_H','XOUT_L','XOUT_H','YOUT_L','YOUT_H','ZOUT_L','ZOUT_H',
                        'COTR','WHO_AM_I','TSCP','TSPP','INS1','INS2','INS3','STATUS_REG','INT_REL','CNTL1','CNTL2','CNTL3','CNTL4','CNTL5','CNTL6','ODCNTL','INC1','INC2','INC3','INC4','INC5','INC6',
                        'TILT_TIMER','TDTRC','TDTC','TTH','TTL','FTD','STD','TLT','TWS','FFTH','FFC','FFCNTL',
                        'TILT_ANGLE_LL','TILT_ANGLE_HL','HYST_SET','LP_CNTL1','LP_CNTL2',
                        'WUFTH','BTSWUFTH','BTSTH','BTSC','WUFC',
                        'SELF_TEST','BUF_CNTL1','BUF_CNTL2','BUF_STATUS_1','BUF_STATUS_2','BUF_CLEAR','BUF_READ',
                        'ADP_CNTL1','ADP_CNTL2','ADP_CNTL3','ADP_CNTL4','ADP_CNTL5','ADP_CNTL6','ADP_CNTL7','ADP_CNTL8','ADP_CNTL9','ADP_CNTL10',
                        'ADP_CNTL11','ADP_CNTL12','ADP_CNTL13','ADP_CNTL14','ADP_CNTL15','ADP_CNTL16','ADP_CNTL17','ADP_CNTL18','ADP_CNTL19')

REGvalAcc = StringVar()
ACCdata_box = ttk.Entry(adcframe, textvariable=REGvalAcc)

ACCrreg_button = ttk.Button(adcframe, text="Read ACC Register", command=ACCThreadRREG)
ACCwreg_button = ttk.Button(adcframe, text="Write ACC Register", command=ACCThreadWREG)

REGvalAcc_lbl = ttk.Label(adcframe, text="ACC Register Value: no data")



ID_lbl = ttk.Label(regframe, text="ID:")
CONFIG1_lbl = ttk.Label(regframe, text="CONFIG1:")
CONFIG2_lbl = ttk.Label(regframe, text="CONFIG2:")
CONFIG3_lbl = ttk.Label(regframe, text="CONFIG3:")
FAULT_lbl = ttk.Label(regframe, text="FAULT:")
CH1SET_lbl = ttk.Label(regframe, text="CH1SET:")
CH2SET_lbl = ttk.Label(regframe, text="CH2SET:")
CH3SET_lbl = ttk.Label(regframe, text="CH3SET:")
CH4SET_lbl = ttk.Label(regframe, text="CH4SET:")
CH5SET_lbl = ttk.Label(regframe, text="CH5SET:")
CH6SET_lbl = ttk.Label(regframe, text="CH6SET:")
CH7SET_lbl = ttk.Label(regframe, text="CH7SET:")
CH8SET_lbl = ttk.Label(regframe, text="CH8SET:")
FAULT_STATP_lbl = ttk.Label(regframe, text="FAULT_STATP:")
FAULT_STATN_lbl = ttk.Label(regframe, text="FAULT_STATN:")
GPIO_lbl = ttk.Label(regframe, text="GPIO:")

ID_lblv = ttk.Label(regframe, text="ID:")
CONFIG1_lblv = ttk.Label(regframe, text="")
CONFIG2_lblv = ttk.Label(regframe, text="")
CONFIG3_lblv = ttk.Label(regframe, text="")
FAULT_lblv = ttk.Label(regframe, text="")
CH1SET_lblv = ttk.Label(regframe, text="")
CH2SET_lblv = ttk.Label(regframe, text="")
CH3SET_lblv = ttk.Label(regframe, text="")
CH4SET_lblv = ttk.Label(regframe, text="")
CH5SET_lblv = ttk.Label(regframe, text="")
CH6SET_lblv = ttk.Label(regframe, text="")
CH7SET_lblv = ttk.Label(regframe, text="")
CH8SET_lblv = ttk.Label(regframe, text="")
FAULT_STATP_lblv = ttk.Label(regframe, text="")
FAULT_STATN_lblv = ttk.Label(regframe, text="")
GPIO_lblv = ttk.Label(regframe, text="")

ADCReadAllReg_button = ttk.Button(adcframe, text="Read All ADC Registers", command=ADCReadAllReg())
#ADC Initialization (THESE ARE BLOCKING, NOT THREADED)

#Initial ADC Reset
ADCInit()

#Grid Widgets

DATAval_lbl.grid(column=2, row=0, pady=10)

ADCcmd_box.grid(column=0, row=0, pady=10)
ADCreg_box.grid(column=0, row=1, pady=10)
ADCdata_box.grid(column=0, row=2, pady=10)

REGval_lbl.grid(column=2, row = 1, pady=10)

ADCcmd_button.grid(column=1, row=0, pady=10)
ADCrreg_button.grid(column=1, row=1, pady=10)
ADCwreg_button.grid(column=1, row=2, pady=10)

ACCreg_box.grid(column=0, row=5, pady=10)
ACCdata_box.grid(column=0, row=6, pady=10)
ACCrreg_button.grid(column=1, row=5, pady=10)
ACCwreg_button.grid(column=1, row=6, pady=10)
REGvalAcc_lbl.grid(column=2, row=5, pady=10)

ADCReadAllReg_button.grid(column=0, row=7, pady=10)

ID_lbl.grid(column=0, row=1, pady=2)
CONFIG1_lbl.grid(column=0, row=2, pady=2)
CONFIG2_lbl.grid(column=0, row=3, pady=2)
CONFIG3_lbl.grid(column=0, row=4, pady=2)
FAULT_lbl.grid(column=2, row=1, pady=2)
CH1SET_lbl.grid(column=2, row=2, pady=2)
CH2SET_lbl.grid(column=2, row=3, pady=2)
CH3SET_lbl.grid(column=2, row=4, pady=2)
CH4SET_lbl.grid(column=4, row=1, pady=2)
CH5SET_lbl.grid(column=4, row=2, pady=2)
CH6SET_lbl.grid(column=4, row=3, pady=2)
CH7SET_lbl.grid(column=4, row=4, pady=2)
CH8SET_lbl.grid(column=6, row=1, pady=2)
FAULT_STATP_lbl.grid(column=6, row=2, pady=2)
FAULT_STATN_lbl.grid(column=6, row=3, pady=2)
GPIO_lbl.grid(column=6, row=4, pady=2)

ADCpadx = 10

ID_lblv.grid(column=1, row=1, padx=ADCpadx, pady=2)
CONFIG1_lblv.grid(column=1, row=2, padx=ADCpadx, pady=2)
CONFIG2_lblv.grid(column=1, row=3, padx=ADCpadx, pady=2)
CONFIG3_lblv.grid(column=1, row=4, padx=ADCpadx, pady=2)
FAULT_lblv.grid(column=3, row=1, padx=ADCpadx, pady=2)
CH1SET_lblv.grid(column=3, row=2, padx=ADCpadx, pady=2)
CH2SET_lblv.grid(column=3, row=3, padx=ADCpadx, pady=2)
CH3SET_lblv.grid(column=3, row=4, padx=ADCpadx, pady=2)
CH4SET_lblv.grid(column=5, row=1, padx=ADCpadx, pady=2)
CH5SET_lblv.grid(column=5, row=2, padx=ADCpadx, pady=2)
CH6SET_lblv.grid(column=5, row=3, padx=ADCpadx, pady=2)
CH7SET_lblv.grid(column=5, row=4, padx=ADCpadx, pady=2)
CH8SET_lblv.grid(column=7, row=1, padx=ADCpadx, pady=2)
FAULT_STATP_lblv.grid(column=7, row=2, padx=ADCpadx, pady=2)
FAULT_STATN_lblv.grid(column=7, row=3, padx=ADCpadx, pady=2)
GPIO_lblv.grid(column=7, row=4, padx=ADCpadx, pady=2)

#Start main loop of GUI
adcgui.mainloop()
