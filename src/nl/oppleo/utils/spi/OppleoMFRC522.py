from mfrc522 import MFRC522
#import RPi.GPIO as GPIO
import spidev
import signal
import time
import logging

"""
    Small improvements on the MFRC522 class in https://github.com/pimylifeup/MFRC522-python/blob/master/mfrc522/MFRC522.py
    - add SimpleFRMC522 read function with yield
    - detect frozen SPI and reset
    - add init params not available through SimpleFRMC522
    - GPIO.cleanup for the reset pin only
    - improved range (48dB) fix as option (comments on github)


    TODO
    - GPIO via modulePresence/init call
    - Don't set GPIO mode

"""

class OppleoMFRC522(MFRC522):
    logger = None
    SPI_BUS = 0
    SPI_DEVICE = 0
    SPI_SPEED = 1000000
    GPIO = None

    """
    if pin_mode == 11:
        pin_rst = 15
    else:
        pin_rst = 22
    """
    SPI_RST_DEFAULT_BCM = 15
    SPI_RST_DEFAULT_BOARD = 22
    SPI_RST = 22        # SPI Reset Pin

    def __init__(self, bus=-1, 
                       device=-1,
                       speed=-1,
                       GPIO=None,
                       pin_rst=-1
                       ):
        self.logger = logging.getLogger('nl.oppleo.utils.spi.OppleoMFRC522')

        self.spi = spidev.SpiDev()
        self.spi.open(bus if bus != -1 else self.SPI_BUS, 
                      device if device != -1 else self.SPI_DEVICE)
        self.spi.max_speed_hz = speed if speed is not -1 else self.SPI_SPEED

        self.GPIO = GPIO
        
        if pin_rst != -1:
            self.SPI_RST = pin_rst
        else:
            if GPIO.getmode() == GPIO.BCM:
                self.SPI_RST = self.SPI_RST_DEFAULT_BCM
            else:
                self.SPI_RST = self.SPI_RST_DEFAULT_BOARD
            
        GPIO.setup(self.SPI_RST, GPIO.OUT)
        GPIO.output(self.SPI_RST, 1)
        self.MFRC522_Init(boostAntenna=True)


    def read(self):
        id, text = self.read_no_block()
        while not id:
            id, text = self.read_no_block()
            # yield
            time.sleep(1)
        return id, text


    def read_no_block(self):
        self.logger.debug('read_no_block()')
        (status, TagType) = self.MFRC522_Request(self.PICC_REQIDL)
        self.logger.debug('read_no_block() - status={}, TagType={}'.format(status, TagType))
        if status != self.MI_OK:
            # No card read, return id=None, text=None
            self.logger.debug('read_no_block() - return None, None [1]')
            return None, None
        self.logger.debug('read_no_block() - MFRC522_Anticoll()')
        (status, uid) = self.MFRC522_Anticoll()
        self.logger.debug('read_no_block() - status={}, uid={}'.format(status, uid))
        if status != self.MI_OK:
            self.logger.debug('read_no_block() - return None, None [2]')
            return None, None
        id = self.uid_to_num(uid)
        self.logger.debug('read_no_block() - id={}'.format(id))
        self.logger.debug('read_no_block() - MFRC522_SelectTag()')
        self.MFRC522_SelectTag(uid)
        self.logger.debug('read_no_block() - MFRC522_Auth({}, {}, {}, {})'.format(self.PICC_AUTHENT1A, 11, self.KEY, uid))
        status = self.MFRC522_Auth(self.PICC_AUTHENT1A, 11, self.KEY, uid)
        self.logger.debug('read_no_block() - status={}'.format(status))
        data = []
        text_read = ''
        if status == self.MI_OK:
            for block_num in self.BLOCK_ADDRS:
                block = self.MFRC522_Read(block_num) 
                if block:
                        data += block
            if data:
                text_read = ''.join(chr(i) for i in data)
        self.logger.debug('read_no_block() - text_read={}'.format(text_read))
        self.logger.debug('read_no_block() - MFRC522_StopCrypto1()')
        self.MFRC522_StopCrypto1()
        self.logger.debug('read_no_block() - return id={} text_read={}'.format(id, text_read))
        return id, text_read


    def MFRC522_Auth(self, authMode, BlockAddr, Sectorkey, serNum):
        buff = []

        # First byte should be the authMode (A or B)
        buff.append(authMode)

        # Second byte is the trailerBlock (usually 7)
        buff.append(BlockAddr)

        # Now we need to append the authKey which usually is 6 bytes of 0xFF
        for i in range(len(Sectorkey)):
            buff.append(Sectorkey[i])

        # Next we append the first 4 bytes of the UID
        for i in range(4):
            buff.append(serNum[i])

        # Now we start the authentication itself
        (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_AUTHENT, buff)

        # Check if an error occurred
        if not (status == self.MI_OK):
            self.logger.error("AUTH ERROR!!")
        if not (self.Read_MFRC522(self.Status2Reg) & 0x08) != 0:
            self.logger.error("AUTH ERROR(status2reg & 0x08) != 0")

        # Return the status
        return status


    def MFRC522_Request(self, reqMode):
        status = None
        backBits = None
        TagType = []

        self.logger.debug('MFRC522_Request() - Write_MFRC522()')
        self.Write_MFRC522(self.BitFramingReg, 0x07)

        TagType.append(reqMode)
        self.logger.debug('MFRC522_Request() - MFRC522_ToCard({}, {})'.format(self.PCD_TRANSCEIVE, TagType))
        (status, backData, backBits) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, TagType)
        self.logger.debug('MFRC522_Request() - status={}, backData={}, backBits={} (MI_OK={} MI_ERR={})'.format(status, backData, backBits, self.MI_OK, self.MI_ERR))

        if ((status != self.MI_OK) | (backBits != 0x10)):
            self.logger.debug('MFRC522_Request() - status=MI_ERR')
            status = self.MI_ERR

        return (status, backBits)


    def Close_MFRC522(self):
        self.spi.close()
        self.GPIO.cleanup(self.SPI_RST)


    def MFRC522_Init(self, boostAntenna=False):
        self.MFRC522_Reset()

        self.Write_MFRC522(self.TModeReg, 0x8D)
        self.Write_MFRC522(self.TPrescalerReg, 0x3E)
        self.Write_MFRC522(self.TReloadRegL, 30)
        self.Write_MFRC522(self.TReloadRegH, 0)

        self.Write_MFRC522(self.TxAutoReg, 0x40)
        self.Write_MFRC522(self.ModeReg, 0x3D)

        # Improve range - comment Tremayne Sargeant (2.5cm -> 5.5cm) by set RFCfgReg to 48db gain
        if boostAntenna:
            self.Write_MFRC522(self.RFCfgReg, 0x06<<4)

        self.AntennaOn()