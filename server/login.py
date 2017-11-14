import json
import falcon


class Login(object):

    def on_get(self, req, resp):
        resp.body = '{"message": "OK"}'
        resp.status = falcon.HTTP_200