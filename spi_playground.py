import RPi.GPIO as GPIO
import spidev

ESC = False
numbytes = 1
data = []
mode = 1
lsbfirst = False

spi = spidev.SpiDev()

while(not ESC):

    inp = input('\nHit any key and "enter" to input bytes you want to write to the SPI bus or type "op" for more options\n')
    #print(hex(inp))
    
    if inp == 'op':
        print("\n 'bytes' --> number of bytes to write.\n 'spimode' --> spi mode (0,1,2 or 3)\n 'lsb' --> set to LSB\n 'msb' --> set to MSB\n 'back' --> return to last page\n")
        op = input("\nEnter command:\n")
        if op == 'bytes':
            numbytes = int(input("\nEnter the bumber of bytes you want to send:\n"))
        if op == 'spimode':
            mode = int(input("\nEnter mode(0,1,2 or 3):\n"))
        if op == 'lsb':
            lsbfirst = True
        if op == 'msb':
            lsbfirst = False
        if op == 'back':
            print("\nBack\n")
    else:
        
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
        spi.close()

