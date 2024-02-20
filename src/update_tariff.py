

# TODO
# - optional energy_device_id
# - write accounting log file [tariff_update_date_charger.log]

import os
from datetime import datetime

from nl.oppleo.config.OppleoSystemConfig import oppleoSystemConfig
from nl.oppleo.config.OppleoConfig import oppleoConfig
from nl.oppleo.models.ChargeSessionModel import ChargeSessionModel
from nl.oppleo.models.ChargerConfigModel import ChargerConfigModel
from nl.oppleo.models.RfidModel import RfidModel

timeStr = datetime.now().strftime("%d-%m-%Y_%H:%M.%S")
auditLogFilename = os.path.dirname(oppleoSystemConfig.logFile) + os.sep + "tariff_update_" + timeStr + ".log"
auditLogFile = open(auditLogFilename, "a") 

print("Oppleo Tariff update utility")
auditLogFile.write("Oppleo Tariff update utility - {}\n".format(timeStr))

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def RepresentsFloat(s):
    try: 
        float(s)
        return True
    except ValueError:
        return False

retry = True
newTariff = oppleoConfig.chargerTariff
fromChargeSessionId = None
lastChargeSessionId = None
rfid = None
energy_device_id = oppleoConfig.energyDevice
while retry:
    try:

        print(" The current tariff is €{:.2f}".format(oppleoConfig.chargerTariff))
        if newTariff == oppleoConfig.chargerTariff:
            newTariff = input(" new Tariff [empty to apply €{:.2f}]: €".format(oppleoConfig.chargerTariff))
        if newTariff == '':
            print(" not changing Charger Tariff, keeping €{:.2f} as general tariff.".format(oppleoConfig.chargerTariff))
            newTariff = oppleoConfig.chargerTariff
        # Float/ Integer?
        if not (isinstance(newTariff, float) or RepresentsFloat(newTariff)):
            print(" please provide a numeric valuen (float).")
            newTariff = oppleoConfig.chargerTariff
            continue
        newTariff = float(newTariff)
        # For now only accepting 2 decimals
        if round(newTariff, 2) != newTariff:
            print(" please provide a maximum of 2 decimals.")
            newTariff = oppleoConfig.chargerTariff
            continue

        if oppleoConfig.chargerTariff != newTariff:
            approvalCT = input("Update charger tariff from €{:.2f} to €{:.2f} now? [Y/N]: ".format(oppleoConfig.chargerTariff, newTariff)) 
            if approvalCT in ["Y", "y"]:
                print(" updating Charger Tariff from €{:.2f} to €{:.2f}...".format(oppleoConfig.chargerTariff, newTariff))
                oppleoConfig.chargerTariff = newTariff
                auditLogFile.write("{} Charger Tariff changed from €{:.2f} to €{:.2f}.\n".format(
                        datetime.now().strftime("%d-%m-%Y %H:%M.%S"),
                        oppleoConfig.chargerTariff, 
                        newTariff
                        )
                    )
            else: 
                print(" not updating Charger Tariff to €{:.2f}, keeping €{:.2f} as general tariff.".format(newTariff, oppleoConfig.chargerTariff))


        if fromChargeSessionId is None:
            fromChargeSessionId = input("Starting Charge Session ID: ")

        # Integer?
        if not (isinstance(fromChargeSessionId, int) or RepresentsInt(fromChargeSessionId)):
            print(" please provide an integer.")
            fromChargeSessionId = None
            continue

        if lastChargeSessionId is None:
            lastChargeSessionId = input("Last Charge Session ID: [empty to select to most recent] ")

        # Empty?
        if lastChargeSessionId == '':
            print(" untill most recent session selected.")
            lastChargeSessionId = None
        else:
            # Integer?
            if not (isinstance(lastChargeSessionId, int) or RepresentsInt(lastChargeSessionId)):
                print(" please provide an integer.")
                lastChargeSessionId = None
                continue


        print("Provide the RFID: [empty for all RFIDs]")
        print(" RFID value options include:")
        knownRfids = RfidModel.get_all()
        for knownRfid in knownRfids:
            chargeSessionsForRFID = ChargeSessionModel.get_sessions_from_id_to_id(
                                        startId=fromChargeSessionId,
                                        toId=lastChargeSessionId,
                                        rfid=knownRfid.rfid, 
                                        energy_device_id=energy_device_id
                                    )

            print(' RFID {} ({}with {} charge sessions in selection)'.format(
                    knownRfid.rfid, 
                    "\"{}\" ".format(knownRfid.name) if knownRfid.name is not None else "", 
                    chargeSessionsForRFID.count()
                    )
                )

        if rfid is None:
            rfid = input(" Provide the RFID: ")
        if len(rfid.strip()) == 0:
            print(" all RFIDs selected.")
            rfid = None

        selectedChargeSessions = ChargeSessionModel.get_sessions_from_id_to_id(
                                    startId=fromChargeSessionId,
                                    toId=lastChargeSessionId,
                                    rfid=rfid, 
                                    energy_device_id=energy_device_id
                                )

        sessionCount = selectedChargeSessions.count()
        # total = sum(selectedChargeSession.total_price for selectedChargeSession in selectedChargeSessions)
        tVal = sum(map(lambda selectedChargeSession: selectedChargeSession.total_price, selectedChargeSessions))

        totalTariffs = {selectedChargeSession.tariff: selectedChargeSession.tariff for selectedChargeSession in selectedChargeSessions}.values()
        totalRFIDs = {selectedChargeSession.rfid: selectedChargeSession.rfid for selectedChargeSession in selectedChargeSessions}.values()
        ts = str(totalRFIDs)

        if sessionCount == 0:
            print(" no sessions selected.") 
            retry = False
            continue


        print("Selecting {} charge sessions with {} tariff{} from {} RFID{} ({}) for a total of €{:.2f} to update.".format(sessionCount, 
                                                                                                                           len(totalTariffs), 
                                                                                                                           "" if len(totalTariffs) == 1 else "s", 
                                                                                                                           len(totalRFIDs), "" if len(totalRFIDs) == 1 else "s",
                                                                                                                           ", ".join(totalRFIDs),
                                                                                                                           tVal)
                )
        approval = input(" continue? [Y/N]: ") 

        if approval in ["Y", "y"]:
            cnt = 0
            updatedCnt = 0
            valueChange = 0
            print(" updating {} charge sessions...".format(sessionCount))
            for selectedChargeSession in selectedChargeSessions:
                cnt += 1
                if selectedChargeSession.tariff == newTariff:
                    print("\r updating {} charge sessions... {:4} not updating (id={}), tariff unchanged (€{:.2f})".format(
                            sessionCount,
                            cnt, 
                            selectedChargeSession.id,
                            selectedChargeSession.tariff
                            )
                        )
                else:
                    old_tariff = selectedChargeSession.tariff
                    old_price = selectedChargeSession.total_price
                    selectedChargeSession.tariff = newTariff
                    selectedChargeSession.total_price = round(selectedChargeSession.total_energy * selectedChargeSession.tariff, 2)
                    valueChange += (selectedChargeSession.total_price - old_price)
                    print("\r updating {} charge sessions... {:4} (id={:5}, {:4.1f}kWh), original tariff €{:3.2f}, new tariff €{:1.2f}. Price from €{:5.2f} to €{:5.2f}".format(
                            sessionCount, 
                            cnt, 
                            selectedChargeSession.id,
                            selectedChargeSession.total_energy,
                            old_tariff,
                            newTariff,
                            old_price,
                            selectedChargeSession.total_price
                            )
                        )
                    selectedChargeSession.save()
                    auditLogFile.write("{} Charge session ID {:5} {:4.1f}kWh - changed tariff from €{:3.2f} to €{:3.2f}, and price from €{:5.2f} to €{:5.2f}.\n".format(
                            datetime.now().strftime("%d-%m-%Y %H:%M.%S"),
                            selectedChargeSession.id,
                            selectedChargeSession.total_energy,
                            oppleoConfig.chargerTariff, 
                            newTariff,
                            old_price,
                            selectedChargeSession.total_price
                            )
                        )

                    updatedCnt += 1
            print("\r --> Summary: updated {} charge sessions (from {} selected), {} the total value by €{:.2f}.".format(
                    updatedCnt, 
                    sessionCount,
                    "reduced" if valueChange < 0 else "increased",
                    valueChange
                    )
                )
        else:
            print("Changes not applied.")

        retry = False


    except KeyboardInterrupt:
        print('\nInterrupted')
        retry = False

auditLogFile.close()
print('Auditlog created ({})'.format(auditLogFilename))

print("Done")
