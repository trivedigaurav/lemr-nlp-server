import json
import falcon

class Login(object):

    #There is no logic to check login here
    #Relying on server configurations for this
    def on_get(self, req, resp):
        resp.body = '{"message": "OK"}'
        resp.status = falcon.HTTP_200