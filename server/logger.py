# https://stackoverflow.com/a/41677596/1491900
import logging
import logging.handlers
import os
from datetime import datetime
import sys
import falcon

# Logging Levels
# https://docs.python.org/3/library/logging.html#logging-levels
# CRITICAL  50
# ERROR 40
# WARNING   30
# INFO  20
# DEBUG 10
# NOTSET    0


def set_up_logging():
    file_path = sys.modules[__name__].__file__
    project_path = os.path.dirname(os.path.dirname(file_path))
    log_location = project_path + '/logs/'
    if not os.path.exists(log_location):
        os.makedirs(log_location)

    current_time = datetime.now()
    current_date = current_time.strftime("%Y-%m-%d")
    file_name = current_date + '.log'
    file_location = log_location + file_name
    with open(file_location, 'a+'):
        pass

    logger = logging.getLogger(__name__)
    format = '[%(asctime)s] [%(levelname)s] [%(message)s]'
    # To store in file
    logging.basicConfig(format=format, filemode='a+', filename=file_location, level=logging.DEBUG)
    # To print only
    # logging.basicConfig(format=format, level=logging.DEBUG)
    return logger

def logEvent(event, message):
    logger = set_up_logging()
    logger.info(event + ":\t"+ message)

class PutLogEvent(object):
    def on_put(self, req, resp, event_name):
        message = req.stream.read()
        logEvent(event_name, message)    
        resp.status = falcon.HTTP_200



