import RPi.GPIO as GPIO
import spidev

#SPI Addresses
spiaddr_ADS131E08 = 1
spiaddr_KX132 = 1

ESC = False
numbytes = 1
mode = 0b01
clockrate = 1000000

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

#**FUNCTION DEFINITIONS**
def sendADCcmd(CMDvar):
    #try:
    spi.open(0,spiaddr_ADS131E08)
    spi.mode = mode
    if CMDvar == 'RDATA':
        spi.writebytes([CMD_ADC[CMDvar]])
        data = spi.readbytes(numbytes)
        #print(data)
        print("ADC Data Value: " + str(data))
    else:
        spi.writebytes([CMD_ADC[CMDvar]])
        
    spi.close()
    print(CMDvar + " command sent\n")
        
    #except:
    #    print("Could not send ADC command " + CMDvar)
    #return 0
        
def ADCReadAllReg():
    try:
        #REGvar.set('ID')
        spi.open(0,spiaddr_ADS131E08) #SPI bus 0, CS matches pin used by ADC
        spi.mode = mode
        spi.max_speed_hz = clockrate
        spi.writebytes([CMD_ADC['RREG'] + REGADDR_ADC['ID'], 0x0F]) #Read ll 16 registers starting with "ID"
        regs = spi.readbytes(16)
        #print(regs)
        #print(hex(CMD_ADC['RREG'] + REGADDR_ADC[REGvar.get()]))
        #REGval_lbl['text'] = "ADC Register Values: " + str(regs)
        spi.close()
        
        print('ID: ' + str(regs[0]) + '\n')
        print('CONFIG1: ' + str(regs[1]) + '\n')
        print('CONFIG2: ' + str(regs[2]) + '\n')
        print('CONFIG3: ' + str(regs[3]) + '\n')
        print('FAULT: ' + str(regs[4]) + '\n')
        print('CH1SET: ' + str(regs[5]) + '\n')
        print('CH2SET: ' + str(regs[6]) + '\n')
        print('CH3SET: ' + str(regs[7]) + '\n')
        print('CH4SET: ' + str(regs[8]) + '\n')
        print('CH5SET: ' + str(regs[9]) + '\n')
        print('CH6SET: ' + str(regs[10]) + '\n')
        print('CH7SET: ' + str(regs[11]) + '\n')
        print('CH8SET: ' + str(regs[12]) + '\n')
        print('FAULT_STATP: ' + str(regs[13]) + '\n')
        print('FAULT_STATN: ' + str(regs[14]) + '\n')
        print('GPIO: ' + str(regs[15]) + '\n')
        
    except:
        print("Could not read ADC register " + REGvar)

def ADCInit():
    try:
        sendADCcmd("RESET")
    except:
        print("Could not initial reset ADC")
    try:
        sendADCcmd("SDATAC")
    except:
        print("Could not stop ADC continuous read\n")
    ADCReadAllReg()

def readregs_ADS131E08(REGvar, numbytes): #Check if byte pairs need to be split in half
    #spi.writebytes([CMD_ADC['RREG'],REGADDR_ADC[REGvar.get()]])
    #print(hex(CMD_ADC['RREG'] + REGADDR_ADC[REGvar.get()]))
    try:
        spi.open(0,spiaddr_ADS131E08)
        spi.mode = mode
        spi.max_speed_hz = clockrate
        spi.writebytes([CMD_ADC['RREG'] + REGADDR_ADC[REGvar], 0x00])
        regs = spi.readbytes(numbytes)
        #print(regs)
        print(hex(CMD_ADC['RREG'] + REGADDR_ADC[REGvar]))
        REGval_lbl['text'] = "ADC Register Value: " + str(regs)
        spi.close()
    except:
        print("Could not read ADC register " + REGvar)
    
    #return 0

def writeregs_ADS131E08(REGvar, DATAvar, numbytes):
    try:    
        spi.open(0,spiaddr_ADS131E08)
        spi.mode = mode
        spi.max_speed_hz = clockrate
        spi.mode = 0x01
        spi.writebytes([CMD_ADC['WREG'] + REGADDR_ADC[REGvar], 0x00, int(DATAvar, 16)])
        print(hex(CMD_ADC['WREG'] + REGADDR_ADC[REGvar]))
        REGval_lbl['text'] = "ADC Register Value: " + hex(int(DATAvar, 16))
        spi.close()
    except:
        print("Could not write " + DATAvar + "to ADC register " + REGvar)
    #return 0

spi = spidev.SpiDev()

#Initial ADC Init
ADCInit()



while(not ESC):

    
    print("\n What would you like to do?\n 'cmd' --> Send ADC Command\n 'rdata' --> Read ADC Data\n 'rrega' --> Read all registers \n 'bytes' --> set number of bytes of data to read.\n 'spimode' --> spi mode (0,1,2 or 3)\n 'clk' --> set clockrate\n 'back' --> return to last page\n")
    op = input("\nEnter command:\n")
    if op == 'cmd':
        cmd = input('\nEnter command name ("WAKEUP": 0x02, "STANDBY": 0x04,"RESET": 0x06,"START": 0x08,"STOP": 0x0A,"OFFSETCAL": 0x1A,"RDATAC": 0x10,"SDATAC": 0x11,"RDATA": 0x12,"RREG": 0x20,"WREG": 0x40)\n')
        sendADCcmd(cmd)
    if op == 'rdata':
        sendADCcmd("RDATA")
    if op == 'rrega':
        ADCReadAllReg()
    if op == 'bytes':
        numbytes = int(input("\nEnter the bumber of bytes you want to read when you use the rdata command:\n"))
    if op == 'spimode':
        mode = int(input("\nEnter mode(0,1,2 or 3):\n"))
    if op == 'back':
        print("\nBack\n")
        
        
    '''else:
        
        bytecount = 0
        data = []
        while(bytecount < numbytes):
            data.append(int(input("\nEnter byte" + str(bytecount) + ":\n"),16))
            bytecount = bytecount + 1
            
        spi.open(0,1)
        spi.mode = mode
        spi.max_speed_hz = 100000
        spi.lsbfirst = lsbfirst
        regs4 =spi.xfer2(data) #Read ll 16 registers starting with "ID"
        print("\nData Out:\n")
        print(data)
        print("\nData In:\n")
        print(regs4)
        spi.close()'''
