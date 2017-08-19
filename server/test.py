import json
import falcon


class Resource(object):

    def on_get(self, req, resp):
        doc = {
            'hello': [
                {
                    'data': 'world'
                }
            ]
        }

        resp.body = json.dumps(doc, ensure_ascii=False)
        resp.status = falcon.HTTP_200