
try:
    from logger import logger
    foundLogger = True
except ImportError:
    import logging
    logging.basicConfig(
            format='%(asctime)s %(levelname)s: %(message)s',
            level=logging.INFO)
    foundLogger = False



class CustomLogger:

    def __init__(self, logFilePath = None):
        self.logger = logger.Logger()

    def log(self, *args):
        for msg in args:
            self.logger.message(msg)

    def logSectionStart(self, msg):
        self.logger.sectionStart(msg)

    def logSectionEnd(self):
        self.logger.sectionEnd()


class StandardLogger:

    def __init__(self, logFilePath = None):
        self.logFilePath = logFilePath
        self.logger = logging.getLogger(__package__)

    def log(self, *args):
        self.logger.info(*args)

    def logSectionStart(self, msg):
        pass

    def logSectionEnd(self):
        pass

if foundLogger:
    ActionLogger = CustomLogger
else:
    ActionLogger = StandardLogger
