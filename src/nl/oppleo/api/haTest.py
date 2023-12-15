import json
import time

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.services.HomeAssistantMqttHandlerThread import HomeAssistantMqttHandlerThread

"""
    Home Assistant MQTT Test


"""


oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()
oppleoSystemConfig.chargerID = oppleoConfig.chargerID

# object_id =  The ID of the device (chargedID, [a-zA-Z0-9_-] alphanumerics, underscore and hyphen)
object_id = oppleoSystemConfig.chargerID


if oppleoSystemConfig.homeAssistantMqttClientId != None and oppleoSystemConfig.homeAssistantMqttClientId != '':
    __client_id = oppleoSystemConfig.homeAssistantMqttClientId
else:
    __client_id = 'Oppleo_' + oppleoSystemConfig.chargerID

"""
    (re-)Send the HomeAssistant Discovery messages
"""

from nl.oppleo.models.RfidModel import RfidModel

defrfidCards = RfidModel.get_all()

rfidCards = list(map(lambda rfid: rfid.name if rfid.name != None and rfid.name != "" else rfid.rfid, RfidModel.get_all()))


key1 = "Testpas A"
key1 = "AAAAAAAA"

rfidCards = RfidModel.get_all()
selectedRfid = None

# Find by name
selectedRfid = next((rfid for rfid in list(filter(lambda rfid: rfid.name == key1, rfidCards)) if rfid), None)
if selectedRfid is None:
    # Find by ID
    selectedRfid = next((rfid for rfid in list(filter(lambda rfid: rfid.rfid == key1, rfidCards)) if rfid), None)


homeAssistantMqttHandlerThread = HomeAssistantMqttHandlerThread()

# Loop the thread
homeAssistantMqttHandlerThread.start()

# homeAssistantMqttClient.publishEnergyDevice(A1=15.7, A2=14.9, A3=14.8, V1=233, V2=234, V3=234, E1=123.4, E2=234.5, E3=345.6, ET=1111.1, P1=11, P2=12, P3=13, Frequency=50.0)

meteringValues = {
    'A1': 12.1,
    'A2': 12.2,
    'A3': 12.3,
    'V1': 221.1,
    'V2': 222.1,
    'V3': 223.1,
    'E1': 21.1,
    'E2': 22.1,
    'E3': 23.1,
    'ET': 25.1,
    'P1': 11.1,
    'P2': 12.1,
    'P3': 13.1,
    'Frequency': 49.9
}

sessionValues1 = {
    'Status': "Waiting",
    'Energy': 12.7,
    'Cost': 12.99,
    'Token': "Testpas",
    'EVSE': "Blocked",
    'Daluren': False,
    'Charging': False,
    'Vehicle': "Sleeping"
}
sessionValues2 = {
    'Status': "Waiting",
    'Energy': 99.7,
    'Cost': 9.99,
    'Token': "AAAAAAAA",
    'EVSE': "Blocked",
    'Daluren': True,
    'Charging': False,
    'Vehicle': "Sleeping"
}
sessionValues3 = {
    'Status': "Waiting",
    'Energy': 22.7,
    'Cost': 2.99,
    'Token': "Testpas A",
    'EVSE': "Blocked",
    'Daluren': True,
    'Charging': False,
    'Vehicle': "Sleeping"
}
#homeAssistantMqttHandlerThread.publish(values=values)

card1 = {
    'Token': "Testpas"
}
card2 = {
    'Token': "AAAAAAAA"
}
card3 = {
    'Token': "Testpas A"
}

from pynput.keyboard import Key, Listener
def on_press(key):
    print('{0} pressed'.format(
        key))

def on_release(key):
    print('{0} release'.format(key))
    if key == Key.esc:
        # Stop listener
        homeAssistantMqttHandlerThread.stop()
        return False
    if hasattr(key, 'char') and key.char == '1':
        # 
        homeAssistantMqttHandlerThread.publish(values=card1)
    if hasattr(key, 'char') and key.char == '2':
        # 
        homeAssistantMqttHandlerThread.publish(values=card2)
    if hasattr(key, 'char') and key.char == '3':
        # 
        homeAssistantMqttHandlerThread.publish(values=card3)
    if hasattr(key, 'char') and key.char in ['d', 'D']:
        # 
        homeAssistantMqttHandlerThread.__triggerAutoDiscover = True
    if hasattr(key, 'char') and key.char in ['s', 'S']:
        # Stop listener
        homeAssistantMqttHandlerThread.publish(values=sessionValues1)
    if hasattr(key, 'char') and key.char in ['m', 'M']:
        # Stop listener
        homeAssistantMqttHandlerThread.publish(values=meteringValues)

# Collect events until released
with Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()


while homeAssistantMqttHandlerThread.is_alive():

    time.sleep(0.75)




print("Done!") 