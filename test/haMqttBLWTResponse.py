import time

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.services.HomeAssistantMqttHandlerThread import HomeAssistantMqttHandlerThread

oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()
oppleoSystemConfig.chargerID = oppleoConfig.chargerID

oppleoSystemConfig.logLevel = "debug"

homeAssistantMqttHandlerThread = HomeAssistantMqttHandlerThread()

# Loop the thread
homeAssistantMqttHandlerThread.start()

homeAssistantMqttHandlerThread.triggerMostRecent()

time.sleep(5)

print("Waiting for HomeAssistantMqttHandlerThread")
print(" (press CTRL+C to stop)")
while homeAssistantMqttHandlerThread.is_alive():
    try:
        while homeAssistantMqttHandlerThread.is_alive():
            # time.sleep(0.05)
            text = input("Enter d/D to (re-)send discovery, s/S to (re-)send status messages:  ")
            text = text.upper().strip()
            if text == 'D':
                print(" Requesting resend auto discovery messages... ")
                homeAssistantMqttHandlerThread.triggerAutoDiscover()
                time.sleep(5)
            elif text == 'S':
                print(" Requesting resend most recent status... ")
                homeAssistantMqttHandlerThread.triggerMostRecent()
                time.sleep(5)
            else:
                print(" Not quite sure what was entered... ")
    except KeyboardInterrupt as kbi:
        # Returning the cursor to home and dont create a new line
        print("\rStopping HomeAssistantMqttHandlerThread...")
        homeAssistantMqttHandlerThread.stop()

print("Done")
