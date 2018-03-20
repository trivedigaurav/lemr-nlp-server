import falcon
from .logger import logEvent

class PutLogEvent(object):
    def on_put(self, req, resp, event_name):
        message = req.stream.read()
        logEvent(event_name, message)    
        resp.status = falcon.HTTP_200
