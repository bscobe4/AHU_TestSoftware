import RPi.GPIO as GPIO
import spidev

#SPI Addresses
spiaddr_ADS131E08 = 1
spiaddr_KX132 = 1

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

spi = spidev.SpiDev()

GPIO.cleanup()
#check reset pin
#check sdatac command is sent
#Which clock source are we using?
#CS1 s used by both ADC and ACC aparently
#Check data lines.

print("\nTest 1:\n")
spi.open(0,spiaddr_ADS131E08)
spi.mode = 0b01
spi.max_speed_hz = 1000000
spi.writebytes([0x12])
data = spi.readbytes(1)
print(data)
print("\nTest 2:\n")
spi.mode = 0b01
spi.max_speed_hz = 1000000
spi.lsbfirst = False
spi.writebytes([0x12])
data = spi.readbytes(1)
print(data)

print("\nTest 3:\n")
spi.mode = 0b01
spi.max_speed_hz = 1000000
spi.lsbfirst = False
data = spi.xfer2([0x12])
print(data)
spi.close()

print("\nTest 4:\n")
spi.open(0,spiaddr_ADS131E08)
spi.mode = 0b01
spi.max_speed_hz = 1000000
spi.lsbfirst = False
spi.writebytes([0x20, 0x0F]) #Read ll 16 registers starting with "ID"
regs = spi.readbytes(16)
print(regs)
spi.close()

print("\nTest 5:\n")
spi.open(0,spiaddr_ADS131E08)
spi.mode = 0b01
spi.max_speed_hz = 1000000
spi.lsbfirst = False
regs2 =spi.xfer([0x20 , 0x0F]) #Read ll 16 registers starting with "ID"
print(regs2)
spi.close()

print("\nRESET and SDATAC:\n")
spi.open(0,spiaddr_ADS131E08)
spi.mode = 0b01
spi.max_speed_hz = 1000000
spi.lsbfirst = False
spi.writebytes([0x06]) #RDATA
spi.writebytes([0x11]) #SDATAC
spi.close()

print("\nRDATA:\n")
spi.open(0,spiaddr_ADS131E08)
spi.mode = 0b01
spi.max_speed_hz = 1000000
spi.lsbfirst = False
data0 = spi.xfer([0x12])
data1 = spi.xfer2([0x12]) 
print(data0)
print(data1)
spi.close()

print("\nTest 6:\n")
spi.open(0,spiaddr_ADS131E08)
spi.mode = 0b01
spi.max_speed_hz = 1000000
spi.lsbfirst = False
regs3 =spi.xfer([0x20 , 0x0F]) #Read ll 16 registers starting with "ID"
print(regs3)
spi.close()

print("\nTest 7:\n")
spi.open(0,spiaddr_ADS131E08)
spi.mode = 0b01
spi.max_speed_hz = 1000000
spi.lsbfirst = False
regs4 =spi.xfer2([0x20 , 0x0F]) #Read ll 16 registers starting with "ID"
print(regs4)
spi.close()
