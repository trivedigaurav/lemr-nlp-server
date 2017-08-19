import falcon
from .test import Resource

api = application = falcon.API()

test = Resource()
api.add_route('/test', test)