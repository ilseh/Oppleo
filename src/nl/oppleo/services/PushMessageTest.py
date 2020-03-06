from nl.oppleo.services.PushMessage import PushMessage
from nl.oppleo.config.OppleoConfig import OppleoConfig

if OppleoConfig.ini_settings is None:
    OppleoConfig.loadConfig()

PushMessage.sendMessage("Test title", "Test message of some more words", PushMessage.priorityEmergency)