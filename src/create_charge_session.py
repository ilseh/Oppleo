


#from nl.oppleo.config.OppleoSystemConfig import oppleoSystemConfig
from nl.oppleo.config.OppleoConfig import oppleoConfig
from nl.oppleo.models.ChargeSessionModel import ChargeSessionModel
from nl.oppleo.models.ChargerConfigModel import ChargerConfigModel
from nl.oppleo.models.RfidModel import RfidModel

print("Oppleo Charge Session utility")
print(" Creates a charge session with th eprovided ID.")

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

retry = True
newChargeSessionId = None
rfid = None
while retry:
    try:
        if newChargeSessionId is None:
            newChargeSessionId = input("Provide the Charge Session ID: ")

        # Integer?
        if not (isinstance(newChargeSessionId, int) or RepresentsInt(newChargeSessionId)):
            print(" please provide an integer.")
            newChargeSessionId = None
            continue

        existingChargeSession = ChargeSessionModel.get_one_charge_session(newChargeSessionId)
        if existingChargeSession is not None:
            print(" please provide an non existing ID.")
            print(" Charge Session {}: {}".format(newChargeSessionId, existingChargeSession.to_str()))
            newChargeSessionId = None
            continue

        print("Provide the RFID: ")
        print(" RFID value options include:")
        knownRfids = RfidModel.get_all()
        for knownRfid in knownRfids:
            print(' RFID {} is "{}"'.format(knownRfid.rfid, knownRfid.name))

        if rfid is None:
            rfid = input(" Provide the RFID: ")
        if len(rfid.strip()) == 0:
            print(" please provide an RFID value (no empty string)")
            rfid = None
            continue

        data_for_session = {
            "id"                : newChargeSessionId,
            "rfid"              : rfid, 
            "energy_device_id"  : oppleoConfig.chargerID,
            "start_value"       : 0,
            "tariff"            : ChargerConfigModel.get_config().charger_tariff,
            "end_value"         : 0,
            "total_energy"      : 0,
            "total_price"       : 0,
            "trigger"           : ChargeSessionModel.TRIGGER_WEB
            }
        charge_session = ChargeSessionModel()
        charge_session.set(data_for_session)
        charge_session.save()

        retry = False
        print("Done")


    except KeyboardInterrupt:
        print('\nInterrupted')
        retry = False
        exit(0)

