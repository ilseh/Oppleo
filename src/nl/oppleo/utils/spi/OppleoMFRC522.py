from datetime import datetime
import threading
from mfrc522 import MFRC522
#import RPi.GPIO as GPIO
import spidev
import signal
import time
import logging

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig

oppleoSystemConfig = OppleoSystemConfig()

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

    MFRC522 Data sheet, including register description
    https://www.nxp.com/docs/en/data-sheet/MFRC522.pdf


        self.Read_MFRC522(self.Status2Reg) & 0x08) != 0
    Bit 3 on Status2Reg register indicates MFCrypto1On (encryption on). Card data cannot be read without AUTH, the
    id however can be read. Oppleo does not use data one the MiFare cards, only the ID itself.

    According thedocumentation (Fig. 4 of https://www.nxp.com/docs/en/application-note/AN10834.pdf) the Mifare
    card needs to be selected before interaction can take place. As Oppleo isn't interacting with the cards,

    https://diy.waziup.io/assets/src/sketch/libraries/MFRC522/doc/rfidmifare.pdf
    The MIFARE Classic 1K offers 1024 bytes of data storage, split into 16 sectors; each sector is protected by 
    two different keys, called A and B. Each key can be programmed to allow operations such as reading, writing, 
    increasing valueblocks, etc. MIFARE Classic 4K offers 4096 bytes split into forty sectors, of which 32 are 
    same size as in the 1K with eight more that are quadruple size sectors. MIFARE Classic mini offers 320 bytes
    split into five sectors.


    !!! If GPIO Pins which are also SPI Pins (GPIO8,9,10,11) are cleaned using GPIO.cleanup() the SPI connection
        fails until Raspberry Pi restart!

"""

class OppleoMFRC522Log():
    threadLock = threading.Lock()

    last_read_call = None
    read_call_count = 0

    last_read_no_block_call = None
    read_no_block_call_count = 0

    last_detected_rfid = None
    detected_rfid_count = 0

    last_detected_nothing = None
    detected_nothing_count = 0

    last_detected_collission = None
    detected_collision_count = 0


    def logRead(self):
        with self.threadLock:
            self.last_read_call = str(datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
            self.read_call_count += 1

    def logReadNoBlock(self):
        with self.threadLock:
            self.last_read_no_block_call = str(datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
            self.read_no_block_call_count += 1


    def logDetectedRfid(self):
        with self.threadLock:
            self.last_detected_rfid = str(datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
            self.detected_rfid_count += 1

    def logDetectedNothing(self):
        with self.threadLock:
            self.last_detected_nothing = str(datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
            self.detected_nothing_count += 1

    def logDetectCollission(self):
        with self.threadLock:
            self.last_detected_collission = str(datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
            self.detected_collision_count += 1

    def to_str(self):
        with self.threadLock:
            return { 'read'              : { 'last': self.last_read_call, 'cnt': self.read_call_count },
                     'read_no_block'     : { 'last': self.last_read_no_block_call, 'cnt': self.read_no_block_call_count },
                     'detected_rfid'     : { 'last': self.last_detected_rfid, 'cnt': self.detected_rfid_count },
                     'detected_nothing'  : { 'last': self.last_detected_nothing, 'cnt': self.detected_nothing_count },
                     'detected_collision': { 'last': self.last_detected_collission, 'cnt': self.detected_collision_count }
            }

class OppleoMFRC522(MFRC522):
    __logger = None
    oLog = OppleoMFRC522Log()

    KEY = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
    BLOCK_ADDRS = [8, 9, 10]

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

    antennaBoost = False


    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(level=oppleoSystemConfig.getLogLevelForModule(__name__))   
        # Don't call MFRC522 default init


    def setup(self, bus=-1, 
                    device=-1,
                    speed=-1,
                    GPIO=None,
                    pin_rst=-1,
                    antennaBoost:bool=False
                    ):

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

        self.antennaBoost = antennaBoost
        self.MFRC522_Init(antennaBoost=antennaBoost)


    def read(self, select:bool=True, auth:bool=True):
        self.oLog.logRead()
        id, text = self.read_no_block()
        while not id:
            id, text = self.read_no_block(select=select, auth=auth)
            # yield
            time.sleep(.05)
        return id, text


    def read_no_block(self, select:bool=True, auth:bool=True):
        self.oLog.logReadNoBlock()
        self.__logger.debug('OppleoMFRC522.read_no_block() select={}, auth={}'.format(select, auth))
        (status, tagType) = self.MFRC522_Request(self.PICC_REQIDL)
        # tagType 16 (cc, mtc)
        if status == self.MI_OK:
            self.oLog.logDetectedRfid()
            self.__logger.info('Detected rfid tag (type={})'.format(tagType))
        if status != self.MI_OK:
            # No card read, return id=None, text=None
            self.oLog.logDetectedNothing()
            return None, None
        (status, uid) = self.MFRC522_Anticoll()
        if status != self.MI_OK:
            self.oLog.logDetectCollission()
            self.__logger.info('Collision reading rfid tag, skipping')
            return None, None
        id = self.uid_to_num(uid)
        self.__logger.info('Read rfid tag (id={})'.format(id))
        text_read = ''
        if select:
            self.MFRC522_SelectTag(uid)
            if auth:
                # Selection and Authentication required for reading text
                status = self.MFRC522_Auth(self.PICC_AUTHENT1A, 11, self.KEY, uid)
                data = []
                if status == self.MI_OK:
                    for block_num in self.BLOCK_ADDRS:
                        block = self.MFRC522_Read(block_num) 
                        if block:
                                data += block
                    if data:
                        text_read = ''.join(chr(i) for i in data)
                self.MFRC522_StopCrypto1()
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
        if (not (status == self.MI_OK) or
            not (self.Read_MFRC522(self.Status2Reg) & 0x08) != 0):
                self.__logger.error("Rfid tag authentication failed")

        # Return the status
        return status



    def Close_MFRC522(self):
        self.spi.close()
        self.GPIO.cleanup(self.SPI_RST)


    def MFRC522_Init(self, antennaBoost=False):
        self.MFRC522_Reset()

        self.Write_MFRC522(self.TModeReg, 0x8D)
        self.Write_MFRC522(self.TPrescalerReg, 0x3E)
        self.Write_MFRC522(self.TReloadRegL, 30)
        self.Write_MFRC522(self.TReloadRegH, 0)

        self.Write_MFRC522(self.TxAutoReg, 0x40)
        self.Write_MFRC522(self.ModeReg, 0x3D)

        # Improve range - comment Tremayne Sargeant (2.5cm -> 5.5cm) by set RFCfgReg to 48db gain
        if antennaBoost:
            self.Write_MFRC522(self.RFCfgReg, 0x06<<4)

        self.AntennaOn()


    def uid_to_num(self, uid) -> int:
        n = 0
        for i in range(0, 5):
            n = n * 256 + uid[i]
        return n