import logging

from nl.carcharging.utils.GenericUtil import GenericUtil


class ChargerDev(object):

    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.services.ChargerDev')

        def start(self):
            self.logger.debug("Fake charger started")

        def stop(self):
            self.logger.debug("Fake charger stopped")


class ChargerProd(object):
    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.services.ChargerProd')

    def start(self):
        self.logger.warning("ChargerProd.start not implemented yet!!")

    def stop(self):
        self.logger.warning("ChargerProd.stop not implemented yet!!")


class Charger(object):
    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.services.Charger')

        if GenericUtil.isProd():
            self.logger.debug("Using production charger")
            self.charger = ChargerProd()
        else:
            self.logger.debug("Using fake charger")
            self.charger = ChargerDev()

    def start(self):
        self.charger.start()

    def stop(self):
        self.charger.stop()
