from nl.oppleo.daemon.VehicleChargeStatusMonitorThread import VehicleChargeStatusMonitorThread
from nl.oppleo.config.OppleoConfig import OppleoConfig

oppleoConfig = OppleoConfig()
oppleoConfig.connectedClients['ABC'] = {
                                    'sid'   : 'ABC',
                                    'auth'  : True, # Authenticated
                                    'stats' : 'connected'
                                    }

vsmt = VehicleChargeStatusMonitorThread()
vsmt.rfid = '584190412223'

# Speed stuff up a bit
vsmt._VehicleChargeStatusMonitorThread__vehicleMonitorInterval = 3

vsmt.monitor()

