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

PIN_MOSI = 19
PIN_MISO = 21
PIN_SCLK = 23
PIN_CS0  = 24
PIN_CS1  = 26

#GPIO.cleanup()

SPI_list = [PIN_MOSI,PIN_MISO,PIN_SCLK,PIN_CS0,PIN_CS1]

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(True)
GPIO.setup(SPI_list, GPIO.OUT, initial=GPIO.HIGH)

input('Initial SPI pin values should be HIGH. Type something and hit "enter" to set SPI pins LOW\n')

GPIO.output(SPI_list, GPIO.LOW)

input('SPI pin values should be low. Press "enter" to end')

spi = spidev.SpiDev()


