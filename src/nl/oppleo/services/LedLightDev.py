import logging
import threading


class LedLightDev(object):
    logger = logging.getLogger('nl.oppleo.services.LedLighter')
    running = False

    def __init__(self, color, intensity):
        self.color = color
        self.intensity = intensity

    def _fakePulse(self):
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            self.logger.debug('fake pulsing %d' % self.color)

    def on(self):
        self.logger.debug('fake light on %d intensity %d' % (self.color, self.intensity))

    def off(self):
        self.logger.debug('fake light off %d %d' % (self.color, self.intensity))

    def cleanup(self):
        self.logger.debug('fake cleanup')

    def pulse(self):
        self.t = threading.Thread(target=self._fakePulse, name="LedPulseThread")
        self.t.start()
        self.logger.debug('Fake pulse started in thread')

    def pulse_stop(self):
        self.t.do_run = False
        self.t.join()
        self.logger.debug('Fake pulse stopped')
