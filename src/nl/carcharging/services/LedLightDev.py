import logging
import threading


class LedLightDev(object):
    logger = logging.getLogger('nl.carcharging.services.LedLighter')
    running = False

    def __init__(self, color):
        self.color = color

    def _fakePulse(self):
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            self.logger.debug('fake pulsing %d' % self.color)

    def pulse(self):
        self.t = threading.Thread(target=self._fakePulse)
        self.t.start()
        self.logger.debug('Fake pulse started in thread')

    def stop(self):
        self.t.do_run = False
        self.t.join()
        self.logger.debug('Fake pulse stopped')
