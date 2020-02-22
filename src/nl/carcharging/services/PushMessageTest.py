from nl.carcharging.services.PushMessage import PushMessage
from nl.carcharging.config.WebAppConfig import WebAppConfig

if WebAppConfig.ini_settings is None:
    WebAppConfig.loadConfig()

PushMessage.sendMessage("Test title", "Test message of some more words", PushMessage.priorityEmergency)