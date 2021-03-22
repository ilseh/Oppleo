import logging
from nl.oppleo.config.Logger import init_log
from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.utils.ModulePresence import modulePresence
from nl.oppleo.utils.spi.OppleoMFRC522 import OppleoMFRC522

oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()

print("RFID Tag Reader")

oppleoMFRC522 = OppleoMFRC522()
init_log('RFIDTagReader', './RFIDTagReader.log', daemons=None, loglevel=logging.DEBUG, maxBytes=524288, backupCount=5):
oppleoMFRC522.logger.setLevel(logging.DEBUG)

run = True
while run:

    try:
        id, text = oppleoMFRC522.read()
        print(" ID:{} Text:{}".format(id, text))
        
    except KeyboardInterrupt as kbi:
        # CTRL-C
        print("Stopping...")
        run = False


print("Stopping RFID Tag Reader...")

print("Done.")

