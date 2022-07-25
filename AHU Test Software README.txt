Please use AHU Test Software Alt for testing

++Initially, the program will read all of the ADC registers and print their value (I forgot to make the current version print this in Hex, so unfortunately it is in decimal for now)

++The program will prompt you with the following text:

"
What would you like to do?
'cmd' --> Send ADC Command
'rdata' --> Read ADC Data
'rrega' --> Read all registers
'bytes' --> set number of bytes of data to read.
'spimode' --> spi mode (0,1,2 or 3)
'clk' --> set clockrate
'back' --> return to last page

Enter command:
"

++'cmd' gives you the following prompt:

    "Enter command name ("WAKEUP": 0x02, "STANDBY": 0x04,"RESET": 0x06,"START": 0x08,"STOP": 0x0A,"OFFSETCAL": 0x1A,"RDATAC": 0x10,"SDATAC": 0x11,"RDATA": 0x12,"RREG": 0x20,"WREG": 0x40)"

    --Enter the text, not the hexadecimal number here. The hex numbers are just for reference. Be sure to follow the same capitalization as the instruction.

++'rdata' will send an 'rdata' command to the ADC in addition to a number of 0x00 bytes equal to the number of bytes configured by the bytes command (default 1 byte).
   That number of bytes will be read by the ADC and printed in the terminal.

++'rrega' will read the value of all ADC registers, as it did during the program startup

++'bytes' will then prompt you to set the number of bytes you want to read from the ADC

++'spimode' will then prompt you to enter the value of the SPImode (1,2,3 or 4)
   You should use 1 (default) for the ADC, as this is the mode for which it is configured.

++'back' ignore this since there is no longer a previous page to view

